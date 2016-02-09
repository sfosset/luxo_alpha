from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import json

with open('luxo_1_data_5.json') as data_file:
    data = json.load(data_file)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
xs, ys, zs = [], [], []

for point_obj in data["dataset"]:
    xs.append(point_obj["point"][0])
    ys.append(point_obj["point"][1])
    zs.append(point_obj["point"][2])
    for linking_points in point_obj["linking_points"]:
        for linking_point in linking_points:
            xs.append(linking_point[0])
            ys.append(linking_point[1])
            zs.append(linking_point[2])




for c, m in [('r', 'o')]:
    ax.scatter(xs, ys, zs, c=c, marker=m)

ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')

plt.show()
