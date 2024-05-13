import matplotlib.pyplot as plt
import numpy as np
import re
from scipy.interpolate import interp1d, CubicSpline
from scipy.signal import savgol_filter

from main import euclidean_distance


def euclidean_distance(p1, p2):
    return np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def interpolate_reference(ref_data, num_points):
    """
    Interpoluje dodatkowe punkty referencyjne, aby uzyskać równomiernie rozmieszczone punkty na całej ścieżce,
    używając interpolacji liniowej opartej na długości łuku.
    """
    # Obliczanie odległości między punktami
    distances = np.array([0] + [euclidean_distance(ref_data[i], ref_data[i - 1]) for i in range(1, len(ref_data))])
    cumulative_distances = np.cumsum(distances)

    # Równomierne rozmieszczenie odległości wzdłuż całkowitej długości ścieżki
    new_distances = np.linspace(0, cumulative_distances[-1], num_points)

    # Interpolacja
    f_lat = interp1d(cumulative_distances, [p[0] for p in ref_data], kind='linear')
    f_lon = interp1d(cumulative_distances, [p[1] for p in ref_data], kind='linear')

    # Tworzenie nowych punktów
    interpolated_points = [(f_lat(d), f_lon(d)) for d in new_distances]
    return interpolated_points


ref_data = []
with open("referencyjne2.txt", "r") as file:
    for line in file:
        match = re.search(r'([\d.]+), ([\d.]+)', line)
        if match:
            lon = float(match.group(1))
            lat = float(match.group(2))
            ref_data.append((lat, lon))
ref_data = np.array(ref_data)
print(ref_data)
interpolated_ref_data = np.array(interpolate_reference(ref_data, 600))
fig, axs = plt.subplots(1, 1, figsize=(15, 10))
axs.scatter(interpolated_ref_data[:, 0], interpolated_ref_data[:, 1], label='Referential points')
axs.set_xlabel('Latitude')
axs.set_ylabel('Longitude')
axs.legend()
plt.tight_layout()
plt.show()
