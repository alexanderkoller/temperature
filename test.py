from scipy import stats
import numpy as np
import matplotlib.pyplot as plt

x = np.arange(0, 300, 1)
a_y = np.log((x + 100.)/100.)
min_num_points = 50
proportion = 0.1
num_points = max(min_num_points, int(0.2 * len(x)))
linreg_start_pos = len(x) - num_points
slope, intercept, _, _, _ = stats.linregress(range(linreg_start_pos, len(x)), a_y[linreg_start_pos:])
plt.plot(x, a_y)
y_hat = slope * x + intercept
plt.plot(x, a_y, color='k')
plt.plot(x, y_hat, color='b')
plt.show()
