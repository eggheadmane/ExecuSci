"""Read a paper figure: axis labels, tick scales, and curve series.

Uses EasyOCR (CRAFT + CRNN) for text and OpenCV for the plot frame and
coloured traces.  Pixel positions are mapped to data coordinates from the
tick labels so the extracted series can be compared with a model curve.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field, replace
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

import cv2
import numpy as np

_FIGURE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp"}

_CAPTION_RE = re.compile(r"^Fig(?:ure)?\.?\s*(\d+[a-z]?)\.\s*(.+)$", re.IGNORECASE | re.MULTILINE)

_THICKNESS_RE = re.compile(
    r"([\d.]+)\s*(mm|um|µm|μm|nm|m)\b",
    re.IGNORECASE,
)

_UNIT_TAIL_RE = re.compile(
    r"[,(\[]?\s*(MPa|GPa|kPa|Pa|kW/?m[\u00b2\u00b3 2]*K?|mm|µm|μm|nm|s|°C|K|N|m/?s|%|m)\s*[)\]]?\s*$",
    re.IGNORECASE,
)

_NUMBER_RE = re.compile(r"^[+\-−]?\d+(?:[.,]\d+)?$")

_X_ALIASES: List[Tuple[re.Pattern[str], str]] = [
    (re.compile(r"contact\s*pressure", re.I), "P"),
    (re.compile(r"\bpressure\b", re.I), "P"),
    (re.compile(r"sliding\s+distance", re.I), "s"),
    (re.compile(r"\btime\b", re.I), "t"),
    (re.compile(r"\btemperature\b", re.I), "T"),
]

_Y_ALIASES: List[Tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bihtc\b", re.I), "h"),
    (re.compile(r"\b(?:ch)?htc\b", re.I), "h"),
    (re.compile(r"interfacial\s+heat\s+transfer", re.I), "h"),
    (re.compile(r"\bcof\b", re.I), "mu"),
    (re.compile(r"coefficient\s+of\s+friction", re.I), "mu"),
    (re.compile(r"\bfriction\b", re.I), "mu"),
]

_ALIASES: List[Tuple[re.Pattern[str], str]] = _Y_ALIASES + _X_ALIASES

_MODEL_RE = re.compile(r"model|predict", re.I)
_EXPERIMENT_RE = re.compile(r"experiment|measured|test\s+result", re.I)
_DRY_RE = re.compile(r"\bdry\b", re.I)
_LUBE_RE = re.compile(r"lube|lubricat", re.I)
#: EasyOCR often reads the tool steel ``P20`` as ``P2O`` (zero vs letter O).
_OCR_TOOL_FIXES: List[Tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bP2O\b", re.I), "P20"),
    (re.compile(r"\bP2\s*0\b"), "P20"),
    (re.compile(r"\bH1S\b", re.I), "H13"),
]

_LEGEND_SCALE = 2.5
_READER = None


class DigitizeError(ValueError):
    """The figure could not be turned into calibrated (x, y) series."""


@dataclass
class OcrBox:
    text: str
    conf: float
    pts: np.ndarray  # 4x2
    cx: float
    cy: float
    x0: float
    y0: float
    x1: float
    y1: float


@dataclass
class AxisCalib:
    """Linear (or log-linear) map from pixel coordinates to data values."""

    x0: float
    y0: float
    x1: float
    y1: float
    xmin: float
    xmax: float
    ymin: float
    ymax: float
    ax: float
    bx: float
    ay: float
    by: float
    log_x: bool = False
    log_y: bool = False

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0

    def to_data(self, px: float, py: float) -> Tuple[float, float]:
        x = self.ax * float(px) + self.bx
        y = self.ay * float(py) + self.by
        if self.log_x:
            x = 10 ** x
        if self.log_y:
            y = 10 ** y
        return x, y

    def to_pixel(self, x: float, y: float) -> Tuple[int, int]:
        xv = np.log10(x) if self.log_x and x > 0 else x
        yv = np.log10(y) if self.log_y and y > 0 else y
        if abs(self.ax) < 1e-18 or abs(self.ay) < 1e-18:
            raise DigitizeError("Axis calibration is degenerate")
        px = (xv - self.bx) / self.ax
        py = (yv - self.by) / self.ay
        return int(round(px)), int(round(py))

    def polyline_pixels(self, x: Sequence[float], y: Sequence[float]) -> np.ndarray:
        pts = [self.to_pixel(float(a), float(b)) for a, b in zip(x, y)]
        return np.asarray(pts, dtype=np.int32)


@dataclass
class Series:
    name: str
    x: np.ndarray
    y: np.ndarray
    color_bgr: Tuple[int, int, int]
    kind: str = "line"
    is_model: bool = True
    tool: Optional[str] = None
    delta: Optional[float] = None


@dataclass
class DigitizedFigure:
    path: str
    x_label: str
    y_label: str
    x_unit: str
    y_unit: str
    x_symbol: Optional[str]
    y_symbol: Optional[str]
    calib: AxisCalib
    series: List[Series] = field(default_factory=list)
    legend_text: List[str] = field(default_factory=list)
    captions: List[str] = field(default_factory=list)
    image_bgr: Optional[np.ndarray] = field(default=None, repr=False)

    def model_series(self) -> List[Series]:
        models = [s for s in self.series if s.is_model]
        return models or list(self.series)

    def to_meta(self) -> dict:
        return {
            "path": self.path,
            "x_label": self.x_label,
            "y_label": self.y_label,
            "x_unit": self.x_unit,
            "y_unit": self.y_unit,
            "x_symbol": self.x_symbol,
            "y_symbol": self.y_symbol,
            "x_range": [self.calib.xmin, self.calib.xmax],
            "y_range": [self.calib.ymin, self.calib.ymax],
            "log_x": self.calib.log_x,
            "log_y": self.calib.log_y,
            "legend_text": list(self.legend_text),
            "captions": list(self.captions),
            "series": [
                {
                    "name": s.name,
                    "kind": s.kind,
                    "is_model": s.is_model,
                    "tool": s.tool,
                    "delta": s.delta,
                    "n_points": int(len(s.x)),
                    "color_bgr": list(s.color_bgr),
                }
                for s in self.series
            ],
        }


def extract_captions(markdown: str) -> List[str]:
    """Figure captions from Mathpix-style ``Fig. N. ...`` lines."""
    return [match.group(2).strip() for match in _CAPTION_RE.finditer(markdown or "")]


def is_figure_path(path: str) -> bool:
    return os.path.splitext(path)[1].lower() in _FIGURE_EXTS


def digitize_figure(
    path: str,
    symbols: Optional[Mapping[str, dict]] = None,
    captions: Optional[Sequence[str]] = None,
    tools: Optional[Sequence[str]] = None,
) -> DigitizedFigure:
    """Calibrate a plot image and extract its data series."""
    image = cv2.imread(path, cv2.IMREAD_COLOR)
    if image is None:
        raise DigitizeError(f"Could not read figure: {path}")

    ocr = read_text(image)
    frame, x_ticks, y_ticks = choose_plot_frame(find_plot_frames(image), ocr)
    calib = calibrate_axes(frame, x_ticks, y_ticks)

    x_label, y_label = _axis_labels(ocr, frame)
    caption_blob = " ".join(captions or [])
    if not x_label:
        x_label = _label_from_caption(caption_blob, axis="x") or ""
    if not y_label:
        y_label = _label_from_caption(caption_blob, axis="y") or ""

    x_label, x_unit = split_label_unit(x_label)
    y_label, y_unit = split_label_unit(y_label)

    symbol_map = dict(symbols or {})
    x_symbol = match_axis_symbol(f"{x_label} {x_unit}".strip(), symbol_map, role="x")
    y_symbol = match_axis_symbol(f"{y_label} {y_unit}".strip(), symbol_map, role="y")
    if not x_symbol:
        x_symbol = match_axis_symbol(caption_blob, symbol_map, role="x")
    if not y_symbol:
        y_symbol = match_axis_symbol(caption_blob, symbol_map, role="y")

    legend_boxes = _collect_legend_boxes(image, frame, ocr)
    legend_rows = stitch_legend_rows(legend_boxes)
    legend_text = [box.text for box in legend_rows]
    series = extract_series(image, calib, hide_rect=_legend_hide_rect(legend_rows))
    series = _annotate_series(series, legend_rows, image, tools or ())

    return DigitizedFigure(
        path=os.path.abspath(path),
        x_label=x_label,
        y_label=y_label,
        x_unit=x_unit,
        y_unit=y_unit,
        x_symbol=x_symbol,
        y_symbol=y_symbol,
        calib=calib,
        series=series,
        legend_text=legend_text,
        captions=list(captions or []),
        image_bgr=image,
    )


def save_digitized(figure: DigitizedFigure, out_dir: str) -> Dict[str, str]:
    """Write ``digitized.csv`` and ``digitized.json``. Returns written paths."""
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "digitized.csv")
    json_path = os.path.join(out_dir, "digitized.json")
    with open(csv_path, "w", encoding="utf-8") as fh:
        fh.write("series,kind,is_model,x,y\n")
        for series in figure.series:
            for x, y in zip(series.x, series.y):
                fh.write(
                    f"{_csv_escape(series.name)},{series.kind},"
                    f"{int(series.is_model)},{x},{y}\n"
                )
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(figure.to_meta(), fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return {"csv": csv_path, "json": json_path}


def match_axis_symbol(
    text: str,
    symbols: Mapping[str, dict],
    role: Optional[str] = None,
) -> Optional[str]:
    """Map an axis title / caption fragment to a stage-02 symbol name."""
    if not text or not symbols:
        return None
    aliases = _Y_ALIASES if role == "y" else _X_ALIASES if role == "x" else _ALIASES
    for pattern, name in aliases:
        if pattern.search(text) and name in symbols:
            return name
    for name in sorted(symbols, key=len, reverse=True):
        if len(name) <= 1:
            continue
        if re.search(rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])", text):
            return name
    words = set(re.findall(r"[a-z]+", text.lower()))
    words -= {"the", "a", "an", "of", "and", "with", "for", "in", "to", "vs"}
    best_name, best_score = None, 0
    for name, info in symbols.items():
        desc = (info.get("description") or "").lower()
        desc_words = set(re.findall(r"[a-z]+", desc))
        score = len(words & desc_words)
        if score > best_score:
            best_name, best_score = name, score
    return best_name if best_score >= 2 else None


def split_label_unit(text: str) -> Tuple[str, str]:
    raw = (text or "").strip().strip("()[]")
    if not raw:
        return "", ""
    match = _UNIT_TAIL_RE.search(raw)
    if match:
        unit = match.group(1).strip()
        label = raw[: match.start()].strip(" ,;:-")
        return label, unit
    if "," in raw:
        label, unit = raw.rsplit(",", 1)
        return label.strip(), unit.strip()
    return raw, ""


def find_plot_frame(image: np.ndarray) -> Tuple[int, int, int, int]:
    """Return ``(x0, y0, x1, y1)`` of the largest axes rectangle."""
    return find_plot_frames(image)[0]


def find_plot_frames(image: np.ndarray) -> List[Tuple[int, int, int, int]]:
    """Return every likely axes rectangle, largest first.

    Multi-panel figures have several subplot frames, each well below 20% of
    the full image.  Those used to be rejected, leaving a single fallback crop
    that does not line up with any tick labels.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    _, bw = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)
    kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (max(20, w // 12), 1))
    kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(20, h // 12)))
    lines = cv2.bitwise_or(
        cv2.morphologyEx(bw, cv2.MORPH_OPEN, kernel_h),
        cv2.morphologyEx(bw, cv2.MORPH_OPEN, kernel_v),
    )
    contours, _ = cv2.findContours(lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    area_img = float(h * w)
    found: List[Tuple[int, int, int, int]] = []
    for contour in contours:
        x, y, ww, hh = cv2.boundingRect(contour)
        area = ww * hh
        if area < 0.10 * area_img or ww < 0.18 * w or hh < 0.18 * h:
            continue
        if abs(ww / max(hh, 1) - 1) > 4:
            continue
        found.append((x, y, x + ww, y + hh))
    found = _dedupe_frames(found)
    found.sort(key=_frame_area, reverse=True)
    if found:
        return found
    return [(int(0.12 * w), int(0.08 * h), int(0.98 * w), int(0.88 * h))]


def choose_plot_frame(
    frames: Sequence[Tuple[int, int, int, int]],
    ocr: Sequence[OcrBox],
) -> Tuple[Tuple[int, int, int, int], List[Tuple[float, float]], List[Tuple[float, float]]]:
    """Pick the frame whose tick labels actually calibrate (need two per axis)."""
    if not frames:
        raise DigitizeError("No plot frame found")
    ranked: List[
        Tuple[int, Tuple[int, int, int, int], List[Tuple[float, float]], List[Tuple[float, float]]]
    ] = []
    for frame in frames:
        x_ticks, y_ticks = _axis_ticks(ocr, frame)
        ranked.append((len(x_ticks) + len(y_ticks), frame, x_ticks, y_ticks))
    viable = [row for row in ranked if len(row[2]) >= 2 and len(row[3]) >= 2]
    pool = viable or ranked
    pool.sort(key=lambda row: (row[0], _frame_area(row[1])), reverse=True)
    _, frame, x_ticks, y_ticks = pool[0]
    return frame, x_ticks, y_ticks


def read_text(
    image: np.ndarray,
    origin: Tuple[float, float] = (0.0, 0.0),
    scale: float = 1.0,
    width_ths: Optional[float] = None,
) -> List[OcrBox]:
    """OCR ``image`` and return boxes in full-figure coordinates.

    ``origin`` / ``scale`` map a cropped (and optionally upscaled) image back
    onto the original: ``full = origin + crop / scale``.
    """
    reader = _easyocr_reader()
    if image.ndim == 2:
        rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    else:
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    kwargs: Dict[str, object] = {"detail": 1, "paragraph": False}
    if width_ths is not None:
        kwargs["width_ths"] = width_ths
    raw = reader.readtext(rgb, **kwargs)
    ox, oy = float(origin[0]), float(origin[1])
    inv = 1.0 / scale if scale else 1.0
    boxes: List[OcrBox] = []
    for item in raw:
        if len(item) < 3:
            continue
        pts_raw, text, conf = item[0], str(item[1]).strip(), float(item[2])
        if not text or conf < 0.25:
            continue
        pts = np.asarray(pts_raw, dtype=float).reshape(-1, 2) * inv + np.array(
            [ox, oy], dtype=float
        )
        xs, ys = pts[:, 0], pts[:, 1]
        boxes.append(
            OcrBox(
                text=text,
                conf=conf,
                pts=pts,
                cx=float(xs.mean()),
                cy=float(ys.mean()),
                x0=float(xs.min()),
                y0=float(ys.min()),
                x1=float(xs.max()),
                y1=float(ys.max()),
            )
        )
    return boxes


def calibrate_axes(
    frame: Tuple[int, int, int, int],
    x_ticks: Sequence[Tuple[float, float]],
    y_ticks: Sequence[Tuple[float, float]],
) -> AxisCalib:
    if len(x_ticks) < 2 or len(y_ticks) < 2:
        raise DigitizeError(
            f"Need at least two ticks on each axis; got {len(x_ticks)} x and {len(y_ticks)} y"
        )
    x0, y0, x1, y1 = (float(v) for v in frame)
    log_x = _looks_log([v for _, v in x_ticks])
    log_y = _looks_log([v for _, v in y_ticks])
    ax, bx = _fit_line([(p, np.log10(v) if log_x else v) for p, v in x_ticks if not log_x or v > 0])
    ay, by = _fit_line([(p, np.log10(v) if log_y else v) for p, v in y_ticks if not log_y or v > 0])
    xmin = ax * x0 + bx
    xmax = ax * x1 + bx
    ymin = ay * y1 + by  # bottom pixel
    ymax = ay * y0 + by  # top pixel
    if log_x:
        xmin, xmax = 10 ** xmin, 10 ** xmax
    if log_y:
        ymin, ymax = 10 ** ymin, 10 ** ymax
    if xmin > xmax:
        xmin, xmax = xmax, xmin
    if ymin > ymax:
        ymin, ymax = ymax, ymin
    return AxisCalib(
        x0=x0, y0=y0, x1=x1, y1=y1,
        xmin=float(xmin), xmax=float(xmax),
        ymin=float(ymin), ymax=float(ymax),
        ax=float(ax), bx=float(bx), ay=float(ay), by=float(by),
        log_x=log_x, log_y=log_y,
    )


def extract_series(
    image: np.ndarray,
    calib: AxisCalib,
    hide_rect: Optional[Tuple[float, float, float, float]] = None,
) -> List[Series]:
    """Trace coloured (and gray) polylines inside the calibrated plot frame."""
    pad = 4
    x0 = int(calib.x0) + pad
    y0 = int(calib.y0) + pad
    x1 = int(calib.x1) - pad
    y1 = int(calib.y1) - pad
    if x1 <= x0 or y1 <= y0:
        raise DigitizeError("Plot frame is too small to extract series")
    crop = image[y0:y1, x0:x1].copy()
    if hide_rect is not None:
        hx0 = int(round(hide_rect[0] - x0))
        hy0 = int(round(hide_rect[1] - y0))
        hx1 = int(round(hide_rect[2] - x0))
        hy1 = int(round(hide_rect[3] - y0))
        cv2.rectangle(crop, (hx0, hy0), (hx1, hy1), (255, 255, 255), thickness=-1)
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    hue, sat, val = cv2.split(hsv)
    white = (val > 245) & (sat < 35)
    black = val < 45
    foreground = ~(white | black)

    series: List[Series] = []
    gray_mask = foreground & (sat <= 45) & (val < 220)
    if int(np.count_nonzero(gray_mask)) > 80:
        traced = _mask_to_series(
            gray_mask, crop, "gray line", (120, 120, 120), x0, y0, calib
        )
        if traced is not None:
            series.append(traced)

    colour_mask = foreground & (sat > 45)
    for mask, bgr, label in _hue_groups(hue, colour_mask, crop):
        traced = _mask_to_series(mask, crop, label, bgr, x0, y0, calib)
        if traced is not None:
            series.append(traced)
    return series


def thickness_to_metres(value: float, unit: str) -> float:
    unit = unit.lower().replace("µ", "u").replace("μ", "u")
    scale = {"m": 1.0, "mm": 1e-3, "um": 1e-6, "nm": 1e-9}
    if unit not in scale:
        raise DigitizeError(f"Unknown thickness unit {unit!r}")
    return float(value) * scale[unit]


def parse_thicknesses(text: str) -> List[float]:
    found: List[float] = []
    for match in _THICKNESS_RE.finditer(text or ""):
        found.append(thickness_to_metres(float(match.group(1)), match.group(2)))
    return found


def parse_tool(text: str, tools: Sequence[str]) -> Optional[str]:
    blob = normalise_ocr_text(text or "").lower()
    for tool in tools:
        if tool and tool.lower() in blob:
            return tool
    # Common tool steels even if the constants module has not been loaded.
    for tool in ("P20", "H13", "CastIron", "cast iron"):
        if tool.lower() in blob:
            return "CastIron" if tool.lower() in {"castiron", "cast iron"} else tool
    return None


def normalise_ocr_text(text: str) -> str:
    """Fix common EasyOCR confusions in legend / axis text (``P2O`` → ``P20``)."""
    cleaned = re.sub(r"\s+", " ", (text or "").strip())
    for pattern, repl in _OCR_TOOL_FIXES:
        cleaned = pattern.sub(repl, cleaned)
    return cleaned


def stitch_legend_rows(boxes: Sequence[OcrBox]) -> List[OcrBox]:
    """Merge OCR boxes that sit on the same baseline into one legend row.

    EasyOCR with ``paragraph=False`` returns word fragments such as
    ``conditions`` / ``dry``.  Those must not be treated as complete labels.
    The merged box keeps the leftmost ``x0`` so swatch sampling still looks
    to the left of the row's text.
    """
    usable = [box for box in boxes if (box.text or "").strip()]
    if not usable:
        return []
    heights = [max(box.y1 - box.y0, 1.0) for box in usable]
    tol = float(np.clip(0.6 * float(np.median(heights)), 6.0, 14.0))
    ordered = sorted(usable, key=lambda b: (b.cy, b.cx))
    clusters: List[List[OcrBox]] = []
    for box in ordered:
        if clusters:
            members = clusters[-1]
            cluster_cy = float(np.mean([m.cy for m in members]))
            if abs(box.cy - cluster_cy) <= tol:
                members.append(box)
                continue
        clusters.append([box])

    rows: List[OcrBox] = []
    for members in clusters:
        members = sorted(members, key=lambda b: b.cx)
        seen: set = set()
        texts: List[str] = []
        for member in members:
            token = member.text.strip()
            key = token.lower()
            if key in seen:
                continue
            seen.add(key)
            texts.append(token)
        texts = _drop_redundant_tokens(texts)
        text = normalise_ocr_text(" ".join(texts))
        if not text:
            continue
        x0 = min(m.x0 for m in members)
        y0 = min(m.y0 for m in members)
        x1 = max(m.x1 for m in members)
        y1 = max(m.y1 for m in members)
        pts = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], dtype=float)
        rows.append(
            OcrBox(
                text=text,
                conf=max(m.conf for m in members),
                pts=pts,
                cx=float((x0 + x1) / 2.0),
                cy=float((y0 + y1) / 2.0),
                x0=float(x0),
                y0=float(y0),
                x1=float(x1),
                y1=float(y1),
            )
        )
    rows.sort(key=lambda b: (b.cy, b.cx))
    return rows


def fill_missing_deltas(
    series: Sequence[Series],
    thicknesses: Sequence[float] = (),
) -> List[Series]:
    """If OCR did not tag dry/lube, infer ``delta`` from curve intercepts.

    Of two model lines, the lower intercept is dry (``delta=0``) and the
    higher one takes the first known lubricant thickness.
    """
    named = list(series)
    line_idxs = [
        i
        for i, item in enumerate(named)
        if item.is_model and item.kind == "line" and len(item.y) >= 5
    ]
    if len(line_idxs) < 2:
        return named

    missing = [i for i in line_idxs if named[i].delta is None]
    known_dry = any(named[i].delta == 0 for i in line_idxs)
    lube_val = next(
        (float(named[i].delta) for i in line_idxs if named[i].delta not in (None, 0)),
        None,
    )
    if lube_val is None and thicknesses:
        lube_val = float(thicknesses[0])

    if len(missing) == 1:
        idx = missing[0]
        if lube_val is not None and not known_dry:
            named[idx] = replace(named[idx], delta=0.0)
        elif known_dry and lube_val is not None:
            named[idx] = replace(named[idx], delta=lube_val)
        return named

    if len(missing) >= 2 and lube_val is not None:
        ranked = sorted(missing, key=lambda i: _series_intercept(named[i]))
        lo, hi = ranked[0], ranked[-1]
        if _series_intercept(named[hi]) - _series_intercept(named[lo]) >= 1.0:
            named[lo] = replace(named[lo], delta=0.0)
            named[hi] = replace(named[hi], delta=lube_val)
    return named


# --------------------------------------------------------------------------- #
# Internals
# --------------------------------------------------------------------------- #

def _frame_area(frame: Tuple[int, int, int, int]) -> int:
    return max(0, frame[2] - frame[0]) * max(0, frame[3] - frame[1])


def _frame_intersection(
    a: Tuple[int, int, int, int], b: Tuple[int, int, int, int]
) -> int:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    return max(0, x1 - x0) * max(0, y1 - y0)


def _dedupe_frames(
    frames: Sequence[Tuple[int, int, int, int]], iou: float = 0.5
) -> List[Tuple[int, int, int, int]]:
    """Keep the largest copy of overlapping / nested subplot boxes."""
    kept: List[Tuple[int, int, int, int]] = []
    for frame in sorted(frames, key=_frame_area, reverse=True):
        drop = False
        for other in kept:
            inter = _frame_intersection(frame, other)
            smaller = min(_frame_area(frame), _frame_area(other))
            union = _frame_area(frame) + _frame_area(other) - inter
            if union and inter / union >= iou:
                drop = True
                break
            if smaller and inter / smaller >= 0.85:
                drop = True
                break
        if not drop:
            kept.append(frame)
    return kept


def _easyocr_reader():
    global _READER
    if _READER is None:
        import easyocr

        _READER = easyocr.Reader(["en"], gpu=False, verbose=False)
    return _READER


def _parse_number(text: str) -> Optional[float]:
    cleaned = (text or "").strip().replace(",", "").replace("−", "-")
    if not _NUMBER_RE.match(cleaned):
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _axis_ticks(
    ocr: Sequence[OcrBox], frame: Tuple[int, int, int, int]
) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
    x0, y0, x1, y1 = frame
    x_cands: List[Tuple[float, float, float]] = []  # pixel, value, distance to spine
    y_cands: List[Tuple[float, float, float]] = []
    for box in ocr:
        if box.conf < 0.4:
            continue
        value = _parse_number(box.text)
        if value is None:
            continue
        below = y1 - 8 <= box.cy <= y1 + 80 and x0 - 20 <= box.cx <= x1 + 40
        left = x0 - 70 <= box.cx <= x0 + 12 and y0 - 20 <= box.cy <= y1 + 20
        if below:
            x_cands.append((box.cx, value, abs(box.cy - y1)))
        elif left:
            y_cands.append((box.cy, value, abs(box.cx - x0)))
    x_ticks = _dedupe_ticks(x_cands)
    y_ticks = _dedupe_ticks(y_cands)
    return _reject_tick_outliers(x_ticks), _reject_tick_outliers(y_ticks)


def _dedupe_ticks(
    ticks: Sequence[Tuple[float, float, float]], px_tol: float = 10.0
) -> List[Tuple[float, float]]:
    """Keep one tick per pixel cluster; prefer the candidate closer to the axis."""
    ordered = sorted(ticks, key=lambda t: (t[0], t[2]))
    out: List[Tuple[float, float, float]] = []
    for px, value, dist in ordered:
        if out and abs(px - out[-1][0]) < px_tol:
            if dist < out[-1][2]:
                out[-1] = (px, value, dist)
            continue
        out.append((px, value, dist))
    return [(px, value) for px, value, _ in out]


def _reject_tick_outliers(
    ticks: Sequence[Tuple[float, float]], max_resid: float = 1.25
) -> List[Tuple[float, float]]:
    """Drop labels that do not lie on the linear tick scale (OCR fragments)."""
    ticks = list(ticks)
    if len(ticks) < 3:
        return ticks
    kept = ticks
    for _ in range(3):
        if len(kept) < 3:
            break
        slope, intercept = _fit_line(kept)
        resid = [abs(slope * px + intercept - value) for px, value in kept]
        worst = max(resid)
        if worst <= max_resid:
            break
        drop = resid.index(worst)
        kept = [tick for i, tick in enumerate(kept) if i != drop]
    return kept


def _axis_labels(ocr: Sequence[OcrBox], frame: Tuple[int, int, int, int]) -> Tuple[str, str]:
    x0, y0, x1, y1 = frame
    x_parts = [
        box for box in ocr
        if box.cy > y1 + 4 and x0 - 40 <= box.cx <= x1 + 40 and _parse_number(box.text) is None
    ]
    y_parts = [
        box for box in ocr
        if box.cx < x0 - 2 and y0 - 20 <= box.cy <= y1 + 20 and _parse_number(box.text) is None
    ]
    x_parts.sort(key=lambda b: b.cx)
    y_parts.sort(key=lambda b: b.cy)
    x_label = " ".join(b.text for b in x_parts).strip()
    y_label = " ".join(b.text for b in y_parts).strip()
    return x_label, y_label


def _drop_redundant_tokens(texts: Sequence[str]) -> List[str]:
    """Drop OCR fragments that are already contained in a longer token on the row."""
    norms = [re.sub(r"[^a-z0-9.]+", "", (t or "").lower()) for t in texts]
    kept: List[str] = []
    for i, token in enumerate(texts):
        needle = norms[i]
        if len(needle) < 4:
            kept.append(token)
            continue
        if any(needle != other and needle in other for j, other in enumerate(norms) if j != i):
            continue
        kept.append(token)
    return kept


def _legend_boxes(ocr: Sequence[OcrBox], frame: Tuple[int, int, int, int]) -> List[OcrBox]:
    x0, y0, x1, y1 = frame
    mid_x = (x0 + x1) / 2
    boxes = [
        box for box in ocr
        if x0 < box.cx < x1 and y0 < box.cy < y1 and box.cx > mid_x
        and _parse_number(box.text) is None
    ]
    boxes.sort(key=lambda b: (b.cy, b.cx))
    return boxes


def _read_legend_crop(
    image: np.ndarray, frame: Tuple[int, int, int, int]
) -> List[OcrBox]:
    """OCR an upscaled right-hand crop so small legend glyphs stay readable."""
    x0, y0, x1, y1 = (int(v) for v in frame)
    mid_x = int((x0 + x1) / 2)
    crop = image[y0:y1, mid_x:x1]
    if crop.size == 0 or crop.shape[0] < 20 or crop.shape[1] < 20:
        return []
    h, w = crop.shape[:2]
    up = cv2.resize(
        crop,
        (int(w * _LEGEND_SCALE), int(h * _LEGEND_SCALE)),
        interpolation=cv2.INTER_CUBIC,
    )
    return read_text(up, origin=(float(mid_x), float(y0)), scale=_LEGEND_SCALE, width_ths=0.7)


def _unique_legend_boxes(boxes: Sequence[OcrBox]) -> List[OcrBox]:
    seen: set = set()
    out: List[OcrBox] = []
    for box in boxes:
        key = (box.text.strip().lower(), int(round(box.cy / 4.0)), int(round(box.cx / 8.0)))
        if key in seen:
            continue
        seen.add(key)
        out.append(box)
    return out


def _collect_legend_boxes(
    image: np.ndarray,
    frame: Tuple[int, int, int, int],
    full_ocr: Sequence[OcrBox],
) -> List[OcrBox]:
    crop_boxes = _legend_boxes(_read_legend_crop(image, frame), frame)
    full_boxes = _legend_boxes(full_ocr, frame)
    return _unique_legend_boxes(list(crop_boxes) + list(full_boxes))


def _legend_hide_rect(
    rows: Sequence[OcrBox], pad_left: float = 36.0, pad: float = 8.0
) -> Optional[Tuple[float, float, float, float]]:
    if not rows:
        return None
    return (
        min(box.x0 for box in rows) - pad_left,
        min(box.y0 for box in rows) - pad,
        max(box.x1 for box in rows) + pad,
        max(box.y1 for box in rows) + pad,
    )


def _label_from_caption(caption: str, axis: str) -> Optional[str]:
    if not caption:
        return None
    aliases = _Y_ALIASES if axis == "y" else _X_ALIASES
    for pattern, _ in aliases:
        match = pattern.search(caption)
        if match:
            return match.group(0)
    return None


def _fit_line(points: Sequence[Tuple[float, float]]) -> Tuple[float, float]:
    if len(points) < 2:
        raise DigitizeError("Not enough points to fit an axis")
    p = np.array([a for a, _ in points], dtype=float)
    v = np.array([b for _, b in points], dtype=float)
    matrix = np.vstack([p, np.ones(len(p))]).T
    slope, intercept = np.linalg.lstsq(matrix, v, rcond=None)[0]
    return float(slope), float(intercept)


def _looks_log(values: Sequence[float]) -> bool:
    positive = sorted(v for v in values if v > 0)
    if len(positive) < 3:
        return False
    logs = np.log10(positive)
    gaps = np.diff(logs)
    if np.any(gaps <= 0):
        return False
    return float(np.std(gaps) / max(np.mean(gaps), 1e-9)) < 0.35 and float(np.mean(gaps)) > 0.4


def _hue_groups(
    hue: np.ndarray,
    mask: np.ndarray,
    crop: np.ndarray,
    max_k: int = 3,
) -> List[Tuple[np.ndarray, Tuple[int, int, int], str]]:
    ys, xs = np.where(mask)
    if len(xs) < 40:
        return []
    angle = hue[ys, xs].astype(np.float32) * np.pi / 90.0
    features = np.stack([np.cos(angle), np.sin(angle)], axis=1).astype(np.float32)
    k = max(1, min(max_k, len(xs) // 80))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 25, 1.0)
    compactness = float("inf")
    labels = np.zeros(len(xs), dtype=np.int32)
    for trial_k in range(1, k + 1):
        compact, lab, _ = cv2.kmeans(
            features, trial_k, None, criteria, 4, cv2.KMEANS_PP_CENTERS
        )
        if compact < compactness * 0.55 or trial_k == 1:
            compactness = float(compact)
            labels = lab.ravel()
            k = trial_k
        else:
            break

    groups: List[Tuple[np.ndarray, Tuple[int, int, int], str]] = []
    for idx in range(int(labels.max()) + 1):
        sel = labels == idx
        if int(sel.sum()) < 30:
            continue
        cluster = np.zeros(mask.shape, dtype=bool)
        cluster[ys[sel], xs[sel]] = True
        mean_bgr = tuple(int(v) for v in crop[cluster].mean(axis=0))
        groups.append((cluster, mean_bgr, _colour_name(mean_bgr)))
    return groups


def _colour_name(bgr: Tuple[int, int, int]) -> str:
    b, g, r = bgr
    hsv = cv2.cvtColor(np.uint8([[[b, g, r]]]), cv2.COLOR_BGR2HSV)[0, 0]
    h, s, v = (int(x) for x in hsv)
    if s < 40:
        return "gray line"
    if h <= 10 or h >= 170:
        return "red series"
    if h < 25:
        return "orange series"
    if h < 40:
        return "yellow series"
    if h < 90:
        return "green series"
    if h < 130:
        return "blue series"
    return "magenta series"


def _mask_to_series(
    mask: np.ndarray,
    crop: np.ndarray,
    name: str,
    bgr: Tuple[int, int, int],
    x_off: int,
    y_off: int,
    calib: AxisCalib,
) -> Optional[Series]:
    n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        mask.astype(np.uint8), connectivity=8
    )
    # Drop tiny speckles.
    clean = np.zeros(mask.shape, dtype=bool)
    for i in range(1, n_labels):
        if stats[i, cv2.CC_STAT_AREA] >= 12:
            clean[labels == i] = True
    if int(np.count_nonzero(clean)) < 25:
        return None

    coverage = len(np.unique(np.where(clean)[1])) / max(clean.shape[1], 1)
    widths = [stats[i, cv2.CC_STAT_WIDTH] for i in range(1, n_labels) if stats[i, cv2.CC_STAT_AREA] >= 12]
    median_width = float(np.median(widths)) if widths else 0.0
    kind = "line" if coverage > 0.35 or median_width > 0.4 * clean.shape[1] else "scatter"
    is_model = kind == "line" and not _EXPERIMENT_RE.search(name)

    xs_pix: List[float] = []
    ys_pix: List[float] = []
    cols = np.unique(np.where(clean)[1])
    for col in cols:
        rows = np.where(clean[:, col])[0]
        if len(rows) == 0:
            continue
        xs_pix.append(float(x_off + col))
        ys_pix.append(float(y_off + np.median(rows)))

    if len(xs_pix) < 5:
        return None

    data_x, data_y = [], []
    for px, py in zip(xs_pix, ys_pix):
        x, y = calib.to_data(px, py)
        if calib.xmin - 0.05 * abs(calib.xmax - calib.xmin) <= x <= calib.xmax + 0.05 * abs(calib.xmax - calib.xmin):
            if calib.ymin - 0.05 * abs(calib.ymax - calib.ymin) <= y <= calib.ymax + 0.05 * abs(calib.ymax - calib.ymin):
                data_x.append(x)
                data_y.append(y)
    if len(data_x) < 5:
        return None
    order = np.argsort(data_x)
    return Series(
        name=name,
        x=np.asarray(data_x, dtype=float)[order],
        y=np.asarray(data_y, dtype=float)[order],
        color_bgr=bgr,
        kind=kind,
        is_model=is_model,
    )


def _series_intercept(series: Series) -> float:
    y = np.asarray(series.y, dtype=float)
    if y.size == 0:
        return float("nan")
    n = max(3, y.size // 20)
    return float(np.median(y[:n]))


def _annotate_series(
    series: Sequence[Series],
    legend_boxes: Sequence[OcrBox],
    image: np.ndarray,
    tools: Sequence[str],
) -> List[Series]:
    legend_blob = " ".join(box.text for box in legend_boxes)
    global_tool = parse_tool(legend_blob, tools)
    thicknesses = parse_thicknesses(legend_blob)
    named: List[Series] = []

    colour_to_text: List[Tuple[Tuple[int, int, int], str]] = []
    for box in legend_boxes:
        swatch = _swatch_colour(image, box)
        colour_to_text.append((swatch, box.text))

    for item in series:
        name = item.name
        delta = None
        tool = global_tool
        best_text = _closest_legend_text(item.color_bgr, colour_to_text)
        if best_text:
            name = best_text
            local_tool = parse_tool(best_text, tools)
            if local_tool:
                tool = local_tool
            local_d = parse_thicknesses(best_text)
            if local_d:
                delta = local_d[0]
        if delta is None and _DRY_RE.search(name):
            delta = 0.0
        if delta is None and _LUBE_RE.search(name) and thicknesses:
            delta = thicknesses[0]
        is_model = bool(_MODEL_RE.search(name)) or (
            item.kind == "line" and not _EXPERIMENT_RE.search(name)
        )
        if _EXPERIMENT_RE.search(name):
            is_model = False
        named.append(
            replace(item, name=name, tool=tool, delta=delta, is_model=is_model)
        )
    return fill_missing_deltas(named, thicknesses)


def _swatch_colour(image: np.ndarray, box: OcrBox) -> Tuple[int, int, int]:
    h, w = image.shape[:2]
    x1 = max(0, int(box.x0) - 8)
    x0 = max(0, x1 - 28)
    y0 = max(0, int(box.cy) - 6)
    y1 = min(h, int(box.cy) + 6)
    patch = image[y0:y1, x0:x1]
    if patch.size == 0:
        return (0, 0, 0)
    hsv = cv2.cvtColor(patch, cv2.COLOR_BGR2HSV)
    sat, val = hsv[:, :, 1], hsv[:, :, 2]
    interesting = (val < 245) & (val > 40)
    if not np.any(interesting):
        return tuple(int(v) for v in patch.reshape(-1, 3).mean(axis=0))
    return tuple(int(v) for v in patch[interesting].mean(axis=0))


def _closest_legend_text(
    colour: Tuple[int, int, int],
    legend: Sequence[Tuple[Tuple[int, int, int], str]],
) -> Optional[str]:
    if not legend:
        return None
    c = np.asarray(colour, dtype=float)
    best_text, best_dist = None, 1e9
    for swatch, text in legend:
        dist = float(np.linalg.norm(c - np.asarray(swatch, dtype=float)))
        if dist < best_dist:
            best_text, best_dist = text, dist
    return best_text if best_dist < 90 else None


def _csv_escape(text: str) -> str:
    if any(ch in text for ch in ",\"\n"):
        return '"' + text.replace('"', '""') + '"'
    return text
