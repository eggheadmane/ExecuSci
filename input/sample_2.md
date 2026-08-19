# Experimental and modelling study of friction evolution and lubricant breakdown behaviour under varying contact conditions in warm aluminium forming processes 

Xiao Yang ${ }^{\mathrm{a}}$, Xiaochuan Liu ${ }^{\mathrm{b}}$, Heli Liu ${ }^{\mathrm{a}}$, Denis J. Politis ${ }^{\mathrm{c}}$, David Leyvraz ${ }^{\mathrm{d}}$, LiLiang Wang ${ }^{\mathrm{a}, *}$<br>${ }^{\mathrm{a}}$ Department of Mechanical Engineering, Imperial College London, London, SW7 2AZ, UK<br>${ }^{\mathrm{b}}$ School of Mechanical Engineering, Xi'an Jiaotong University, Xi'an, 710049, China<br>${ }^{\mathrm{c}}$ Department of Mechanical and Manufacturing Engineering, University of Cyprus, Nicosia, 1678, Cyprus<br>${ }^{\mathrm{d}}$ Novelis Switzerland SA, Novelis Innovation Center Sierre, Rte des Laminoirs 15, CH - 3960, Sierre, Switzerland

ARTICLE INFO

Keywords:
Friction evolution
Lubricant breakdown
Interactive friction model
Aluminium forming


#### Abstract

The lubricant behaviours under varying contact conditions were investigated by conducting pin-on-strip tests between P20 tool steel and AA7075 aluminium alloy using an automated testing system, Tribo-Mate. The effects of temperature changes, and rapid load and speed changes on the coefficient of friction (COF) and lubricant breakdown phenomenon were experimentally studied. The evolutions of COF showed three distinct stages, indicating the transformation from boundary lubrication condition to dry sliding condition. The value of COF at the initial stage was found to increase with increasing temperature. The increase of temperature, contact load and sliding speed caused an earlier breakdown of the lubricant. An interactive friction model was developed to predict friction evolutions at varying contact conditions. A close agreement with errors less than 6.8\% were achieved between the model predictions and experimental results.


## 1. Introduction

The coefficient of friction (COF) at the tool-workpiece interface is one of the most important boundary conditions in metal forming processes, which influences the material flow and required forming loads [1,2]. The COF is influenced by a vast number of variables and contact conditions including contact pressure, relative sliding speed and temperature at the interface making the determination of an exact value challenging [3-5].

Established research studies have documented that the contact conditions at the interface vary historically and spatially in metal forming processes. Contact pressure is unevenly distributed across the tool-workpiece interface due to the complexity of tooling geometry combined with the flow of workpiece material. Rapid changes of contact pressure and sliding speed occur at particular positions on the tool, such as the die radius, due to the sudden contact and detachment from the tool [6-8]. Variations in wear severity across the workpiece surface also occurs owing to the uneven distributed pressure and relative movement depending on interfacial geometry and local constraints [9,10]. Temperature distribution is affected by the local cooling rate, which is influenced by contact pressure distribution, thermal properties and local thickness of the specimen and lubricant properties and, thus, is non-uniform across the tool-workpiece interface. The evolution of temperature at a specific position on the tool is affected by the interfacial heat transfer and deformation energy of the workpiece material [11,12].

There is substantial literature focused on the effects of varying contact conditions on the COF under dry sliding conditions and the wear/ galling that occurs in metal forming processes. Hu et al. investigated the dynamic formation of the aluminium transfer layer under load varying conditions at room temperature and found that the contact load change would rebuild the dynamic balance of wear particles and influence friction evolution and saturation transfer volume at the steady state [13]. Pereia et al. proposed a method to numerically describe the distribution of the sliding distance and determine the position where the most severe wear occurred by characterising the varying contact conditions on the tool-workpiece interfaces for cold stamping of steel [10]. Venema et al. investigated the dependency of coefficient of friction on temperature during dry sliding between relatively clean surfaces in the press hardening of UHSS and found that the ratio of adhered/abraded material decreased with the increase of temperature [14]. A tribological

[^0]test programme was developed in which a pin continuously slid on hot steel strips and the mass loss was evaluated with variable contact pressure and sliding velocity that represented the press hardening process [15].

The lubricant breakdown phenomenon involves a transition of lubrication mode at the contact interface, leading to a vast change in friction values [16,17]. However, a constant coefficient of friction value is usually assigned in FE simulations to represent the complex tribological conditions at the interface, which is not suitable and will cause inaccuracy in the predicted results [4]. The lubricant breakdown phenomenon has been studied at constant contact conditions at room temperature to replicate metal forming processes. It is found that an increase of friction coefficient occurs when the lubrication condition transforms from the full film lubricated condition to the boundary lubricated condition. An increase in contact pressure and a decrease of sliding speed leads to a larger diminution rate of the film thickness and an earlier occurrence of the lubricant breakdown phenomenon [18]. Friction evolutions between P20 and non-alloy martensitic steel have been investigated by conducting pin-on-disc tests at lubricated conditions and the testing results have been successfully implemented into FE simulations by showing good agreements with experimentally formed components [19]. Full film lubrication is difficult to be sustained because of the decrease of lubricant viscosity at elevated temperatures and boundary lubrication is found to be prevailing in warm and hot metal forming processes [20].

For warm aluminium forming processes, lubricant is necessary at the tool-workpiece interface to decrease forming load and eliminate galling between hot aluminium alloy and cold forming tools. However, there have been limited investigations in analysing the effects of varying contact conditions as a function of sliding distance on the COF evolution and lubricant breakdown behaviours at elevated temperatures.

In this paper, friction tests between P20 and AA7075 were conducted to investigate the coefficient of friction evolution and lubricant breakdown behaviours under varying contact conditions, including investigation of the variations: load jump, speed jump and temperature changes. An interactive friction model was established to predict the friction evolution considering the effects of these variables. A close agreement with errors less than $6.8 \%$ were achieved between the model predictions and experimental results.

## 2. Methodology

### 2.1. Materials

A lab-scale automated tribo-testing system, Tribo-Mate, with a Universal Robot and pin-on-strip configurations, as shown in Fig. 1, was used to investigate friction evolutions under varying contact conditions. The strip was made from an AA7075 aluminium alloy blank with a thickness of 1.6 mm and an average surface roughness (Ra) of $0.3 \mu \mathrm{~m}$. The pin was made from P20 tool steel in the pre-hardened condition with a hardness of approximately 320 HV. The diameter of the spherical pinhead was 6 mm with an average surface roughness (Ra) of $0.8 \mu \mathrm{~m}$. The surface roughness of $0.8 \mu \mathrm{~m}$ was specified by the tool maker. The lubricant utilized in the friction tests was a lubricant grease dedicatedly developed for warm aluminium forming processes. The kinematic viscosity of the lubricant was 11.74 cSt at 40 °C and 5.62 cSt at 100 °C, and the specific gravity of the lubricant was 0.93 at 15 °C. The lubricant was only applied on the steel pin and the initial lubricant volume was 23.2 g/ $\mathrm{m}^{2}$ in all the tests. The amount of lubricant applied was carefully controlled by a dedicated tool with precisely machined pockets (lubricant reservoirs) of various depths ranging from 2 to 4 mm. Lubricant was held in the pockets prior to the tests and was applied to the pin surface by dipping the pin into a pocket with a specific normal load applied, and thus a repeatable amount of lubricant adhered on the steel pin for each test.

### 2.2. Test methods

The automated testing system, Tribo-Mate, was utilized to realize rapid changes in contact load and speed during the sliding process. The effective feedback system of the robot made it possible to change the contact load and sliding speed within a very short time, thus realizing load/speed jump or continuous changes in these contact conditions during the sliding process. By designing suitable cooling channels in the specimen holder, temperature changes with a constant or variable gradient over the sliding distance could be achieved in the blank. A dedicated force sensor was applied on the robot to acquire the force data.

In this research, three groups of tests were designed to investigate the effects of load, speed and temperature changes on the friction evolution and lubricant breakdown behaviours. Friction tests at constant contact conditions were conducted as benchmarks. The testing contact conditions were determined according to the characteristics at the toolworkpiece interfaces of warm aluminium forming processes [21,22], as demonstrated in the test matrix of Table 1. These characteristics include the contact load, relative sliding speed and interfacial temperature. Mean contact pressure was calculated based on a plastic model considering the width of wear track at elevated temperatures [23]. In each friction test, the aluminium blank was first heated to the target temperature and the cold steel pin was activated to slide against the blank specimen. Each test condition was conducted three times and the COF evolution as a function of the sliding distance was recorded. For each test condition, the average data scatter and standard deviation were recorded as presented in the subsequent section.

### 2.2.1. Friction tests with temperature changes

In the friction tests, temperature was varied linearly with increasing sliding distance to represent temperature evolutions which are

![](https://cdn.mathpix.com/cropped/35c5b818-0eb5-4053-9148-968283315c0f-02.jpg?height=491&width=1438&top_left_y=2035&top_left_x=314)
Fig. 1. Schematic diagram of the tribo-testing system, Tribo-Mate.

Table 1
Test matrix of friction tests at varying contact conditions.
| Test No. | Temperature (°C) | Speed (mm/s) | Load (N) | Pressure (MPa) | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 200 | 50 | 5 | 410 | Constant |
| 2 | 300 | 50 | 5 | 270 | conditions |
| 3 | 300 → 200 | 50 | 5 | 270 → 410 | Temperature decrease |
| 4 | $200 \rightarrow 300$ | 50 | 5 | $410 \rightarrow 270$ | Temperature increase |
| 5 | 300 | 50 | 5 | 270 | Constant |
| 6 | 300 | 50 | 8 | 360 | conditions |
| 7 | 300 | 50 | $5 \rightarrow 8$ | 270 → 360 | Load increase |
| 8 | 300 | 50 | $8 \rightarrow 5$ | 360 → 270 | Load decrease |
| 9 | 250 | 50 | 5 | 340 | Constant |
| 10 | 250 | 80 | 5 | 340 | conditions |
| 11 | 250 | 50 → 80 | 5 | 340 | Speed increase |
| 12 | 250 | $80 \rightarrow 50$ | 5 | 340 | Speed decrease |


continuous and gradual in metal forming processes [11]. A temperature decrease from 300 °C to 200 °C and an increase from 200 °C to 300 °C at the changing rate of $(67.5 \pm 7.5)^{\circ} \mathrm{C} / \mathrm{s}$ were applied during a speed of 50 mm/s and a contact load of 5 N.

### 2.2.2. Friction tests with abrupt load changes

Abrupt contact load changes are widely observed in metal forming processes, due to materials being drawn into the die cavity and the sudden contact and detachment from the tools. The contact load changes are between 10\% and 30\% within several milliseconds [6,21]. In the present research, a load increase from 5 N to 8 N and a decrease from 8 N to 5 N were applied within 0.1s by the ultra-precise control of Tribo-Mate.

### 2.2.3. Friction tests with abrupt speed changes

The sliding speed variable also experiences rapid changes at the contact interfaces. In this study, a speed increase from 50 mm/s to 80 mm/s and a decrease from 80 mm/s to 50 mm/s within 0.3s were conducted and investigated. The temperature of 250 °C was selected to clearly demonstrate the effects of sliding speeds on the friction evolution and lubricant breakdown behaviour at constant and varying conditions.

## 3. Results and discussion

3.1. Friction evolution with lubricant diminution effects at elevated temperatures

The friction evolution with lubricant diminution effect at the temperature of 300 °C, speed of 50 mm/s and contact load of 5 N (test no.2) is shown in Fig. 2. The COF began and stabilized at a low value of approximately 0.24 during a sliding distance of 19 mm, then increased rapidly from 0.24 to 1.5 with the increase of the sliding distance from 19 mm to 38 mm, and finally showed severe fluctuations at the value of approximately 1.5. According to the experimental results, the sliding process can be divided into three stages. The first stage with the low friction value occurred when boundary lubrication was prevalent. The second stage with the rapidly increasing COF was the transition stage when the lubricant film thickness decreased to a critical value. The final plateau stage occurred with high friction values when the lubricant breakdown occurred and the two surfaces had intimate contact. It has been examined and observed that three stages, i.e. the low friction stage, the transition stage and the breakdown stage, existed for all the test conditions. OM images of the wear track at points 1-4 (as shown in Fig. 2) on the aluminium blank are demonstrated in Fig. 3.

In the first stage (point 1 ), the friction value was approximately 0.24 . Plowing grooves were observed on the aluminium surface and the wear track was clearly visible at the low friction stage, as shown in Fig. 3a, indicating that the boundary lubrication occurred during this stage [20].

![](https://cdn.mathpix.com/cropped/35c5b818-0eb5-4053-9148-968283315c0f-03.jpg?height=702&width=855&top_left_y=189&top_left_x=1072)
Fig. 2. COF evolution at the elevated temperature of 300 °C with the speed of 50 mm/s and contact load of 5 N.

The friction force at this stage was generated from two parts. The lubricant was entrapped between the contact surfaces and shear force was generated due to the internal fluid flow during the sliding process. In addition, it also arose from the adhesion force between asperity contacts and plowing of hard asperities on the steel pin surface. As sliding proceeded, the lubricant film thickness gradually decreased owing to the transfer of the lubricant from the steel pin to the wear track on the aluminium blank.

At the beginning of the second stage (point 2), the coefficient of friction began to increase, aluminium wear particles agglomerated and formed wear debris lumps on the wear track, as shown by the dark areas in Fig. 3b. This could be results of the decrease in the thickness of lubricant film. As the lubricant film thickness decreased to the average height of the asperities at the interface [17,24], a significant amount of asperities at the contact interface came into contact. The relative motion resulted in the detachment of the aluminium wear particles and the subsequent formation of wear debris lumps on the wear track on the blank. As sliding proceeded (point 3), the area covered by wear debris lumps increased, as shown in Fig. 3c. This means an increased unlubricated contact area at the interface, which would cause an increase in the COF.

At the third stage (point 4), friction fluctuated severely at a value of approximately 1.5, which could be results of the breakdown of the lubricant leading to direct contact between the steel pin and hot aluminium blank. As a result of dry sliding, strong adhesive friction force between steel and hot aluminium with intimate contact could have contributed to the high value of coefficient of friction. Large numbers of aluminium wear particles were generated and formed wear debris lumps on the wear track, as illustrated in Fig. 3d, resulting in the severe fluctuation of friction values.

### 3.2. Effect of varying temperatures on the COF evolution

As shown in Fig. 4, the COF was initially stable at 0.24 at the initial low friction stage when a constant load of 5 N and speed of 50 mm/s was applied under a temperature of 300 °C. The coefficient of friction began to increase rapidly when the sliding distance reached 19 mm, suggesting that lubricant breakdown occurred. When the friction test was conducted at the temperature of 200 °C, the COF at the low friction stage decreased by 29.2\% to 0.17, compared to the friction value at 300 °C. The coefficient of friction was stable at 0.17 during a sliding distance of 83 mm, indicating that the lubricant breakdown distance was over 83

![](https://cdn.mathpix.com/cropped/35c5b818-0eb5-4053-9148-968283315c0f-04.jpg?height=1098&width=1445&top_left_y=185&top_left_x=310)
Fig. 3. OM images of wear track on the aluminium blank a) in stage I (initial low friction stage); b) at the transition point of stage I and II; c) in stage II (wear debris lumps unevenly distributed on the wear track); and d) in stage III where severe adhesive wear occurred. Sliding direction: black arrows (top right); unlubricated area and wear debris lumps: white arrow heads.

![](https://cdn.mathpix.com/cropped/35c5b818-0eb5-4053-9148-968283315c0f-04.jpg?height=650&width=859&top_left_y=1473&top_left_x=138)
Fig. 4. Effect of temperature decrease on the COF evolution. Symbols represent the average values; envelopes represent SD.

mm at 200 °C.
When temperature decreased from 300 °C to 200 °C during the sliding process, the COF at the low friction stage decreased by 20\% from 0.25 to 0.20 before the lubricant breakdown occurred at the sliding distance of 23 mm. The temperature decrease test represents the quenching effect of the workpiece in warm stamping processes and the results indicate that friction values and breakdown behaviours would change due to the varying thermal conditions at the contact interface.

The decrease in friction values before the lubricant breakdown occurred was due to the potential decrease of adhesion and plowing forces as temperature decreased. According to the results shown in Fig. 4, the lubricant breakdown distance during the temperature decrease test was between the constant temperature tests at 200 °C and 300 °C. It was found that the decreasing temperature increased the lubricant viscosity. The increase in the viscosity led to reduced lubricant volume being transferred onto the wear track and a decrease of the film thickness diminution rate, resulting in a larger sliding distance before

![](https://cdn.mathpix.com/cropped/35c5b818-0eb5-4053-9148-968283315c0f-04.jpg?height=648&width=853&top_left_y=1843&top_left_x=1072)
Fig. 5. Effect of temperature increase on the COF evolution. Symbols represent the average values; envelopes represent SD.

lubricant breakdown occurred.
As shown in Fig. 5, when the temperature increased from 200 °C to 300 °C over a total sliding distance of 65 mm, the coefficient of friction increased by 47\% from 0.17 to 0.25 before lubricant breakdown occurred at the distance of 58 mm . The increase of friction values at the initial low friction stage was due to the increased adhesion forces and plowing friction. With the increase of temperature, film thickness decreased at a faster rate and thus an earlier occurrence of lubricant breakdown was observed compared with that at 200 °C.

### 3.3. Effect of varying load on the COF evolution

The COF was stable at 0.24 at the low friction stage when a constant contact load of 5 N was applied at the speed of 50 mm/s and temperature of 300 °C, as shown in Fig. 6. At this stage, the boundary lubrication was dominant at the interface. When the sliding distance reached 19 mm, the lubricant breakdown occurred as the lubrication mode started to shift from the boundary lubrication condition to the dry condition, resulting in a sudden increase of the COF. When a larger contact load of 8 N was applied, the COF at the low friction stage remained at 0.24, although the lubricant breakdown distance decreased to 9.5 mm.

As shown in Fig. 6, when the contact load suddenly increased from 5 N to 8 N at the sliding distance of 8.5 mm, the lubricant breakdown occurred at the sliding distance of 15 mm, which was 21\% less than the breakdown distance of 19 mm in the constant load test at 5 N. The friction values at the initial low friction stage stabilized at 0.24 which was the same as those obtained at constant load conditions. As there was a step decrease of contact load from 8 N to 5 N at the sliding distance of 8 mm , the lubricant breakdown distance became 14 mm while the initial friction values were stable at 0.24, as shown in Fig. 7. Varying load conditions exist in forming processes during the sudden contact and detachment from the tools. The different lubricant behaviours shown in the testing results of constant and varying conditions signify that the applied lubricant performance would be influenced by the varying load conditions.

The COF at the low friction stage was not affected by the changes of contact load due to the characteristics in the boundary lubrication regime [17,25]. When the contact load increased, the lubricant film became thinner as more lubricant was transferred onto the wear track and the diminution rate of the film thickness increased. Thinner film was entrapped at the interface and earlier lubricant breakdown occurred.

![](https://cdn.mathpix.com/cropped/35c5b818-0eb5-4053-9148-968283315c0f-05.jpg?height=670&width=855&top_left_y=1822&top_left_x=138)
Fig. 6. Effect of load increase on the COF evolution. Symbols represent the average values; envelopes represent SD.

![](https://cdn.mathpix.com/cropped/35c5b818-0eb5-4053-9148-968283315c0f-05.jpg?height=670&width=853&top_left_y=189&top_left_x=1072)
Fig. 7. Effect of load decrease on the COF evolution. Symbols represent the average values; envelopes represent SD.

### 3.4. Effect of varying speed on the COF evolution

As shown in Fig. 8, when a speed of $50 \mathrm{~mm} / \mathrm{s}$ and a contact load of 5 N was applied at 250 °C in the friction test, the coefficient of friction stabilized at 0.20 before the sliding distance reached 47 mm . While a speed of 80 mm/s was applied, the distance decreased to 18 mm before lubricant breakdown occurred. The friction values began to increase rapidly after the lubricant breakdown.

As the speed increased from 50 mm/s to 80 mm/s at the sliding distance of 18 mm, the lubricant breakdown distance decreased by 40.4\% from 47 mm to 28 mm, compared with that at the constant speed of 50 mm/s, as shown in Fig. 8. In the test with the decrease of the speed from 80 mm/s to 50 mm/s at the distance of 10 mm, the lubricant breakdown distance increased by 66.7\% from 18 mm to 30 mm when compared with the constant speed test of 80 mm/s, as shown in Fig. 9. In the meanwhile, the friction values at the initial low friction stage were stable at 0.20 in the tests at varying speed conditions. Varying speed conditions at the interface would affect the lubricant behaviours in forming processes.

Increasing sliding speed caused a reduction in lubricant viscosity due to the frictional heat [26]. As the lubricant viscosity decreased, the

![](https://cdn.mathpix.com/cropped/35c5b818-0eb5-4053-9148-968283315c0f-05.jpg?height=659&width=857&top_left_y=1832&top_left_x=1072)
Fig. 8. Effect of speed increase on the COF evolution. Symbols represent the average values; envelopes represent SD.

![](https://cdn.mathpix.com/cropped/35c5b818-0eb5-4053-9148-968283315c0f-06.jpg?height=659&width=859&top_left_y=189&top_left_x=138)
Fig. 9. Effect of speed decrease on the COF evolution. Symbols represent the average values; envelopes represent SD.

lubricant film became thinner. Thus, the volume of lubricant transferred onto the wear track increased and the diminution of the film thickness increased rapidly, causing an earlier onset of the lubricant breakdown. Similar results were found by Czichos [27] where the lubricant breakdown was accelerated with increasing sliding speed.

## 4. Development of an interactive friction model for lubricant behaviours under varying contact conditions

### 4.1 Development of the interactive friction model

The framework of interactive friction modelling has been applied to describe friction evolution at room temperature in a coated system [28], a lubricated contact [18] and a dry sliding condition where adhesive wear occurs [13,29] under constant contact conditions as in previous studies. Moreover, in this study, an interactive friction model was developed to investigate friction evolution and lubricant behaviours at elevated temperatures under varying contact conditions. The overall coefficient of friction $\mu(t)$ is expressed as a time dependent variable, composed of two parts at the interface, friction contributed by the lubricated area and friction contributed by the dry contact, respectively, when the lubrication mode at the contact interface evolves from the boundary lubrication condition to the final dry condition, as shown in Eq. (1).

$$
\begin{equation*}
\mu(t)=(1-\beta) \mu_{l}(t)+\beta \mu_{d}(t) \tag{1}
\end{equation*}
$$

$\mu_{l}(t)$ and $\mu_{d}(t)$ represent the friction values at boundary lubrication condition at the initial low friction stage and dry condition at the final plateau stage, respectively. Arrhenius equations were used to represent the temperature effects on the values of $\mu_{l}(t)$ and $\mu_{d}(t)$, as described by Eqs. (2) and (3):

$$
\begin{equation*}
\mu_{l}(t)=\mu_{l 0} \exp \left(-\frac{Q_{l}}{R T(t)}\right) \tag{2}
\end{equation*}
$$

$$
\begin{equation*}
\mu_{d}(t)=\mu_{d 0} \exp \left(-\frac{Q_{d}}{R T(t)}\right) \tag{3}
\end{equation*}
$$

where $\mu_{l 0}$ and $\mu_{d 0}$ are model constants, $Q_{l}$ and $Q_{d}$ are activation energy for lubricated and dry conditions, respectively. The contribution of $\mu_{l}(t)$ and $\mu_{d}(t)$ to the overall COF is characterised by the ratio between the unlubricated area and the lubricated area, $\beta$, which varies from 0 (boundary lubrication condition) to 1 (dry condition). The lubrication condition is determined by the lubricant film thickness entrapped at the interface. As the lubricant is smeared on the wear track and the film thickness decreases, more asperities at the interface come into contact, indicating the transformation from the boundary lubrication to the dry condition and leading to an overall increase of the COF. Thus, the relationship of the area ratio, $\beta$, and the instantaneous lubricant film thickness, $h(t)$, is modelled as Eq. (4), where $t$ is the sliding time and $\lambda_{1}$, $\lambda_{2}$ are model parameters.

$$
\begin{equation*}
\beta(t)=\exp \left[-\left(\lambda_{1} h(t)\right)^{\lambda_{2}}\right] \tag{4}
\end{equation*}
$$

When the thickness of lubricant film is smaller than the average height of the asperity peaks of the aluminium material, the lubricant breakdown would occur and the contact condition would begin to transfer from the boundary lubrication condition to the dry condition [17,24].

To calculate the instantaneous thickness entrapped at the contact interface, it is critical to consider the relation between the total amount of lubricant and that smeared on the wear track and the influencing contact parameters. The total amount of lubricant volume is assumed as constant during the sliding process. Therefore, the initial entrapped lubricant equals the sum of the instantaneous lubricant volume and the volume transferred on the wear track, which is presented as Eq. (5):

$$
\begin{equation*}
V(0)=V(t)+\Delta V(t)=V(t)+\int_{0}^{t} d V \tag{5}
\end{equation*}
$$

where $V(0)$ and $V(t)$ are the initial and instantaneous entrapped lubricant volume, respectively, and $\Delta V(t)$ represents the lubricant volume smeared on the wear track, which is integrated by the transferred amount of the lubricant onto the wear track during a short sliding time, $d V$, which can be expressed by Eq. (6):

$$
\begin{equation*}
d V=a h(t) \cdot w \cdot v^{k_{1}} d t \tag{6}
\end{equation*}
$$

where $h(t)$ is the instantaneous film thickness, $w$ is the width of the wear track, $v$ is the speed and $d t$ is the increment of sliding time. $a$ is a model parameter accounting for the influence of deformed contact area $(A)$ on the transferred volume of lubricant. The width of the wear track $(w)$ is affected by the normal contact pressure and the lubricant viscosity [30, 31], indicating $w=f(P, \eta)$, which can be written as $w=m P^{k_{3}} / \eta^{k_{2}}$, where $m$ is a constant, $P$ is the mean contact pressure and $\eta$ is the lubricant viscosity. Thus by incorporating these parameters ( $A$ is extracted from the model parameter $a$ and $m$ is integrated into $b$ ), Eq. (7) can be obtained from Eq. (6):

$$
\begin{equation*}
\Delta V=\int_{0}^{t} A \cdot b \frac{P^{k_{3}} v^{k_{1}}}{\eta^{k_{2}}} \cdot h(t) d t \tag{7}
\end{equation*}
$$

By taking the derivative on both sides, Eq. (7) can be written as Eq. (8):

$$
\begin{equation*}
\dot{h}(t)=\frac{\dot{V}(t)}{A}=-h(t)\left(c P^{k_{p}} v^{k_{v}} / \eta^{k_{\eta}}\right) \tag{8}
\end{equation*}
$$

where $\dot{h}(t)$ represents the diminution rate of the film thickness, $P, v$ and $\eta$ represent the mean contact pressure, sliding speed and lubricant viscosity at a specific temperature, respectively. $c$ is a model constant, $k_{p}, k_{v}$ and $k_{\eta}$ are the pressure-dependent, speed-dependent and viscositydependent parameters, respectively.

Considering the effect of temperature on the lubricant viscosity, the Arrhenius equation is applied to describe the relationship between the viscosity and temperature [32], as shown in Eq. (10), where $T$ represents the instantaneous temperature of the aluminium, $\eta_{0}$ is the model constant, $Q_{\eta}$ is the activation energy and $R$ is the universal gas constant. The deviation between the dynamic viscosity and kinematic viscosity is negligible as the change of the lubricant density could be ignored at elevated temperatures. The lubricant viscosity at the test conditions can
be obtained by Eq. (9).

$$
\begin{equation*}
\eta=\eta_{0} \exp \left(\frac{Q_{\eta}}{R T}\right) \tag{9}
\end{equation*}
$$

### 4.2 Optimization of the model parameters

The friction test results at constant contact conditions are used to calibrate the model parameters. The model was validated by comparing the predicted and experimental results at varying contact conditions. The calibration of the model parameters is essentially an optimization process once a proper objective function is confirmed, which is usually defined to compute the deviation between the modelling and experimental results. Thus, the objective function can be defined in terms of the square of the differences between the predicted and experimental results for the COF at different sliding distances, as shown in Eq. (10):

$$
\begin{equation*}
f(x)=\sum_{i=1}^{m} w_{i}\left(\mu_{i}^{p}-\mu_{i}^{e}\right)^{2} \tag{10}
\end{equation*}
$$

where $f(x)$ is the sum of residuals for the COF, $x\left(x=\left[x_{1}, x_{2}, \ldots \ldots, x_{s}\right]\right)$ represents the model parameters and $s$ is the number of the model parameters to be calibrated. $\mu_{i}^{p}$ and $\mu_{i}^{e}$ are the predicted and experimental results for the COF at the same sliding distances. $w$ is a weighting function and $m$ is the total number of data points considered.

The optimised parameters that were determined are displayed in Table 2. The comparisons between the predicted results by the model and the experimental results at varying contact conditions are shown in Fig. 10. Good agreements with errors less than 6.8\% have been achieved under varying contact conditions. Evolutions of lubricant film thickness and thickness diminution rate predicted by the interactive friction model are demonstrated to reveal the corresponding model responses in the temperature decrease, load increase and speed increase tests, respectively. As shown in Fig. 11a, temperature decrease results in a lubricant breakdown distance of 18 mm. The large difference in lubricant breakdown behaviours between this temperature decrease test and the constant temperature tests is successfully predicted by the interactive friction model through the deviations in the evolution of film thickness and thickness diminution rate. When the contact load suddenly increases from 5 N to 8 N at the sliding distance of 8.5 mm, the diminution rate of the lubricant thickness increases from $-38 \mu m / s$ to $-67 \mu m / \mathrm{s}$. As a consequence, the lubricant film thickness decreases at a faster rate and approaches the breakdown within a shorter distance, as shown in Fig. 11b. When there is a step change of the speed from 50 mm/s to 80 mm/s at the distance of 18 mm, the diminution rate of the lubricant thickness increases suddenly from $-19 \mu m / s$ to $-75 \mu m / s$, representing the corresponding responses of the developed model to the speed increase, as shown in Fig. 11c.

Therefore, it is proven that the COF evolution and the lubricant breakdown behaviours under varying contact conditions are successfully captured and accurately predicted by the developed interactive friction model.

Table 2
Parameters of the interactive friction model under varying contact conditions.
| Parameter | $\mu_{10}(-)$ | $\mu_{\mathrm{d} 0}(-)$ | $\mathrm{Q}_{1}(\mathrm{~kJ} / \mathrm{mol})$ | $\mathrm{Q}_{\mathrm{d}}(\mathrm{kJ} / \mathrm{mol})$ |
| :--- | :--- | :--- | :--- | :--- |
| Value | 1.23 | 9.65 | 7.8 | 8.8 |
| Parameter | $\lambda_{1}\left(\mu \mathrm{~m}^{-1}\right)$ | $\lambda_{2}(-)$ | c $\left(\mathrm{s}^{-1}\right)$ | $\mathrm{k}_{\mathrm{p}}(-)$ |
| Value | 20 | 1.10 | 0.012 | 2.05 |
| Parameter | $\mathrm{k}_{\mathrm{\eta}}(-)$ | $\eta_{0}\left(\mathrm{~mm}^{2} / \mathrm{s}\right)$ | $\mathrm{Q}_{\eta}(\mathrm{kJ} / \mathrm{mol})$ | R (J/(K ⋅ mol)) |
| Value | 5.30 | 0.12 | 11.93 | 8.314 |


## 5. Prediction of the friction evolution as a function of instantaneous contact conditions

Tribologically-related instantaneous contact conditions involve contact pressure, relative sliding speed, interfacial temperature and relative sliding distance at the tool-workpiece interface. By extracting data from experimentally verified FE simulations and making subsequent analysis, a comprehensive understanding can be achieved to demonstrate how contact conditions flow during the forming process and provide guidance for more relevant study.

Tribological-related data on the tool-workpiece interface in each forming step are extracted from the experimentally verified FE simulations. The relative sliding speed experienced by the element on the tool surface accounts for both translational sliding of workpiece material and the surface enlargement resulting from the large deformation. As the sliding time elapsed between the tool and workpiece is dependent on the component geometry and the region where the element is located, a time-based evolution process of contact conditions are transformed into a distance-based one which corresponds to the relative sliding distance at the tool-workpiece interface. The relative sliding distance experienced by the element on the tool surface is obtained by the accumulated material flow through the tool surface in each step and contact pressure, speed and temperature can be interpolated for each step accordingly. Thus the evolution processes of contact conditions as a function of the normalised sliding distance are figured out to describe the tribological characteristics of a specific metal forming process. A case study of the instantaneous contact conditions was obtained from a benchmark data package including experimentally verified FEA data for various warm aluminium forging processes [33] and shown in Fig. 12.

Under such complicated-varying contact conditions, the contact pressure is 284 MPa when the forming process initiates and decreases to the minimum value of 215 MPa when the sliding distance increases to 10 mm, followed by an increase to the maximum value of 375 MPa with increasing sliding distance to 22 mm. The average contact pressure during the forming process is 290 MPa. The sliding speed is 57 mm/s at the beginning of sliding and increases to the maximum value of 90 mm/s at the sliding distance of 13 mm, following by a decrease to the minimum value of 55 mm/s the average sliding speed during the forming process is 70 mm/s. The temperature decreases all through the sliding process, which demonstrates a maximum value of 300 °C, a minimum value of 220 °C and an average value of 250 °C.

The coefficient of friction as a function of the instantaneous contact conditions is predicted by the developed interactive friction model and shown in Fig. 13. In addition, the coefficient of friction under three different constant contact conditions are predicted as well. Condition 1 represents the constant conditions at the maximum values of contact pressure, sliding speed and temperature, Condition 2 represents the constant conditions at their average values, and Condition 3 represents the constant conditions at their minimum values.

At varying conditions of the evolution history of contact conditions shown in Fig. 12, the predicted coefficient of friction evolves with a slightly decrease from 0.24 to 0.22 at the beginning of the sliding before the lubricant breakdown occurs, which is primarily due to the decrease in temperature. At the sliding distance of about 10 mm, the lubricant breakdown occurs and the coefficient of friction starts to increase rapidly from 0.23 to 0.73, which is the accumulated effects of all the varied contact parameters. At the constant condition 1, the friction evolution demonstrates the shortest lubricant breakdown distance and largest friction values before the lubricant breakdown occurs as the interface undergoes most severe contact conditions among the three constant conditions. At the constant condition 2, the coefficient of friction shows similar evolution history as the varying conditions. However, the friction value of 0.2 at the low friction stage of constant condition 2 is smaller than that at varying conditions (0.24-0.22). The friction evolutions, between the constant and varying contact conditions, yields a largest deviation of about 45.8\% at the sliding distance of 17.4 mm. In

![](https://cdn.mathpix.com/cropped/35c5b818-0eb5-4053-9148-968283315c0f-08.jpg?height=1735&width=1445&top_left_y=185&top_left_x=312)
Fig. 10. Modelling results of the COF evolution under both constant and varying contact conditions compared with experimental results. Solid lines, modelling results; scatters, average values; envelopes, SDs.

addition, the lubricant breakdown distance of 15 mm is larger than that of 10 mm at the varying conditions. At the constant condition 3, the lubricant survives a sliding distance of 25 mm and the coefficient of friction remains at a low value of 0.19, which is due to low pressure, small speed and low temperature.

It is found that the coefficient of friction under varying contact conditions is significantly different from those under constant contact conditions, either using the maximum, minimum or average values. Therefore, the ability to predict the coefficient of friction as a function of instantaneous contact conditions is essential to acquire accurate friction results as boundary conditions in the metal forming processes.

## 6. Conclusions

In this paper, pin-on-strip tests between P20 tool steel and AA7075 aluminium alloys were conducted during lubricated sliding under varying contact conditions by an automated system, Tribo-Mate. It has been found that the increase in temperature increased the friction value at the boundary lubrication stage before the lubricant breakdown occurred. The increase in temperature, load and speed accelerated the lubricant breakdown and shortened the lubricant breakdown distances. An interactive friction model for predicting friction evolution and lubricant behaviours under varying contact conditions was established and the predictions showed good agreements with errors less than 6.8\% when compared with the experimental test results.

The detailed findings of this work could be summarised below:

![](https://cdn.mathpix.com/cropped/35c5b818-0eb5-4053-9148-968283315c0f-09.jpg?height=1262&width=1789&top_left_y=185&top_left_x=140)
Fig. 11. Evolutions of coefficient of friction, film thickness and thickness diminution rate under constant conditions and a) temperature decrease test, b) load increase test, c) speed increase test.

![](https://cdn.mathpix.com/cropped/35c5b818-0eb5-4053-9148-968283315c0f-09.jpg?height=799&width=1242&top_left_y=1602&top_left_x=411)
Fig. 12. An example of the instantaneous contact conditions in a warm forming process of AA7075.

![](https://cdn.mathpix.com/cropped/35c5b818-0eb5-4053-9148-968283315c0f-10.jpg?height=773&width=1245&top_left_y=189&top_left_x=409)
Fig. 13. Friction evolutions at varying and constant contact conditions, respectively.

1. The experimental results illustrate that the COF evolution consists of three stages at elevated temperatures. The first stage with the low friction value occurs when boundary lubrication is dominant. The second stage with the rapidly increasing coefficient of friction is the transition stage when the lubricant film thickness decreases to a critical value. The final plateau stage occurs with high friction values when the lubricant breakdown occurs and the two surfaces have intimate contact.
2. A temperature decrease from 300 °C to 200 °C caused a longer lubricant breakdown distance than that at constant temperature test of 300 °C with friction values decreasing from 0.24 to 0.22 before the lubricant breakdown occurred. A temperature increase caused a shorter lubricant breakdown distance with friction values increasing from 0.17 to 0.24.
3. The contact load effects on the friction values at the initial (boundary lubrication) stage was negligible. The abrupt increase of contact load caused the earlier onset of lubricant breakdown. The contact load increase from 5 N to 8 N reduces the lubricant breakdown distance by $21 \%$, while the load decrease gave rise to a $47 \%$ increase of the lubricant breakdown distance.
4. The sliding speed did not affect the COF at the low friction stage. The lubricant breakdown distance decreased with the increase of speed. As the speed increased from 50 mm/s to 80 mm/s, the lubricant breakdown distance decreased by approximately 40\% to 28 mm. As the speed decreased from 80 mm/s to 50 mm/s, the lubricant breakdown distance increased by 67\% to 30 mm.
5. As temperature, contact pressure and sliding speed varied continuously and simultaneously, the friction evolutions between the constant and varying conditions yielded a largest deviation of about 45.8\% in the friction values and a 50\% of increase in the lubricant breakdown distance, which demonstrated the significance of using the interactive friction model to provide accurate predictions under varying contact conditions.

## Credit authors

Xiao Yang: Experiments, Modelling and Draft writing. Xiaochuan Liu: Review and edit writing. Heli Liu: Experiments. Denis Politis: Review and Proofreading. David Leyvraz: Review. Liliang Wang: Review, Conceptualization and Supervision.

## Declaration of competing interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

## Acknowledgements

The research in this paper was supported by the China Scholarship Council with Grant CSC no. 201706230235. CSC is a national institution supporting excellent Chinese students to participate in MSc and PhD programs overseas.

## References

[1] Wang ZG. Tribological approaches for green metal forming. J Mater Process Technol 2004;151:223-7. https://doi.org/10.1016/J.JMATPROTEC.2004.04.046.
[2] Bay N, Olsson DD, Andreasen JL. Lubricant test methods for sheet metal forming. Tribol Int 2008;41:844-53. https://doi.org/10.1016/j.triboint.2007.11.017.
[3] Chowdhury MA, Khalil MK, Nuruzzaman DM, Rahaman ML. The effect of sliding speed and normal load on friction and wear property of aluminum. Int J Mech Mechatron Eng 2011;11:45-9.
[4] Wang W, Zhao Y, Wang Z, Hua M, Wei X. A study on variable friction model in sheet metal forming with advanced high strength steels. Tribol Int 2016;93:17-28. https://doi.org/10.1016/j.triboint.2015.09.011.
[5] Dohda K, Boher C, Rezai-Aria F, Mahayotsanun N. Tribology in metal forming at elevated temperatures. Friction 2015;3:1-27. https://doi.org/10.1007/s40544-015-0077-3.
[6] Karupannasamy DK, Hol J, de Rooij MB, Meinders T, Schipper DJ. A friction model for loading and reloading effects in deep drawing processes. Wear 2014;318:27-39. https://doi.org/10.1016/J.WEAR.2014.06.011.
[7] Mori K, Abe Y, Miyazawa S. Warm stamping of ultra-high strength steel sheets at comparatively low temperatures using rapid resistance heating. Int J Adv Manuf Technol 2020;108:3885-91. https://doi.org/10.1007/s00170-020-05642-x.
[8] Karbasian H, Tekkaya AE. A review on hot stamping. J Mater Process Technol 2010;210:2103-18.
[9] Wang Z, Dohda K, Haruyama Y. Effects of entraining velocity of lubricant and sliding velocity on friction behavior in stainless steel sheet rolling. Wear 2006;260: 249-57. https://doi.org/10.1016/j.wear.2005.04.029.
[10] Pereira MP, Yan W, Rolfe BF. Sliding distance, contact pressure and wear in sheet metal stamping. Wear 2010. https://doi.org/10.1016/j.wear.2010.01.020.
[11] Liu X, Ji K, Fakir O El, Fang H, Gharbi MM, Wang L. Determination of the interfacial heat transfer coefficient for a hot aluminium stamping process. J Mater Process Technol 2017;247:158-70. https://doi.org/10.1016/J.JMATPROTEC.2017.04.005.
[12] Fan XB, He Z Bin, Zhou WX, Yuan SJ. Formability and strengthening mechanism of solution treated Al-Mg-Si alloy sheet under hot stamping conditions. J Mater Process Technol 2016;228:179-85. https://doi.org/10.1016/j.jmatprotec.2015.10.016.

[13] Yang X, Hu Y, Zheng Y, Politis DJ, Liu X, Wang L. Experimental and modelling study of interaction between friction and galling under contact load change conditions. Tribol Int 2020 [Under Review].
[14] Venema J, Matthews DTA, Hazrati J, Wörmann J, van den Boogaard AH. Friction and wear mechanisms during hot stamping of AlSi coated press hardening steel. Wear 2017;380-381:137-45. https://doi.org/10.1016/j.wear.2017.03.014.
[15] Deng L, Mozgovoy S, Hardell J, Prakash B, Oldenburg M. Development of a tribological test programme based on press hardening simulations. Tribol Lett 2017. https://doi.org/10.1007/s11249-017-0826-8.
[16] Bowden FP, Bowden FP, Tabor D. The friction and lubrication of solids, vol. 1. Oxford university press; 2001.
[17] Bhushan B. Introduction to tribology. John Wiley \& Sons; 2013.
[18] Hu Y, Wang L, Politis DJ, Masen MA. Development of an interactive friction model for the prediction of lubricant breakdown behaviour during sliding wear. Tribol Int 2017. https://doi.org/10.1016/j.triboint.2016.11.005.
[19] Liu X, Yang X, Sun Y, Politis DJ, Mori K, Wang L. Characterization of thermomechanical boundary conditions of a martensitic steel for a FAST forming process. J Manuf Mater Process 2020;4:57. https://doi.org/10.3390/jmmp4020057.
[20] Komvopoulos K, Saka N, Suh NP. The mechanism of friction in boundary lubrication. J Tribol 1985;107:452-62. https://doi.org/10.1115/1.3261108.
[21] Wang A, Zheng Y, Liu J, Fakir O El, Masen M, Wang L. Knowledge Based Cloud FE simulation - data-driven material characterization guidelines for the hot stamping of aluminium alloys. J Phys Conf Ser 2016;734:32042. https://doi.org/10.1088/1742-6596/734/3/032042.
[22] Liu X, El Fakir O, Zheng Y, Gharbi MM, Wang L. Effect of tool coatings on the interfacial heat transfer coefficient in hot stamping of aluminium alloys under variable contact pressure conditions. Int J Heat Mass Tran 2019;137:74-83. https://doi.org/10.1016/J.IJHEATMASSTRANSFER.2019.03.087.
[23] Wang L, He Y, Zhou J, Duszczyk J. Effect of temperature on the frictional behaviour of an aluminium alloy sliding against steel during ball-on-disc tests. Tribol Int 2010;43:299-306. https://doi.org/10.1016/J.TRIBOINT.2009.06.009.
[24] Wilson WRD, Hsu TC, Huang XB. A realistic friction model for computer simulation of sheet metal forming processes. J Manuf Sci Eng Trans ASME 1995;117:202-9. https://doi.org/10.1115/1.2803295.
[25] Schipper DJ, de Gee AWJ. On the transitions in the lubrication of concentrated contacts. J Tribol 1995;117:250-4. https://doi.org/10.1115/1.2831238.
[26] Begelinger A, De Gee AWJ. Failure of thin film lubrication - a detailed study of the lubricant film breakdown mechanism. Wear 1982. https://doi.org/10.1016/0043-1648(82)90044-8.
[27] Czichos H. Failure criteria in thin film lubrication- the concept of a failure surface. Tribology 1974. https://doi.org/10.1016/0041-2678(74)90062-1.
[28] Ma G, Wang L, Gao H, Zhang J, Reddyhoff T. The friction coefficient evolution of a TiN coated contact during sliding wear. Appl Surf Sci 2015;345:109-15. https://doi.org/10.1016/j.apsusc.2015.03.156.
[29] Hu Y, Zheng Y, Politis DJ, Masen MA, Cui J, Wang L. Development of an interactive friction model to predict aluminum transfer in a pin-on-disc sliding system. Tribol Int 2019;130:216-28. https://doi.org/10.1016/j.triboint.2018.08.034.
[30] Wang L, He Y, Zhou J, Duszczyk J. Effect of temperature on the frictional behaviour of an aluminium alloy sliding against steel during ball-on-disc tests. Tribol Int 2010;43:299-306.
[31] Goddard J, Wilman H. A theory of friction and wear during the abrasion of metals. Wear 1962;5:114-35. https://doi.org/10.1016/0043-1648(62)90235-1.
[32] Seeton CJ. Viscosity-temperature correlation for liquids. In: STLE/ASME 2006 int. Jt. Tribol. Conf. American Society of Mechanical Engineers; 2006. p. 131-42.
[33] Wang A, El Fakir O, Liu J, Zhang Q, Zheng Y, Wang L. Multi-objective finite element simulations of a sheet metal-forming process via a cloud-based platform. Int J Adv Manuf Technol 2019;100:2753-65. https://doi.org/10.1007/s00170-018-2877-x.

[^0]:    * Corresponding author.
    E-mail address: liliang.wang@imperial.ac.uk (L. Wang).

