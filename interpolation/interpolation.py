from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from scipy import interpolate
import numpy as np
import scipy.linalg
import csv

input_file = csv.DictReader(open("collected_data.csv"))

angle = []
stiffness = []
camera = []

for row in input_file:
    angle.append((3.1415 * int(row['angle'])) / 180)
    stiffness.append(int(row['stiffness']))
    camera.append(float(row['camera']))

# c_ method added items along second axis
data = np.c_[angle, stiffness, camera]

x_range = np.arange(0, 3.14, 0.25)
y_range = np.arange(-60, 60, 20)
X, Y = np.meshgrid(x_range, y_range)
XX = X.flatten()
YY = Y.flatten()

# best-fit quadratic curve
A = np.c_[np.ones(data.shape[0]), data[:, :2], np.prod(data[:, :2], axis=1), data[:, :2] ** 2]
C, _, _, _ = scipy.linalg.lstsq(A, data[:, 2])


# evaluate it on a grid
Z = C[4]*X**2. + C[5]*Y**2. + C[3]*X*Y + C[1]*X + C[2]*Y + C[0]

# plots 3D chart

fig = plt.figure()
ax = fig.gca(projection='3d')
ax.plot_surface(X, Y, Z, rstride=1, cstride=1, alpha=0.2)
ax.scatter(angle, stiffness, camera, c='r', marker='o')

plt.xlabel('angle')
plt.ylabel('stiffness')
ax.set_zlabel('camera')

plt.show()

# plt.plot(angle, camera, 'ro')
# plt.show()
