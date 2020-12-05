import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("xyz_output.txt")

us  = (data.iloc[:, 1] ** 2 + data.iloc[:, 2] ** 2 + data.iloc[:, 3] ** 2) ** 0.5
s = (data.iloc[:, 4] ** 2 + data.iloc[:, 5] ** 2 + data.iloc[:, 6] ** 2) ** 0.5
plt.plot(data.iloc[:,0], s, label='y')
plt.plot(data.iloc[:,0], us, label='z')
plt.legend()
plt.show()
pass