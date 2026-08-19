clear all;
k = 10^6;
n1 = 4;
n2 = 13;
K = 10^6;
B = 10^7;
A = 13;
C = 10^2;
E = 10^10;
i = 1;
ep(i) = 0;
etotalrate = 1;
flow(i) = 0;
disloc(i) = 0;
R(i) = 0;
etotal(i) = 0.0001;
t(i) = 0;
deltat = 0.01;
while etotal < 1

R(i) = B*(disloc(i))^0.5;
// eprate = dotepsilon_p
// flow = sigma
// k = sigma_0
eprate(i) = abs((flow(i) - R(i) - k)/K)^n1;
// dislocrate = dotrho
// disloc = rho
dislocrate(i) = A * ( 1- disloc(i))*eprate(i) - C * (disloc(i))^n2;

flow(i+1) = E * (etotal(i) - ep(i));

ep(i+1) = ep(i) + eprate (i) * deltat;
disloc(i+1) = disloc(i) + dislocrate(i)*deltat; 
etotal(i+1) = etotal (i) + etotalrate * deltat;
%%flow(i+1) = flow(i) + flowrate(i)*deltat;
t(i+1) = t(i) + deltat;
i = i+1;
end
// etotal = episilon_t (integrate dotepsilon)
plot (etotal, flow)