# Experimental and modeling study of the interfacial and convective heat transfer coefficients of 6061 aluminum alloy in hot gas forming 

Jiatian Lin ${ }^{\mathbf{1}}$ • Dechong Li ${ }^{\mathbf{1}}$ • Kailun Zheng ${ }^{\mathbf{1}}$ • Xiaochuan Liu ${ }^{\mathbf{2}}$

Received: 27 May 2024 / Accepted: 18 September 2024 / Published online: 4 October 2024
© The Author(s), under exclusive licence to Springer-Verlag London Ltd., part of Springer Nature 2024


#### Abstract

The heat transfer coefficient, including interfacial heat transfer coefficient (IHTC) and convective heat transfer coefficient (CHTC), plays a pivotal role in the thermal dynamics of hot gas forming processes. This parameter can determine the temperature field, thereby affecting the deformation and mechanical properties of the material to improve productivity. In this paper, we present an innovative experimental apparatus designed to measure the temperature evolutions of the aluminum specimen and the die during the hot gas forming processes. This apparatus is capable of simultaneously measuring IHTC and CHTC. Using the inverse finite element method, the simulated temperature histories are matched with empirical data and the best-fit values are adopted as indicative of IHTC and CHTC. This study identified the effects of contact pressure and die temperature on IHTC, as well as the impact of gas pressure on CHTC. In addition, a predictive model was developed to forecast the IHTC and CHTC at varying contact pressures and die temperatures with a prediction accuracy surpassing 0.95. By leveraging the predictive model presented in this paper, users can modulate contact pressure and die temperature based on specific production needs to achieve a targeted temperature profile. This method offers enhanced precision in managing the temperature field of the workpiece during hot gas forming experiments, thereby refining the temperature distribution. Moreover, it optimizes the formability and microstructural attributes of the material, ultimately leading to improved mechanical characteristics.


Keywords AA6061 ⋅ Hot gas forming ⋅ FE simulation ⋅ Interfacial heat transfer coefficient (IHTC) • Convective heat transfer coefficient (CHTC) • Predictive model

## 1 Introduction

Hot gas forming technology is a process that heats the aluminum alloy to a certain temperature and then inflates the blank to bulge into the same shape as the die cavity, resulting in structural parts with the desired shape and performance [1]. By increasing the forming temperature, enhancing the plasticity of aluminum alloy and adjusting the process parameters are performed to control the strain and strain rate hardening during the forming of high-strength aluminum alloys, as well as achieve a uniform wall thickness,

[^0]microstructure and properties of the formed parts [2, 3]. Hot gas forming technology of aluminum alloys can be widely used in the automotive, aerospace, and electronics industries [4, 5]. A hot gas forming process of a material is typically accompanied by heat conduction of the workpiece, contact heat exchange between the die and workpiece, convective heat exchange with air, and thermal radiation between the die and workpiece. These heat transfer processes affect the temperature field. The more uniform the distribution of the temperature field, the better the plastic forming properties and microstructural performance of the material. This enables the material undergoing thermal expansion to achieve better mechanical properties. Adjusting the temperature, air pressure loading rate, and other process parameters will result in better temperature control of the workpiece to achieve the ideal temperature field. This helps to reduce forming defects and allow complex aluminum alloy parts to be formed with higher precision [1, 6, 7].

The heat transfer coefficient determines the temperature evolution of aluminum alloys and significantly affects the
post-form geometries and properties in hot gas forming. The heat transfer coefficient includes the interfacial heat transfer coefficient (IHTC) between hot aluminum alloys and forming die, and the convective heat transfer coefficient (CHTC). The interfacial heat transfer coefficient refers to the heat exchanged per unit of area per unit of time between solids, reflecting the heat transfer capacity between contact surfaces. The convective heat transfer coefficient is a physical quantity that refers to the direct fluid-solid contact. It represents the heat transfer caused by temperature differences between the fluid and the solid. Obtaining precise simulation results for the heat transfer coefficient is necessary as heat transfer is related to the object's cooling, and involves many complex factors [8].

To determine the IHTC under different conditions, Caron et al. [9, 10] used Beck's non-linear method to estimate the IHTC based on the measured temperature data, while Bai et al. [11] predicted the IHTC using the 1D heat transfer equation from closed-form expression. On the other hand, Jarrar et al. [12] and Yukawa et al. [13] used PAM-STAMP and DEFORM-2D to simulate the temperature evolutions. They fitted the experimental curves to determine the corresponding IHTC values.

In a study to investigate the factors influencing the IHTC during the metal forming process, Chang et al. [14] found that the IHTC increased with rising contact pressure, growing from $0 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$ at 0 MPa to $4.5 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$ at 30 MPa during a hot stamping process of 22MnB5 steel. Meanwhile, Bai et al. [11] and Yukawa et al. [13] concluded that the IHTC increased exponentially with rising contact pressure in their respective studies on the hot stamping processes of Ti-6Al-4 V and carbon steel. Different tool materials also affect the IHTC. In a study of Chang et al. [14], 22MnB5 billets were stamped using AISI1045 steel and H13 tool steel, with AISI1045 steel resulting in larger IHTC values due to higher thermal conductivity and specific heat capacity. In addition, Hu et al. [15] also found that the IHTC values using 22MnB5 billet and H11 tool steel were intermediate to the IHTC values between AISI1045 steel and H13 tool steel. Hu et al. [16] further noted that under the same conditions, Ti-6Al-4 V and Inconel alloy 718 had lower IHTC values than Ti-6Al-4 V and H13. Examining the effects of lubricant on the IHTC, Burte et al. [17] deduced that using graphite as a lubricant in aqueous suspension showed a positive correlation, increasing the IHTC value from 1.8 to 6 kW/m2K at 0.85 MPa. However, Zhang et al. [18] found a negative correlation between a glass lubricant and the IHTC. Moreover, Zhao et al. [19] found that the AL-278 lubricant also had a thermal insulation effect, and unilateral contact led to an increase in the IHTC throughout the process.

Some researchers designed various devices to establish IHTC patterns during the thermal forming process. Ying et al. [20] set up a cylindrical model experimental apparatus to study the transient heat transfer characteristics of 7075-T6 aluminum alloy during the hot gas forming process. They obtained the transient IHTC under different contact pressures, surface roughness, and lubrication conditions. In addition, Liu et al. [21] developed a new type of interface heat transfer experimental apparatus. They recorded changes in temperature during the stamping process and determined the IHTC value that best fits the experimental conditions after comparing the temperature evolution from finite element simulations with the experimental data. IHTC values were obtained under different contact pressures and die materials. Khandkar et al. [22] developed a vertical compression apparatus. Moving a carbon steel sample to an adiabatic die and compressing it with a thermal conductive punch, thermocouples record the temperature data of the punch and sample. In addition, using zirconia as the mold material can reduce heat loss from the sample and measure the IHTC.

There is a lack of studies on the impact of die temperature on the IHTC, as current research focuses on the effect of contact pressure, lubricants, and tool materials on the IHTC. Research on the effects of the CHTC on thermal forming is spare, and a lack of experimental equipment that can simultaneously measure the IHTC and CHTC. This paper has developed an interface heat transfer experimental apparatus and a hollow upper die device that enables heat exchange between air and the billet to measure the IHTC and CHTC. A finite element simulation of heat transfer was established through heat transfer experiments under different contact pressures and die temperatures. The heat transfer coefficients under various conditions were obtained using the inverse finite element method. Models for the heat transfer coefficient during hot gas forming and heat transfer coefficient of gas pressure were established based on the heat transfer mechanisms, thereby enabling the prediction of the IHTC and CHTC values under different conditions.

## 2 Experimental procedures and finite element simulations

With two different sets of die, this paper used the inverse finite element method to determine the IHTC between AA6061 and die, and the CHTC between AA6061 and air during hot gas forming. The experimental temperature evolution data obtained from the hot gas forming experiments were compared with the corresponding temperature data under specific temperature and pressure conditions in the FE simulation. The values that best fit the data were used as the IHTC between AA6061 and H13 die under these conditions.

The CHTC is measured after obtaining the IHTC between AA6061 and the die. Replacing the upper die with a hollow die and the lower die with a solid steel die, the experiment is carried out in the same way to obtain the temperature
data. The simulation die is also replaced with the second set of dies in the simulation software, and the IHTC between AA6061 and solid H13 die from the first set of die experiments was entered to obtain the temperature evolution between the hollow die and AA6061. Comparing the experimental data with the simulation data, the results were fairly reliable when the R value was not less than 0.95 , and the coefficient value at this point was considered as the CHTC between AA6061 and air under the current conditions.

### 2.1 Experimental equipment

A piece of specialized testing equipment was used, including a heating device, a press, and a temperature data acquisition system. The press had a nominal force of 3150 kN, drawing force of 2000 kN, blank holding force of 1150 kN, and a pressure error control within ±0.1 kN. The data acquisition system measured the temperature range from - 30 to 1000 °C with an accuracy of ±0.3 °C. The experimental temperature evolution of aluminum alloy and tool steel was recorded under different contact pressures and die temperatures.

The heating system comprised a furnace, temperature control box, and ceramic heating jacket. The temperature control box of the furnace was precise, with a temperature error of ±1 °C. The ceramic heating jacket was used to heat the die, and temperature control was achieved by adjusting the heating power through the temperature control box.

To simultaneously measure the IHTC and CHTC, this paper designed two sets of upper dies. The first set of die simulated the interfacial heat transfer between the billet and die, with both upper and lower dies made of solid steel to measure the IHTC. The second set retained the solid steel lower die, but the upper mold was replaced with a hollow die with air holes to facilitate the convective heat transfer between the plate material and air to measure the CHTC. Simply switching the upper die in the equipment allowed the simultaneous measurement of the IHTC and CHTC during the experiment. Figure 1 shows the schematic diagram of the convective heat transfer experimental equipment, which mainly consists of a heating jacket, an insulating plate, and upper and lower dies.

During the experimental process, the die was first heated to the preset temperature using a heating jacket. After heating to the target temperature, the plate material was placed on the lower die. Insulation boards were used between the upper and lower dies, as well as the die frame to prevent the die from transferring heat to the press, which could destabilize the die temperature. A high-pressure air source was connected to the die frame via air tubes, with holes on the side of the frame for air to reach the die cavity. To prevent air leakage caused by gaps between the insulation board, die, and frame, rubber gaskets were placed between these components during installation. The press was used to move the upper die downward, thereby applying pressure to the sheet. After the upper and lower dies were clamped, the sheet underwent sufficient convective heat exchange with the air. Thermocouples were installed at distances of 1.5 mm, 3 mm, and 4.5 mm from the surface of the lower die to obtain the experimental temperature curves under different conditions and measure the real-time die temperature changes during the experiment.

### 2.2 Materials and test scheme

Supplied by Chongqing Southwest Aluminum (Group) Co. Ltd., AA6061 T6 was used as the test material and its chemical composition is shown in Table 1.

The thermophysical parameters of AA6061 and H13 were not constant, including the thermal conductivity, Young's modulus, and specific heat capacity. Temperature can affect the parameters, with the thermophysical data shown in Tables 2 and 3.

This paper's test scheme explored the changing laws of IHTC and the CHTC under different contact pressures and die temperatures, as shown in Table 4. Three temperatures of room temperature, 160 °C, and 200 °C were selected

Fig. 1 Schematic diagram of the experimental equipment
![](https://cdn.mathpix.com/cropped/212defdc-725e-4542-8ac4-d90bcbc9fbdf-03.jpg?height=573&width=1258&top_left_y=1914&top_left_x=635)

Table 1 Chemical composition of AA6061 aluminum alloy
| Element | Si | Fe | Cu | Mn | Mg | Cr | Zn |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Wt.\% | 0.4-0.8 | 0.7 | 0.15-0.4 | 0.15 | 0.8-1.2 | 0.04-0.35 | 0.25 |


Table 2 Numerical table of AA6061 thermal physical properties [23-25]
| Temperature (°C) | 25 | 100 | 200 | 300 | 400 | 500 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Thermal conductivity $\left(\mathrm{W} / \mathrm{m}^{\circ} \mathrm{C}\right)$ | 170 | 180 | 192 | 207 | 220 | 225 |
| Young's modulus (GPa) | 70.9 | 67.7 | 63.5 | 59.2 | 54.2 | 48.8 |
| Specific heat capacity (J/kgK) | 896 | 978 | 1028 | 1078 | 1100 | 1150 |


Table 3 Numerical table of H13 thermophysical properties [26]
| Temperature (°C) | 25 | 100 | 200 | 300 | 400 | 500 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Thermal conductivity $\left(\mathrm{W} / \mathrm{m}^{\circ} \mathrm{C}\right)$ | 50 | 46 | 43 | 40 | 35 | 31 |
| Young's modulus (GPa) | 210 | 190 | 180 | 165 | 150 | 130 |
| Specific heat capacity (J/kgK) | 450 | 460 | 465 | 470 | 475 | 699 |


Table 4 Test scheme
| Test group | Die temperature (°C) | Pressure (MPa) | Pressure mode |
| :--- | :--- | :--- | :--- |
| 1 | RT | 1 | Die pressing |
| 2 | RT | 3 | Die pressing |
| 3 | RT | 5 | Die pressing |
| 4 | RT | 10 | Die pressing |
| 5 | RT | 15 | Die pressing |
| 6 | 160 | 1 | Die pressing |
| 7 | 160 | 3 | Die pressing |
| 8 | 160 | 5 | Die pressing |
| 9 | 160 | 10 | Die pressing |
| 10 | 160 | 15 | Die pressing |
| 11 | 200 | 1 | Die pressing |
| 12 | 200 | 3 | Die pressing |
| 13 | 200 | 5 | Die pressing |
| 14 | 200 | 10 | Die pressing |
| 15 | 200 | 15 | Die pressing |
| 16 | 160 | 1 | Gas pressure |
| 17 | 160 | 3 | Gas pressure |
| 18 | 160 | 5 | Gas pressure |
| 19 | 160 | 10 | Gas pressure |
| 20 | 160 | 15 | Gas pressure |


based on the commonly used die temperatures that affect the heat transfer coefficient [18]. Since the common range of pressure for hot bulging is between 1 and 15 MPa, five contact pressures of 1, 3, 5, 10, and 15 MPa were chosen for their impact on the IHTC and CHTC [27]. The experiments were conducted using both die pressing and gas pressing methods.

Fig. 2 FE model. a Pressure by die. b Pressure by gas
![](https://cdn.mathpix.com/cropped/212defdc-725e-4542-8ac4-d90bcbc9fbdf-05.jpg?height=1247&width=1099&top_left_y=191&top_left_x=798)

A gas pressure heat transfer model was used to simulate the CHTC, as shown in Fig. 2b. The solid steel die was fixed as the bottom die, while the upper die was removed. The gas pressure was set to pressurize AA6061. Using the IHTC determined from the stamping heat transfer model, the contact heat transfer coefficient was set between the lower surface of AA6061 and surface of the bottom die. Furthermore, there was heat exchange on the upper surface of AA6061, defining and selecting built-in coefficients with the film cooling effectiveness as a variable for simulation, while the ambient temperature varied with the die temperature. After pressurization, the nodal temperature NT11 was used to obtain the simulated temperature data of AA6061 under corresponding conditions. The CHTC between AA6061 and air was then determined through the inverse finite element method.

## 3 Results and discussion

### 3.1 Effect of contact pressure on IHTC of AA6061

In the hot gas forming experiments, the temperature variation curves of AA6061 at die temperatures of room temperature, $160^{\circ} \mathrm{C}$, and $200^{\circ} \mathrm{C}$ were derived under contact pressures of 1, 3, 5, 10, and 15 MPa. Using the die temperature at room temperature as an example, the temperature data at pressures of 1, 10, and 15 MPa were selected. The simulated temperature curves were obtained using finite element software, and the experimental data were fitted with the simulation data, as shown in Fig. 3.

The results showed that the initial cooling rate of AA6061 was relatively fast, reaching approximately 75 °C/s, 100 °C/s, and 125 °C/s within 2 s at pressures of 1, 10, and 15 MPa, respectively. The cooling rate decreased and gradually stabilized after 2 s, with the temperature eventually stabilizing around 110 °C, 77 °C, and 75 °C. After making adjustments using the inverse finite element method, good consistency was achieved between the experimental temperature data and simulated temperature data at the three pressures, with reliability $R$ values reaching $0.95,0.98$, and 0.97, respectively. Thus, the IHTC of AA6061 under room temperature conditions was respectively determined to be $1.4 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}, 2.6 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$, and $2.8 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$ at contact pressures of $1 \mathrm{MPa}, 10 \mathrm{MPa}$, and 15 MPa .

To analyze the effect of contact pressure on the IHTC of AA6061, the IHTC obtained for different contact pressures

Fig. 3 Comparison between the experimental and simulated temperatures of AA6061 contacted by H13 dies at 1, 10, and 15 MPa
![](https://cdn.mathpix.com/cropped/212defdc-725e-4542-8ac4-d90bcbc9fbdf-06.jpg?height=831&width=1095&top_left_y=197&top_left_x=800)

through the inverse finite element method at a die temperature of 160 °C were compared with the results predicted by a stamping heat transfer coefficient prediction model, as shown in Fig. 4.

As Fig. 4 illustrates, the IHTC increased when contact pressure rose. There was a noticeable rise in IHTC value when contact pressure was less than 5 MPa, expanding 50\% to $1.4 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$ at 1 MPa and $2.1 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$ at 5 MPa .

This is because the load directly affected the extent of surface deformation. When the pressure rose, the elastic deformation of the surface protrusions caused an increase in contact area, intensifying heat exchange on the surface. The true contact area between the workpiece and die was often much smaller than the deformed contact area. Moreover, the true contact area increased with rising contact pressure due to the elastic and plastic deformation of rough surfaces [25]. The enlarged true contact area facilitated the heat transfer from the workpiece to the die interface, hence the IHTC value drastically increased with the rise in the initial contact pressure.

Subsequently, the rate of increase in the IHTC value slowed down when the contact pressure rose. When the contact pressure rose from 5 to 15 MPa, the IHTC value increased by only $0.1 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$ and stabilized at 2.2 kW/ $\mathrm{m}^{2} \mathrm{~K}$. The contact surface protrusions underwent plastic deformation that led to work hardening when the pressure was elevated. This further resulted in surface hardness increase and decrease in contact area. Therefore, the sensitivity of the interfacial heat transfer coefficient to load decreased at higher pressures. The large contact area ratio (ratio of actual contact area to deformed contact area) might be the reason for the stable IHTC values. To summarize, IHTC began to increase with increasing pressure and then leveled off. If a rapid cooling rate of AA6061 is preferred in the forming process, using the maximum heat transfer between AA6061 and the die can ensure a higher IHTC value while maintaining a pressure of 5 MPa. Conversely, the pressure can be lowered to around 2 MPa if a slower cooling rate is required.

### 3.2 Effect of die temperature on the IHTC of AA6061

The IHTC values of AA6061 can be derived at three different die temperatures of room temperature, $160^{\circ} \mathrm{C}$, and 200 °C with pressure variation through the experiments and inverse finite element method. The IHTC values at the three die temperatures were compared with the heat transfer coefficient model predictions, as shown in Fig. 5.

Figure 5 illustrates how the IHTC value decreases with an increase in die temperature at the same contact pressure. At room temperature, 160 °C, and 200 °C, the IHTC value decreased with a difference of approximately $0.25 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$ when the pressure was less than 5 MPa. The difference in IHTC values across the three die temperatures reached $0.5 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$ when the pressure exceeded 5 MPa. The difference in IHTC values then stabilized.

This was because the initial temperature of AA6061 was 500 °C, resulting in varying degrees of temperature differences with the die. There was a significant temperature gradient across the interface between them, known as the thermal boundary layer [29]. The thickness of the thermal boundary layer affected its temperature distribution, which in turn influenced the temperature gradient. The larger the temperature difference between AA6061 and the die, the

Fig. 4 Experimental and modeling IHTC of AA6061 as a function of pressure
![](https://cdn.mathpix.com/cropped/212defdc-725e-4542-8ac4-d90bcbc9fbdf-07.jpg?height=820&width=1099&top_left_y=195&top_left_x=798)

greater the temperature gradient, and the faster the heat transfer, resulting in a higher IHTC value. Under the same pressure, the IHTC decreased progressively when the die temperature transitioned from room temperature to 160 °C and 200 °C. At lower pressures, the differences in die temperatures had a minimal impact on the degree of deformation in the slight protrusions on the surface between AA6061 and the die. The elastic deformation of these surface protrusions led to a similar increase in the contact area, resulting in similar heat exchanges between AA6061 and die. Consequently, there was a relatively small difference in the IHTC values between AA6061 and die at approximately $0.25 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$. The surface heat exchange intensified when the pressure continued to rise, enough to enhance the heat exchange between AA6061 and die at different die temperatures. Hence, the difference in the IHTC values between room temperature, $160^{\circ} \mathrm{C}$, and $200^{\circ} \mathrm{C}$ reached $0.5 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$ under the same pressure.

Fig. 5 The experimental and predicted at different die temperatures
![](https://cdn.mathpix.com/cropped/212defdc-725e-4542-8ac4-d90bcbc9fbdf-07.jpg?height=876&width=1092&top_left_y=1616&top_left_x=803)

### 3.3 Effect of gas pressure on the CHTC of AA6061

Using a second set of upper die, the solid upper die was replaced with a hollow one for gas pressing. Compared to die pressing, gas pressure had a more enclosed heat transfer space, and the ambient temperature underwent significant changes during the experiment. An increase in ambient temperature led to an increase in the heat transfer coefficient, which was due to the fact that at higher temperatures, the thermal movement of the analysis was more intense, the frequency of collisions between molecules increased, and the heat transfer coefficient also increased. As the ambient temperature continued to rise, the CHTC stabilized because molecular motion had been stabilized at high temperatures. Thus, it is necessary to adjust the ambient temperature in the simulation to match the real conditions, aligning the simulated cooling curve with the experimental results.

The finite element simulation method was used to fit the experimental temperature evolution curves with the FE simulation of various preset CHTC when the die temperature was 160 °C, and the gas pressures were 1, 3, and 15 MPa. It can be seen from Fig. 6 that the temperatures at the three curves of 1,3, and 15 MPa decreased rapidly in 2 s, and the temperatures dropped to 27\%, 31\%, and 33\% of the initial temperatures. Subsequently, the temperature drop slowed down and leveled off. The simulated cooling curve was consistent with the experimental curve, indicating that the simulated convective heat transfer coefficient value corresponds to the CHTC at the specific pressure and temperature. The CHTC was $1.1 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}, 1.4 \mathrm{~kW} /$ $\mathrm{m}^{2} \mathrm{~K}$, and $1.5 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$ at the die temperatures of 160 °C and gas pressures of 1 MPa, 3 MPa, and 15 MPa, respectively. The higher the gas pressure, the larger the CHTC value of AA6061.

To analyze the effect of gas pressure on the CHTC of AA6061, the experimental CHTC value of AA6061 at a die temperature of 160 °C was selected to compare with the results of the gas pressure heat transfer coefficient model, as shown in Fig. 7. The CHTC had a similar initial growth trend to the IHTC. When the air pressure was less than 10 MPa, CHTC increased with a rise in gas pressure. The CHTC value stabilized at $1.6 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$ when the gas pressure was higher than 10 MPa. This was because an increase in gas pressure caused the temperature at the outlet to elevate significantly. The heat exchange between air and AA6061 was intense, and the CHTC increased significantly. When the gas pressure increased to a certain extent, the rise in outlet temperature became slow. In the context of constant heat transfer area, the increase in outlet temperature indicated enhanced heat transfer, with the CHTC showing an overall increasing trend and a faster growth rate in the early stage before slowing down at the later stage.

Fig. 6 Comparison between the experimental and simulated temperatures of AA6061 at different air pressures of 1, 3, and 15 MPa
![](https://cdn.mathpix.com/cropped/212defdc-725e-4542-8ac4-d90bcbc9fbdf-08.jpg?height=1004&width=1258&top_left_y=1485&top_left_x=635)

Fig. 7 The experimental and predicted at different gas pressures
![](https://cdn.mathpix.com/cropped/212defdc-725e-4542-8ac4-d90bcbc9fbdf-09.jpg?height=1013&width=1264&top_left_y=195&top_left_x=633)

## 4 Modeling of the IHTC and CHTC of AA6061

Cetinkale and Fishenden [23] first proposed the heat transfer model, which suggests that heat transfer is a sum of two parts: heat transfer across solid contact between the blank and the die, and heat transfer between the air interface and slab. Since then, Rapier et al. [30] and Cooper et al. [31] verified the independence from the overall heat transfer. In this paper, the stamping heat transfer coefficient model and gas pressure heat transfer coefficient model were proposed as heat transfer consists of two parts.

### 4.1 Predictive model for the IHTC between AA6061 and dies

The IHTC in a stamping heat transfer coefficient model usually depends on the contact pressure, material of the contacting body, and type of lubricant [32]. The present heat transfer coefficient model further took into account the impact of die temperature on the IHTC value between AA6061 and steel die, as the presence of the temperature field also affects the IHTC.

The IHTC of the contact between solids, i.e., $\mathrm{h}_{\mathrm{a}}$, depended on the thermal conductivity of the two contacting solids and contacting surfaces. The amount of heat transfer increased when the thermal conductivity of the specimen and tool increased. Therefore, $\mathrm{h}_{\mathrm{a}}$ with the harmonic mean thermal conductivity $K_{\mathrm{st}}$ was positively correlated. The heat transfer coefficient due to the contact pressure between the solids was obtained by $\mathrm{h}_{\mathrm{a}}$. The equation was shown in Eq. (1) [17].

$$
\begin{equation*}
\mathrm{h}_{\mathrm{a}}=\alpha(T) \frac{K_{s t}}{R_{s t}} N_{p} \tag{1}
\end{equation*}
$$

where $\alpha(T)$ was the temperature-dependent model parameter, $K_{\mathrm{st}}$ was the harmonic mean thermal conductivity of the contacting solid, and $N_{p}$ was the pressure-dependent parameter.

To simplify the model, the harmonic average thermal conductivity $K_{\mathrm{st}}$ was determined by the average thermal conductivity of sample $k_{s}$ and tool $k_{t}$ within the temperature range used in the experiment, as shown in Eq. (2).

$$
\begin{equation*}
K_{\mathrm{st}}=\frac{2 k_{s} k_{t}}{k_{s}+k_{t}} \tag{2}
\end{equation*}
$$

Moreover, the amount of heat transfer increased with the increase of the actual contact area between the specimen and the tool. The contact area between the surfaces was related to the surface roughness. The larger the surface roughness, the larger the increase in real contact area. Thus, the solid contact IHTC $\left(h_{a}\right)$ had a negative correlation with the root mean square of the initial surface roughness of the specimen and tool. Surface roughness $R_{s t}$ was determined by the specimen $R_{s}$ and the forming tool $R_{t}$. The average surface roughness of the tool determined the height variation of the contact surface. The root mean square value was used to ascertain the roughness condition at the interface, as shown in Eq. (3).

$$
\begin{equation*}
R_{s t}=\sqrt{R_{s}^{2}+R_{t}^{2}} \tag{3}
\end{equation*}
$$

Due to the uneven contact surface, the real contact area at the interface was less than the apparent value before compression. An aluminum sheet had a much weaker strength than steel at room temperature when it was heated to high temperatures. Hence, the forming tool deformed the bumps on the contact surface of the blank at a defined contact pressure during compression, resulting in an increase in the real contact area and IHTC. When the applied pressure reached its convergence value, the real contact area approached its apparent contact area, leading to a peak in the IHTC. It was found that the real contact area divided by its apparent value was equal to the applied pressure divided by the ultimate strength of the aluminum billet. It was also determined that the real contact area increased logarithmically with pressure [33, 34]. Thus $N_{p}$, the real contact area increased logarithmically with pressure as the ratio of $P$ to $\sigma$ ratio increases logarithmically. This could be shown by the following exponential law in Eq. (4).

$$
\begin{equation*}
N_{p}=1-\exp \left[-\beta(T) \frac{P}{\sigma}\right] \tag{4}
\end{equation*}
$$

where $\beta$ was the model parameter, $P$ denoted the contact pressure between the specimen and tool, and $\sigma$ was the ultimate strength of AA6061 aluminum alloy at 535 °C. In Eqs. (1) and (4), $\alpha(T)$ and $\beta(T)$ were the temperature-dependent model parameters. By using the Arrhenius equation, $\alpha(T)$ and $\beta(T)$ were modeled by Eqs. (5) and (6).

$$
\begin{equation*}
\alpha(T)=\alpha_{0} \exp \left(\frac{Q_{\alpha}}{R \Delta \mathrm{~T}}\right) \tag{5}
\end{equation*}
$$

$$
\begin{equation*}
\beta(T)=\beta_{0} \exp \left(\frac{Q_{\beta}}{R \Delta \mathrm{~T}}\right) \tag{6}
\end{equation*}
$$

where $R$ was the molar gas constant. $\Delta \mathrm{T}$ was the temperature difference between the die and AA6061, while $\alpha_{0}, Q_{\alpha}, \beta_{0}$, and $Q_{\beta}$ were the model constants.

### 4.2 Predictive model for the CHTC between AA6061 and gas

The factors affecting the CHTC in the gas pressure heat transfer coefficient model were air flow, flow velocity and morphology, presence or absence of phase change in the fluid, geometry and size of the heat transfer surface, and thermophysical properties of the fluid. This model was based on the convective heat transfer criterion, which enabled the convective heat transfer coefficient $\left(\mathrm{h}_{\mathrm{c}}\right)$ at different air pressure sizes to be predicted.

Equation (7) was the Nusselt criterion, which reacted to the strength of convective heat transfer, the dimensionless temperature gradient of the fluid on the solid surface, and the magnitude of the wall's normal temperature gradient during the reactive convective heat transfer process.

$$
\begin{equation*}
N \mathrm{u}=\frac{\mathrm{h}_{\mathrm{c}} \delta}{\mathrm{k}_{\mathrm{sa}}} \tag{7}
\end{equation*}
$$

where $\mathrm{k}_{\mathrm{sa}}$ was the harmonic mean thermal conductivity between the fluid and solid. This was determined through the solid thermal conductivity $\mathrm{k}_{\mathrm{s}}$ and fluid thermal conductivity $\mathrm{k}_{\mathrm{a}}$, where $\delta$ was half of the thickness of AA6061 slab.

It was necessary for gas to flow to the die at high pressure to achieve contact between air and slab. With forced convection of the gas flow, the Reynolds criterion responded to the relative magnitude of inertial and viscous forces in the forced convection of fluids. Equation (8) was the Reynolds criterion.

$$
\begin{equation*}
\operatorname{Re}=\frac{\rho \nu \delta}{\mu} \tag{8}
\end{equation*}
$$

where $\rho$ was the air density, $\nu$ was the fluid velocity, and $\mu$ represented the gas viscosity. There was a temperature difference between the gas and slab after gas flow at high pressure, and the air density would change. Equation (9) reacted to the change of air density with the change of temperature $T$ and pressure.

$$
\begin{equation*}
\rho=\frac{P M}{R \Delta T} \tag{9}
\end{equation*}
$$

where $P$ was the gas pressure, $M$ is the gas mass fraction, and $R$ was the gas constant. The physical properties of the fluxed air varied with the surrounding environment. To achieve quantification of the air's physical properties, Platt's law was chosen in Eq. (10) to characterize the effect of the fluid's physical properties on the $\mathrm{h}_{\mathrm{c}}$, which responded to the relative magnitude of the fluid's momentum diffusivity compared to its thermal diffusivity.

$$
\begin{equation*}
P \mathrm{t}=\frac{\mu C_{\mathrm{p}}}{\mathrm{k}_{\mathrm{a}}} \tag{10}
\end{equation*}
$$

where $C_{\mathrm{p}}$ was the specific heat capacity of the gas, and $\mathrm{k}_{\mathrm{a}}$ was the thermal conductivity of the gas. Equation (11) characterized the strength of convective heat transfer in forced convection. Meanwhile, $\mathrm{h}_{\mathrm{c}}$ was the convective heat transfer coefficient and $A$ was the model parameter, as the convective heat transfer was mainly accomplished through the movement and mixing of fluids. Thus, it was closely related to the fluid flow condition, and this equation was the total formula of convective heat transfer coefficient obtained by combining the above four equations.

$$
\begin{equation*}
\mathrm{h}_{\mathrm{c}}=A \operatorname{Re}^{\mathrm{n}} P \mathrm{t}^{\mathrm{m}} \frac{\mathrm{k}_{\mathrm{sa}}}{\delta} \tag{11}
\end{equation*}
$$

The results obtained from the model were compared with the experimental results, with an average error of less than 5\%. The best fit parameters were solved by minimizing the

Table 5 Model constants
| Parameter | $\mathrm{k}_{\mathrm{s}}(\mathrm{kW} / m K)$ | $\mathrm{k}_{\mathrm{t}}(\mathrm{kW} / m K)$ | $R(\mathrm{~J} / \mathrm{molK})$ | $\alpha_{0}(-)$ |
| :--- | :--- | :--- | :--- | :--- |
| Value | 0.207 | 0.039 | 8.55 | 5.51e-5 |
| Parameter | $\beta_{0}(-)$ | $Q_{\alpha}(\mathrm{J} / \mathrm{mol})$ | $Q_{\beta}(\mathrm{J} / \mathrm{mol})$ | $\sigma(\mathrm{MPa})$ |
| Value | $6.29 \mathrm{e}-5$ | -1730 | -1260 | 21 |
| Parameter | A(-) | $\mu(-)$ | $n(-)$ | $m(-)$ |
| Value | 1.34 | $3.14 \mathrm{e}-5$ | 0.46 | 0.38 |
| Parameter | $R_{s}(\mathrm{~nm})$ | $R_{t}(\mathrm{~nm})$ | $k_{a}(\mathrm{~kW} / m K)$ | $\delta(\mathrm{mm})$ |
| Value | 347 | 268 | 0.0264 | 2 |
| Parameter | $v(\mathrm{ml} / s)$ | $\rho\left(\mathrm{kg} / \mathrm{m}^{3}\right)$ | $C_{p} \mathrm{~J} /(k g \cdot K)$ |  |
| Value | 5 | 1.29 | 1005 |  |


residual sum of squares and fitted function using the least squares method. The predictive model constants for IHTC and CHTC are shown in Table 5.

## 5 Conclusion

The heat transfer coefficient, including the IHTC between AA6061 and H13 tool steel, as well as the CHTC between AA6061 and gas, determined the temperature evolution of aluminum alloys. This subsequently affected the geometric accuracy and post-form properties in hot gas forming. A device was developed in this study to measure the temperature histories of AA606 quenched by the die and air under different conditions. The IHTC and CHTC were then determined using the inverse finite element method, and the effects of contact pressure and die temperature were investigated. Moreover, a model was developed to accurately predict the IHTC and CHTC of AA6061 at different contact pressures and die temperatures with an error of less than 5\%. The detailed findings are summarized below:

1. A thermal forming device specifically designed for studying the heat transfer coefficient was developed to record the temperature evolution of AA6061 and die under stamping and pneumatic conditions. The inverse finite element simulation method was used to derive the IHTC and CHTC values of AA6061 at different temperatures and pressures during the thermal forming experiments.
2. The effects of contact pressure and die temperature on the IHTC of AA6061 were investigated, and the results showed that the IHTC increased following a rise in contact pressure. The IHTC increased rapidly from 1.4 to $2.1 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$, with a $50 \%$ increase in the value of the IHTC, when the contact pressure was lower than 5 MPa. When the contact pressure rose from 5 to 15 MPa, the IHTC value increased slowly before leveling off when the IHTC value reached $2.2 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$.
3. The IHTC decreased when the die temperature was raised. With a contact pressure below 5 MPa, the IHTC at room temperature, 160 °C, and 200 °C decreased $0.25 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$. When the pressure reached 5 MPa , the difference in the IHTC at the three die temperatures of room temperature, 160 °C and 200 °C reached 0.5 kW/ $\mathrm{m}^{2} \mathrm{~K}$ at the same pressure. Thereafter, the difference in the IHTC stabilized among the three temperatures.
4. The results further showed that the CHTC of AA6061 increased with rising gas pressure. When the pressure was below 10 MPa, the CHTC values doubled from 0.8 to $1.6 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$. Subsequently, the values tended to stabilize, with the CHTC remaining steady at $1.6 \mathrm{~kW} / \mathrm{m}^{2} \mathrm{~K}$.
5. Predictive models for the IHTC and CHTC were developed in this study. The IHTC model considered the changes in surface roughness caused by pressure, which in turn affected the IHTC. This model also considered the temperature differences due to the heat transfer between the blank and die, which changed the IHTC. The IHTC model can predict the corresponding IHTC of AA6061 based on different contact pressures and die temperatures. Taking into account the impact of gas pressure on the temperature field surrounding the blank, the CHTC model can predict the CHTC of AA6061 under various gas pressure magnitudes. Both models were capable of accurate predictions.

Acknowledgements Much appreciated is the strong support received from the below. This work is supported by the National Natural Science Foundation of China (grant number 52205412).

Author contribution Jiatian Lin: conceptualization, methodology, writing-original draft preparation. Dechong Li: writing-reviewing and editing. Kailun Zheng: conceptualization, validation, funding acquisition. Xiaochuan Liu: supervision.

## Declarations

Ethics approval Not applicable.
Consent to participate All authors agreed to participate in this research.

Consent for publication All authors have read and agreed to the published version of the manuscript.

Competing interests The authors declare no competing interests.

## References

1. Karbasian H, Tekkaya AE (2010) A review on hot stamping. J Mater Process Technol 210:2103-2118. https://doi.org/10.1016/j.jmatp rotec.2010.07.019
2. Maeno T, Mori K, Unou C (2011) Optimisation of condition in hot gas bulging of aluminium alloy tube using resistance heating set into dies. KEM 473:69-74. https://doi.org/10.4028/www.scientific.net/KEM.473.69

3. Xu Y, Lv X-W, Wang Y et al (2023) Effect of hot metal gas forming process on formability and microstructure of 6063 aluminum alloy double wave tube. Materials 16:1152. https://doi.org/10.3390/ma160 31152
4. Cui J, Roven HJ (2010) Recycling of automotive aluminum. Trans Nonferrous Met Soc China 20:2057-2063. https://doi.org/10.1016/S1003-6326(09)60417-9
5. Toros S, Ozturk F, Kacar I (2008) Review of warm forming of aluminum-magnesium alloys. J Mater Process Technol 207:1-12. https://doi.org/10.1016/j.jmatprotec.2008.03.057
6. El Fakir O, Wang L, Balint D et al (2014) Numerical study of the solution heat treatment, forming, and in-die quenching (HFQ) process on AA5754. Int J Mach Tools Manuf 87:39-48. https://doi.org/10.1016/j.ijmachtools.2014.07.008
7. Raugei M, El Fakir O, Wang L et al (2014) Life cycle assessment of the potential environmental benefits of a novel hot forming process in automotive manufacturing. J Clean Prod 83:80-86. https://doi. org/10.1016/j.jclepro.2014.07.037
8. Ikeuchi K, Yanagimoto J (2011) Valuation method for effects of hot stamping process parameters on product properties using hot forming simulator. J Mater Process Technol 211:1441-1447. https://doi. org/10.1016/j.jmatprotec.2011.03.017
9. Caron EJFR, Daun KJ, Wells MA (2014) Experimental heat transfer coefficient measurements during hot forming die quenching of boron steel at high temperatures. Int J Heat Mass Transf 71:396-404. https://doi.org/10.1016/j.ijheatmasstransfer.2013.12.039
10. Caron E, Daun KJ, Wells MA (2013) Experimental characterization of heat transfer coefficients during hot forming die quenching of boron steel. Metall Mater Trans B 44:332-343. https://doi.org/10. 1007/s11663-012-9772-x
11. Bai Q, Lin J, Zhan L et al (2012) An efficient closed-form method for determining interfacial heat transfer coefficient in metal forming. Int J Mach Tools Manuf 56:102-110. https://doi.org/10.1016/j.ijmac htools.2011.12.005
12. Jarrar FS, Hector LG, Khraisheh MK, Bower AF (2010) New approach to gas pressure profile prediction for high temperature AA5083 sheet forming. J Mater Process Technol 210:825-834. https://doi.org/10.1016/j.jmatprotec.2010.01.002
13. Yukawa N, Nakashima Y, Ishiguro T et al (2014) Modeling of heat transfer coefficient of oxide scale in hot forging. Procedia Eng 81:492-497. https://doi.org/10.1016/j.proeng.2014.10.028
14. Chang Y, Tang X, Zhao K et al (2016) Investigation of the factors influencing the interfacial heat transfer coefficient in hot stamping. J Mater Process Technol 228:25-33. https://doi.org/10.1016/j.jmatp rotec.2014.10.008
15. Hu P, Ying L, Li Y, Liao Z (2013) Effect of oxide scale on temperature-dependent interfacial heat transfer in hot stamping process. J Mater Process Technol 213:1475-1483. https://doi.org/10.1016/j.jmatprotec.2013.03.010
16. Hu ZM, Brooks JW, Dean TA (1998) The interfacial heat transfer coefficient in hot die forging of titanium alloy. Proc Inst Mech Eng C J Mech Eng Sci 212:485-496. https://doi.org/10.1243/0954406981 521385
17. Burte PR, Im Y-T, Altan T, Semiatin SL (1990) Measurement and analysis of heat transfer and friction during hot forging. J Eng Ind 112:332-339. https://doi.org/10.1115/1.2899596
18. Zhang XZ, Zhang LW, Xing L (2010) Study of thermal interfacial resistance between TC11/glass lubrication/K403 joint. Exp Thermal Fluid Sci 34:48-52. https://doi.org/10.1016/j.expthermflusci.2009.09.001
19. Zhao K, Ren D, Wang B, Chang Y (2019) Investigation of the interfacial heat transfer coefficient of sheet aluminum alloy 5083 in warm stamping process. Int J Heat Mass Transf 132:293-300. https://doi. org/10.1016/j.ijheatmasstransfer.2018.11.158
20. Ying L, Gao T, Dai M, Hu P (2017) Investigation of interfacial heat transfer mechanism for 7075-T6 aluminum alloy in HFQ hot forming process. Appl Therm Eng 118:266-282. https://doi.org/10. 1016/j.applthermaleng.2017.02.107
21. Liu X, Ji K, Fakir OE et al (2017) Determination of the interfacial heat transfer coefficient for a hot aluminium stamping process. J Mater Process Technol 247:158-170. https://doi.org/10.1016/j.jmatp rotec.2017.04.005
22. Khandkar MZH, Khan JA, Reynolds AP (2003) Prediction of temperature distribution and thermal history during friction stir welding: input torque based model. Sci Technol Weld Joining 8:165-174. https://doi.org/10.1179/136217103225010943
23. Hamilton C, Dymek S, Sommers A (2008) A thermal model of friction stir welding in aluminum alloys. Int J Mach Tools Manuf 48:1120-1130. https://doi.org/10.1016/j.ijmachtools.2008.02.001
24. Schmidt H, Hattel J, Wert J (2004) An analytical model for the heat generation in friction stir welding. Modelling Simul Mater Sci Eng 12:143-157. https://doi.org/10.1088/0965-0393/12/1/013
25. Gadakh VS, Adepu K (2013) Heat generation model for taper cylindrical pin profile in FSW. J Market Res 2:370-375. https://doi.org/10.1016/j.jmrt.2013.10.003
26. Hao G, Liu Z (2020) Thermal contact resistance enhancement with aluminum oxide layer generated on TiAlN-coated tool and its effect on cutting performance for H13 hardened steel. Surf Coat Technol 385:125436. https://doi.org/10.1016/j.surfcoat.2020.125436
27. Zhao K, Wang B, Chang Y et al (2015) Comparison of the methods for calculating the interfacial heat transfer coefficient in hot stamping. Appl Therm Eng 79:17-26. https://doi.org/10.1016/j.applt hermaleng.2015.01.018
28. She J, Zhang H, Han K et al (2020) Experimental investigation of mechanisms influencing friction coefficient between lost circulation materials and shale rocks. Powder Technol 364:13-26. https://doi. org/10.1016/j.powtec.2020.01.047
29. Wang Z, Tong H, Wang Z et al (2023) Effect of gap length and partition thickness on thermal boundary layer in thermal convection. Entropy 25:386. https://doi.org/10.3390/e25020386
30. Rapier AC, Jones TM, McIintosh JE (1963) The thermal conductance of uranium dioxide/stainless steel interfaces. Int J Heat Mass Transf 6:397-416. https://doi.org/10.1016/0017-9310(63)90101-7
31. Cooper MG, Mikic BB, Yovanovich MM (1969) Thermal contact conductance. Int J Heat Mass Tranf 12:279-300. https://doi.org/10. 1016/0017-9310(69)90011-8
32. Liu X, Cai Z, Zheng Y et al (2020) A general IHTC model for hot/ warm aluminium stamping. Appl Therm Eng 181:115619. https://doi.org/10.1016/j.applthermaleng.2020.115619
33. Buchner B, Buchner M, Buchmayr B (2009) Determination of the real contact area for numerical simulation. Tribol Int 42:897-901. https://doi.org/10.1016/j.triboint.2008.12.009
34. Murashov MV, Panin SD (2015) Numerical modelling of contact heat transfer problem with work hardened rough surfaces. Int J Heat Mass Transf 90:72-80. https://doi.org/10.1016/j.ijheatmasstransfer. 2015.06.024

Publisher's Note Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations.

Springer Nature or its licensor (e.g. a society or other partner) holds exclusive rights to this article under a publishing agreement with the author(s) or other rightsholder(s); author self-archiving of the accepted manuscript version of this article is solely governed by the terms of such publishing agreement and applicable law.


[^0]:    Xiaochuan Liu
    liuxiaochuan2020@xjtu.edu.cn
    Jiatian Lin
    linjiatian12138@163.com
    ${ }^{1}$ School of Mechanical Engineering, Dalian University of Technology, Dalian 116024, China
    ${ }^{2}$ School of Mechanical Engineering, Xi'an Jiaotong University, Xi'an 710049, China

