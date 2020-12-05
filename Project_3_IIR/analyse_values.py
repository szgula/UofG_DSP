import pandas as pd
import matplotlib.pyplot as plt
from IIR_filter import IIRFilter, IIR2Filter, return_filter
plot_loaded_data = False

data = pd.read_csv(r"Arduino Python/xyz_output.txt", names=['time', 'x', 'y', 'z', 'x_f', 'y_f', 'z_f'], header=None)

us = (data.iloc[:, 1] ** 2 + data.iloc[:, 2] ** 2 + data.iloc[:, 3] ** 2) ** 0.5
s = (data.iloc[:, 4] ** 2 + data.iloc[:, 5] ** 2 + data.iloc[:, 6] ** 2) ** 0.5
if plot_loaded_data:
    plt.plot(data.iloc[:,0], s, label='filtered')
    plt.plot(data.iloc[:,0], us, label='raw')
    plt.legend()

fx, fy, fz = return_filter(), return_filter(), return_filter()
data_out = {'x': [], 'y':[], 'z':[], 's':[]}

for idx,(_, x, y, z, *_) in data.iterrows():
    xf, yf, zf = fx.filter(x), fx.filter(y), fx.filter(z)
    data_out['x'].append(xf)
    data_out['y'].append(yf)
    data_out['z'].append(zf)
    data_out['s'].append((xf**2 + yf**2 + zf**2)**0.5)


plt.plot(data.iloc[:,0], s, label='filtered')
plt.plot(data.iloc[:,0], us, label='raw')
#plt.plot(data.iloc[:,0], data_out['s'], label='filtered_2')
plt.legend()



pass