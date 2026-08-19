target temperatures and soaked for different periods of times, the specimens made of carbon steel, were moved onto a heat insulating die and compressed by a heat conducting punch. The temperature evolutions of the punch were measured and recorded using thermocouples embedded in the punch.

In order to identify the IHTC under specific experimental conditions, the measured temperature evolutions were compared with those inversely calculated with Beck's non-linear estimation method (Caron et al., 2014), or with those predicted by formulations using a 1D closed form method (Bai et al., 2012). Additionally, FE simulations (run in ABAQUS (Ji et al., 2014), PAM-STAMP (Liu et al., 2015) or DEFORM2D (Yukawa et al., 2014)) were applied to obtain simulated temperature evolutions to fit the experimental curves to identify the corresponding IHTC values.

Several studies have also investigated factors, e.g. contact pressure, tool material and lubricant, influencing the IHTC in metal forming processes. The power increasing trend of IHTC with contact pressure was obtained by Chang et al. (2016) for hot stamping of 22 MnB 5 steel. The IHTC was observed to increase from $0 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$ at 0 MPa to around $4.5 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$ at 30 MPa . The result of the exponential increasing trend of IHTC with contact pressure was observed in the study by Bai et al. (2012) of Ti-6Al-4 V and Yukawa et al. (2014) of carbon steel. The effect of tool material has been characterised in Chang et al.'s (2016) study, in which 22 MnB 5 blanks were stamped by AISI1045 steel and H13 tool steel respectively. The thermo-physical properties e.g. the thermal conductivity and specific heat capacity, of 1045 tool steel are higher than that of H13 tool steel, contributing to higher IHTC values. Hu et al. (2013) investigated the IHTC in hot stamping between 22 MnB 5 blanks and H11 tools, which have thermophysical property values, and subsequently IHTC values, between those of 1045 and H13 tool steels (Chang et al., 2016). Hu et al. (1998) also found that the peak IHTC of $2.5 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$ between Ti-6Al-4 V and Inconel alloy IN718 at 200 MPa , was less than that of $\mathrm{H} 13\left(20 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}\right)$ under the same conditions (Bai et al., 2012). The effect of lubricant has been investigated in Burte et al.'s (1990) study, in which graphite in water suspension was applied as a lubricant between aluminium alloy 20240 and H13 tool steel. The lubricant raised the IHTC values from 1.8 to $6 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$ at 0.85 MPa and from 9 to $18 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$ at 150 MPa . This positive effect of lubricant on the IHTC was also observed in the study by Foster et al. (2008) of AA6082 using four different lubricants and by Jain, (1990) for Al1100-O using $\mathrm{MoS}_{2}$ as a lubricant. However, the reverse effect was found in Zhang et al.'s (2010) research, in which glass was used as a lubricant.

The IHTC therefore depends on the contact pressure, the material of the contact bodies and the lubricant. In order to predict its value, Çetinkale and Fishenden, (1951)'s equation is widely used to estimate the general heat transfer coefficient, as shown in Eq. (1).

$$
\begin{equation*}
h=h_{g}+h_{c} \tag{1}
\end{equation*}
$$

where $h_{g}$ and $h_{c}$ are the heat transfer coefficients across the air gap and for the solid contact respectively.

Cooper and Yovanovich, (1969) identified a theoretical model for the IHTC between two contact solid bodies, as a power function of contact pressure, as shown in Eq. (2):

$$
\begin{equation*}
h=1.45 k \frac{\tan \theta}{\sigma}\left(\frac{p}{H}\right)^{0.985} \tag{2}
\end{equation*}
$$

where $k$ is the mean thermal conductivity of two contact bodies, $\theta$ is the mean of the absolute slope of the surface profile and $\sigma$ is the standard deviation of the profile heights.

As shown in Eq. (3), a power relationship between the IHTC and contact pressure was also developed as an empirical model by Shlykov et al. (1977):

$$
\begin{equation*}
h=8000 \bar{\lambda}\left(\frac{p}{C \sigma_{U}} K\right)^{0.86} \tag{3}
\end{equation*}
$$

where $\bar{\lambda}$ is the mean thermal conductivity of the two contact bodies, $\sigma_{U}$ is the ultimate strength of the test specimens, and $K$ and $C$ are model coefficients.

Differing from the models above, an exponential equation for IHTC as a function of contact pressure was developed by Yukawa et al. (2014), as shown in Eq. (4):

$$
\begin{equation*}
h=A(1-\exp (-B P)) \tag{4}
\end{equation*}
$$

where $A$ and $B$ are model constants determined by the least square method using the experimental results.

In order to characterise the IHTC values under a lubricated condition, an equation was built up by Wilson et al. (2004), as shown in Eq. (5):

$$
\begin{equation*}
h=\frac{1-A}{h_{f}} \frac{2 k_{f} k_{t} k_{w}}{2 k_{t} k_{w}-k_{w} k_{f}-k_{f} k_{t}} \tag{5}
\end{equation*}
$$

where $A$ is the contact area, $h_{f}$ is the applied lubricant thickness, and $k_{f}$, $k_{t}$ and $k_{w}$ are the thermal conductivities of the lubricant, tool and workpiece, respectively.

In the present research, a novel experimental facility was developed and applied to measure temperature evolutions of specimens and tools at different contact pressures under dry and lubricated conditions. The facility, designed with interchangeable components, streamlines the process by which the IHTC between different combinations of blank and tool materials could be determined. The IHTC value was subsequently found by utilising an inverse technique to fit the experimental data to simulated temperature evolutions obtained using the FE software PAMSTAMP. The capabilities of the IHTC test facility are demonstrated here by using it to investigate the effect of contact pressure and lubricant on the IHTC between a hot AA7075 specimen and three different tools. In addition, an IHTC model was developed as a function of contact pressure, tool material and lubricant to predict their effect on the IHTC, and validated using the results of hot stamping tests of a hemispherical dome shape and B pillar component.

## 2. Methodology

### 2.1. Design of the IHTC test facility

The IHTC test facility, a schematic for which is shown in Fig. 1, was developed to simulate hot stamping processes. Three sets of punches and dies were available, made from three different tool steels, i.e. H13, cast iron and P20, with contact surfaces of $50 \times 25 \mathrm{~mm}^{2}$. The average surface roughnesses of H13, cast iron and P20 tools were 980, 810 and 960 nm respectively, and were measured using White Light Interferometry equipment (Wyko NT9100). A specimen (No. 1 in Fig. 1) was screwed onto two blankholders (No. 4 in Fig. 1), and heated using direct resistance heating, then compressed against a fixed die (No. 3 in Fig. 1) by a moving punch (No. 2 in Fig. 1).

During these temperature/pressure-sensitive IHTC tests, the compressive loads were only able to reach the target value in 0.3 s after compression was initiated, with an approximate $20^{\circ} \mathrm{C}$ temperature loss in the samples; this was accounted for when comparing with the simulation results. Variable heating and cooling can be realised in both the test facility and in the simulations to represent particular processes, e.g. multi-paint cycles. Variable loads and stamping speeds can be controlled accurately, which can also be assigned in simulations to simulate different forming processes, e.g. warm/hot stamping.

The IHTC test facility provides a high stability and repeatability in the test results. Specifically, the specimens were controlled precisely to be compressed at the centre of the tools in each test with a tolerance of 0.1 mm , thus ensuring that the heat transfer between the specimen and

![](https://cdn.mathpix.com/cropped/2a02d6f3-829f-4f19-889b-56b1f63d26ac-2.jpg?height=865&width=868&top_left_y=208&top_left_x=129)
Fig. 1. Overall schematic structure of the IHTC test facility.

tools was in three dimensions and symmetric. Additionally, the specimens were heated by direct resistance heating from their respective tops and bottoms simultaneously, ensuring a high temperature homogeneity in the compression region. The measured temperature difference between the centre and edges of the compression regions in the specimens was within $5^{\circ} \mathrm{C}$. After heating, the IHTC test facility also does not necessitate the transfer of the specimens from a furnace to a press machine. Therefore, the punch, which only takes 0.05 s to compress the specimens at a speed of $400 \mathrm{~mm} / \mathrm{s}$, could be actuated immediately after heating, ensuring a negligible temperature loss from the specimens. The initial temperature of both the punch and die could also be considered as being equivalent when the compression process was started.

### 2.2. Experimental procedures

Prior to each test, a $120 \times 10 \times 2 \mathrm{~mm}^{3}$ AA7075 specimen supplied by AMAG Austria Metal AG in the T6 condition, was screwed onto the blankholders and positioned between the punch and die. The average surface roughness of the specimens was 340 nm and the composition of AA7075-T6 is shown in Table 1. In order to monitor temperature, pairs of thermocouples were embedded mid-thickness at the centre of the specimen, and at a distance of 3 mm below the centre of the tool (punch and die) contact surfaces respectively, and then connected to a data logger.

To represent a hot stamping process, the specimen was firstly heated by direct electrical resistance heating to its SHT temperature, $490^{\circ} \mathrm{C}$, at a heating rate of $10^{\circ} \mathrm{C} / \mathrm{s}$, while the temperature of the tools was maintained at room temperature. Once the target temperature was reached, the punch was instantly actuated to move towards the specimen at a speed of $400 \mathrm{~mm} / \mathrm{s}$ and compress it against the die at different pre-defined contact pressures. After the compression, the punch was

![](https://cdn.mathpix.com/cropped/2a02d6f3-829f-4f19-889b-56b1f63d26ac-2.jpg?height=858&width=828&top_left_y=206&top_left_x=1095)
Fig. 2. The FE model of the IHTC test facility in PAM-STAMP.

moved back to its initial position. The temperature evolutions of the specimen and the tools were recorded throughout the compression process. Prior to each test for the lubricated condition studies, greasebased graphite was applied with great care onto the tool surfaces only, which were thoroughly cleaned by using a chemical etchant after each test. The applied layer thickness of lubricant was precisely measured by using dedicated equipment.

### 2.3. FE simulation procedures

In order to simulate temperature evolutions of the specimen and tools, a FE model was built up in PAM-STAMP, which enables modelling of the interactions between mechanical and thermal fields (Karbasian and Tekkaya, 2010) and that can model heat transfer in 3D. The dimensions of the specimen and tools were the same as those used in the IHTC test facility, as shown in Fig. 2. The material properties of the specimen were generated by using empirical fittings as a function of temperature in Kelvin (Johnson, 2004), and the material properties of the three tools were based on a professional online material information resource (MatWeb, 2016), and are shown in Table 2.

Explicit quadrangle thermal shell elements with two degrees of freedom in temperature were used for the specimen to precisely represent the heat transfer mechanism that occurs during the hot stamping process. The selected element size, 2 mm , ensured that the temperature at the centre of the specimen could be captured accurately while providing a reasonable computational time. The same element type and size were selected for the majority of the regions on the tools, whilst explicit triangle thermal shell elements were used for some regions near circular edges. The total number of elements of the specimen (No. 1 in Fig. 2), punch/die (No. 2 \& 3 in Fig. 2), blankholders (No. 4 in Fig. 2) and screws (No. 5 in Fig. 2) were 240, 325, 634 and 216 respectively.
'Hotforming double action validation' was selected as the simulation

Table 1
The chemical composition of AA7075.
| Element | Si | Fe | Cu | Mn | Mg | Cr | Zn | Ti | Ti + Zr | Others Each | Al |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| $\mathrm{Wt} \%$ | 0.09 | 0.13 | 1.4 | 0.05 | 2.6 | 0.19 | 5.7 | 0.03 | 0.04 | 0.02 | Bal. |


Table 2
Material properties of the specimen and tools.
| Property | AA7075 |  |  |
| :--- | :--- | :--- | :--- |
| Young's modulus (MPa) | $-39.082 \mathrm{~T}+82532$ |  |  |
| Density ( $\mathrm{kg} / \mathrm{m}^{3}$ ) | $-6.7537 \mathrm{e}-05 \mathrm{~T}^{2}-0.15 \mathrm{~T}+2.8608 \mathrm{e} 03$ |  |  |
| Thermal conductivity ( $\mathrm{kW} / \mathrm{mK}$ ) | $-5.145 \mathrm{e}-08 \mathrm{~T}^{2}+1.368 \mathrm{e}-04 \mathrm{~T}$ + 0.085224 |  |  |
| Specific heat capacity (J/kgK) |  | $8.721 \mathrm{e}-07 \mathrm{~T}^{3}-1.4625 \mathrm{e}-03 \mathrm{~T}^{2}+1.2 \mathrm{~T}+608.3$ |  |
| Poisson's ratio (-) | $3.893 \mathrm{e}-08 \mathrm{~T}^{2}+0.000013505 \mathrm{~T}$ + 0.325165 |  |  |
|  |  |  |  |
| Thermal expansion (-) | $0.0216 \mathrm{~T}+16.499$ |  |  |
| Property | H13 | Cast iron | P20 |
| Young's modulus (GPa) | 210 | 101.4 | 205 |
| Density ( $\mathrm{kg} / \mathrm{m}^{3}$ ) | 7.8e03 | 7.15e03 | 7.85 e 03 |
| Thermal conductivity (kW/mK) | 0.0244 | 0.044 | 0.0315 |
| Specific heat capacity (J/kgK) | 460 | 465 | 473 |
| Poisson's ratio (-) | 0.3 | 0.29 | 0.285 |


process type in PAM-STAMP, and was composted of four individual stages; gravity, holding, stamping and quenching. All six degrees of freedom were restricted for the die, whilst all degrees of freedom, except for that in the z -direction (direction of punch motion), were restricted for the punch, blankholders and screws. The specimen was able to deform in all degrees of freedom. In the gravity and holding stages, the specimen was located and held by the blankholders and screws. In the subsequent stamping and quenching stages, the punch moved towards the specimen at the same speed as that in the experiments and compressed it against the die for 4 s .

Prior to the quenching stage, the actual measured temperature from the experiments at the two ends of the specimen was $310^{\circ} \mathrm{C}$, due to the heat transfer to the blankholders, whilst the temperature distribution within the compression region was uniform. Therefore, the initial temperature of the tools, the two ends of the specimen and the centre of the specimen were set as 25,310 and $490^{\circ} \mathrm{C}$ respectively. Differing from the experiments, a different constant IHTC value was assigned for each simulation to eliminate the effect of contact pressure on the temperature evolution. The temperature evolutions, at identical locations to those in the experiments, were then plotted and compared with the experimental temperature evolutions. The experimental and simulated curves with the best agreement indicated that the IHTC assigned
in that simulation was the corresponding value at the selected experimental conditions.

Fig. 3 shows a comparison of the temperature evolutions obtained from a simulation assigned an IHTC value of $9.2 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$ and from an experiment with a contact pressure of 3 MPa under dry conditions, using cast iron tools. From the results, it was found that the temperature of the specimen dropped drastically in the first 2 s , while the punch temperature increased gradually with time. The experimental temperature evolutions agree well with the simulated curves, which indicates that the IHTC value is $9.2 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$ when the contact pressure is 3 MPa under dry conditions, using cast iron tools.

## 3. Results and discussion

### 3.1. Effect of contact pressure on IHTC

As shown in Fig. 4, when H13 was used as the tool material, the IHTC increase considerably from $0.7 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$ to approximately $8.2 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$ when the contact pressure increases from 0 to 7 MPa under dry conditions, followed by a gentle increase as the contact pressure increases from 7 to 10 MPa . When the contact pressure is higher than 13 MPa , a plateau of the IHTC is observed, with value of approximately $8.6 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$. The variation of the IHTC values can be explained by the evolutions of real contact area at different contact pressures. The real contact area between the specimen and tools is usually much less than the apparent contact area, and increases with increasing contact pressure due to the variation of the specimen surface condition (Buchner et al., 2009). This is beneficial for the interfacial heat transfer between the specimen and the tools, leading to an increase in the IHTC with increasing contact pressure.

In order to characterise the relationship between the real contact area and contact pressure, the average surface roughness of the H13 tools and the specimens were measured after the IHTC tests. The average surface roughness of the H13 tools remained stable at 980 nm throughout the experiments, whilst for the specimen this value varied with the contact pressure. The strength of H13 within the temperature range used in the experiments was much larger than that of AA7075 at elevated temperatures. As a result, the surfaces of the specimens were deformed by the tools during the hot stamping processes and thus the surface roughness of the specimens increased correspondingly. Therefore, the real contact area was growing due to the fact that the two contact surfaces were increasingly meshed together. As shown in

![](https://cdn.mathpix.com/cropped/2a02d6f3-829f-4f19-889b-56b1f63d26ac-3.jpg?height=778&width=1086&top_left_y=1767&top_left_x=488)
Fig. 3. The comparison between experimental and simulated temperature evolutions at a contact pressure of 3 MPa under dry conditions, using cast iron tools.

![](https://cdn.mathpix.com/cropped/2a02d6f3-829f-4f19-889b-56b1f63d26ac-4.jpg?height=845&width=1175&top_left_y=193&top_left_x=447)
Fig. 7. The IHTC evolutions with applied lubricant layer thickness using cast iron tools, at contact pressures of 5 and 10 MPa .

using the graphite lubricant. Therefore, the application of a lubricant with a higher thermal conductivity would result in higher IHTC values and thus a shorter required quenching time for hot stamping processes. The critical contact pressure and friction would thereby be reduced, extending the tool life. Excessive lubricant could also be prevented from being applied. Overall, these features would be beneficial to the promotion of cost efficiency in hot stamping processes.

## 4. Development of a mechanism based IHTC model

The results obtained using the IHTC test facility at different contact pressures and for different tool materials under both dry and lubricated conditions were used to develop a definition of the overall IHTC between the specimen and tools, derived from the null-pressure IHTC $h_{a}$, solid-contact IHTC $h_{c}$ and lubricant-contact IHTC $h_{l}$, as shown in Eq. (6).

$$
\begin{equation*}
h=h_{a}+h_{c}+h_{l} \tag{6}
\end{equation*}
$$

where $h_{a}$ represents the heat transfer across the air gap between the specimen and tools with zero pressure, and typically has a low value, $h_{c}$ represents the contact under pressure between two solid surfaces, and $h_{l}$ represents the application of lubricant between two solid surfaces. Eq. (6) is developed based on Çetinkale and Fishenden's, (1951) equation, which is widely used as a general model to estimate the general heat transfer coefficient. It was found that the null-pressure IHTC $h_{a}$ did not play an important role in the present research since the initial amount of heat transfer between the contact surfaces was negligible according to the experimental observations. Once a contact pressure was applied, the heat transfer between the contact surfaces was increased significantly under both dry and lubricated conditions, thus the overall IHTC was mainly characterised by the solid-contact IHTC $h_{c}$ and the lubricant-contact IHTC $h_{l}$. Therefore, it was reasonable to assume a constant value for the null-pressure IHTC $h_{a}$ of approximately $0.8 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$, which was determined by running IHTC tests under dry conditions with zero contact pressure. The solid-contact IHTC $h_{c}$, induced by the applied contact pressure, was modelled by Eq. (7):

$$
\begin{equation*}
h_{c}=\alpha \frac{K_{s t} N_{P}}{R} \tag{7}
\end{equation*}
$$

where $\alpha$ is a model parameter, $K_{s t}$ is the harmonic mean thermal
conductivity of the contact solids, $R$ is the root mean square of surface roughness of the contact solids and $N_{P}$ is a pressure dependent parameter. The solid-contact IHTC $h_{c}$ depends on the thermal conductivity of the two contact solids and the contact surfaces. Eq. (7) therefore was developed combining the physical mechanism of the heat transfer between the contact surfaces and the theory of Cooper and Yovanovich, (1969). The amount of heat transfer was considered to increase with the increasing thermal conductivity of both the specimen and tools. The solid-contact IHTC $h_{c}$ is thus correlated positively with the harmonic mean thermal conductivity $K_{s t}$. In order to simplify the model, the harmonic mean thermal conductivity $K_{s t}$ shown in Eq. (8) was determined from the average thermal conductivities of the specimen $k_{s}$ and tools $k_{t}$, in the temperature range used in the experiments:

$$
\begin{equation*}
K_{s t}=\frac{2}{k_{s}^{-1}+k_{t}^{-1}} \tag{8}
\end{equation*}
$$

Meanwhile, the amount of heat transfer reduced with the decreasing real contact area between the specimen and tools, which was associated with a higher initial surface roughness of the contact surfaces. Hence a negative relationship between the solid-contact IHTC $h_{c}$ and the root mean square (r.m.s.) of the initial surface roughness of the specimen and tools $R$ was considered. The r.m.s. surface roughness was determined by the average surface roughness of the specimen $R_{s}$ and tools $R_{t}$, as shown in Eq. (9):

$$
\begin{equation*}
R=\sqrt{R_{s}{ }^{2}+R_{t}{ }^{2}} \tag{9}
\end{equation*}
$$

The heat transfer was more rapid when the contact pressure increased, as the real contact area between the contact surfaces was increased. Hence this results in a positive correlation between the solidcontact IHTC $h_{c}$ and the pressure dependent parameter $N_{P}$, which can be represented by the following exponential-law equation, Eq. (10):

$$
\begin{equation*}
N_{P}=1-\exp \left(-\lambda \frac{P}{\sigma_{U}}\right) \tag{10}
\end{equation*}
$$

where $\lambda$ is a model parameter, $P$ is the contact pressure between the specimen and tools, and $\sigma_{U}$ is the ultimate strength of AA7075 at $490^{\circ} \mathrm{C}$. In order to increase the IHTC values, a contact pressure could be applied, deforming the asperities on the specimen surface and thus enlarging the real contact area between the specimen and tools. The

Table 3
Material constants and model parameters of IHTC model.
| $k_{s}(\mathrm{~kW} / \mathrm{mK})$ | $k_{t}$ (H13) | $k_{\mathrm{t}}$ (Cast iron) | $k_{t}$ (P20) | $k_{l}$ (Lubricant) |
| :--- | :--- | :--- | :--- | :--- |
| 0.14 | 0.0244 | 0.044 | 0.0315 | 0.024 |
| $R_{s}(\mathrm{~m})$ | $R_{t}$ (H13) | $R_{t}$ (Cast iron) | $R_{t}$ (P20) | $h_{a}\left(\mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}\right)$ |
| $3.4 \mathrm{e}-7$ | $9.8 \mathrm{e}-7$ | $8.1 \mathrm{e}-7$ | $9.6 \mathrm{e}-7$ | 0.8 |
| $\sigma_{U}$ | $\alpha(-)$ | $\lambda(-)$ | $\beta(-)$ | $\gamma\left(\mathrm{m}^{-1}\right)$ |
| 21 | $2.01 \mathrm{e}-4$ | 6.05 | $1.1 \mathrm{e}-4$ | 2e5 |


ratio of the applied contact pressure to the ultimate strength (Cooper et al., 1969) (hardness (Shlykov et al., 1977)) of a specimen is equal to the ratio of the real contact area to the apparent contact area. Eq. (10) therefore represents the deformation mechanism of the asperities on the specimen surface.

When the lubricant was applied, the lubricant-contact IHTC $h_{l}$ also contributed to the overall IHTC value, which was modelled by Eq. (11):

$$
\begin{equation*}
h_{l}=\beta \frac{K_{s t l} N_{L}}{R} \tag{11}
\end{equation*}
$$

where $\beta$ is a model parameter, $K_{\text {stl }}$ is the harmonic mean thermal conductivity of the three contacting materials, i.e. the tools, lubricant and specimen, $R$ is the root mean square of the surface roughness of the two contact solids and $N_{L}$ is a layer thickness dependent parameter. When a lubricant layer was introduced between the two contact solids, the heat flowed through these three contacting materials; hence the harmonic mean thermal conductivity $K_{s t l}$ is correlated positively with $h_{l}$. The harmonic mean thermal conductivity was calculated as shown in Eq. (12).

$$
\begin{equation*}
K_{s t l}=\frac{3}{k_{s}^{-1}+k_{t}^{-1}+k_{l}^{-1}} \tag{12}
\end{equation*}
$$

where $k_{s}, k_{t}$ and $k_{l}$ are the average thermal conductivities of the specimen, tools and grease-based graphite lubricant respectively.

The applied lubricant layer thickness is an influential factor on the lubricant-contact IHTC $h_{l}$, which can be represented by the following exponential-law equation, Eq. (13):

$$
\begin{equation*}
N_{L}=1-\exp (-\gamma \delta) \tag{13}
\end{equation*}
$$

where $\gamma$ is a model parameter and $\delta$ is the applied lubricant layer thickness.

The IHTC model was calibrated using the experimental data from the tests carried out under dry and lubricated conditions using two different tool materials. Table 3 lists the identified material constants and certain model parameters.

In order to verify the predicted results generated by the IHTC model, the material constants for P20 were used to predict the evolution of the IHTC with contact pressure under both dry and lubricated 0.015 mm layer thickness) conditions, assuming that P20 was used as the tool material, as shown in Fig. 8. These IHTC evolutions, rather than constant values, were then implemented in the FE simulation to simulate temperature evolutions using P20 tools with a contact pressure of 3 MPa under dry conditions, and 13 MPa under lubricated conditions with a layer thickness value of 0.015 mm . Meanwhile, two new tests were conducted under the same conditions as those of the simulations using the IHTC test facility. As shown in Fig. 9, it is evident that the simulated temperature evolutions were in close agreement with the experimental curves, indicating that when using P20 tools, the IHTC values at 3 MPa under dry conditions and at 13 MPa under lubricated conditions with a layer thickness value of 0.015 mm , are 6.7 and $14.5 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$ respectively.

Therefore, the IHTC model developed in the present research enables the prediction of IHTC evolutions as a function of contact pressure, tool material and lubrication. When using certain materials

![](https://cdn.mathpix.com/cropped/2a02d6f3-829f-4f19-889b-56b1f63d26ac-5.jpg?height=771&width=1081&top_left_y=1774&top_left_x=493)
Fig. 8. The predicted IHTC evolutions with contact pressure using P20 tools under dry and lubricated conditions.

