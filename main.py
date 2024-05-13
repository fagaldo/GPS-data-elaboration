from mpl_toolkits.mplot3d.art3d import Line3D
import matplotlib.pyplot as plt
import numpy as np
import re
from scipy.interpolate import interp1d
from scipy.interpolate import UnivariateSpline

def euclidean_distance(p1, p2):
    return np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)


def interpolate_reference(ref_data, num_points):
    """
    Interpoluje dodatkowe punkty referencyjne, aby uzyskać równomiernie rozmieszczone punkty na całej ścieżce.
    """
    total_distance = 0
    distances = [0]
    for i in range(1, len(ref_data)):
        dist = euclidean_distance(ref_data[i], ref_data[i-1])
        total_distance += dist
        distances.append(total_distance)
    f_lat = interp1d(distances, [point[0] for point in ref_data], kind='linear')
    f_lon = interp1d(distances, [point[1] for point in ref_data], kind='linear')
    new_distances = np.linspace(0, total_distance, num_points)
    interpolated_ref_data = [(f_lat(dist), f_lon(dist)) for dist in new_distances]
    return interpolated_ref_data


def calculate_mean_euclidean_error(smoothed_data, ref_data):
    """
    Oblicza błąd pomiędzy danymi wygładzonymi a danymi referencyjnymi.
    """
    total_error = 0
    num_points = len(smoothed_data)
    for i in range(num_points):
        error = euclidean_distance(smoothed_data[i][1:], ref_data[i])
        total_error += error
    mean_error = total_error / num_points
    return mean_error


def calculate_mse(smoothed_data, ref_data):
    """
    Oblicza błąd średniokwadratowy (MSE) pomiędzy danymi wygładzonymi a danymi referencyjnymi przy użyciu NumPy.
    """
    smoothed_data = np.array(smoothed_data)[:, 1:]  # Pomiń pierwszą kolumnę, przekonwertuj na NumPy array
    ref_data = np.array(ref_data)
    squared_error = np.sum((smoothed_data - ref_data) ** 2, axis=1)
    mean_squared_error = np.mean(squared_error)
    return mean_squared_error


def calculate_mae(smoothed_data, ref_data):
    # Przekształcenie danych wejściowych na tablice NumPy i pominiecie pierwszej kolumny w smoothed_data, jeśli jest to potrzebne
    smoothed_array = np.array(smoothed_data)[:, 1:]  # Zakładamy, że pierwsza kolumna to czas lub inny identyfikator
    ref_array = np.array(ref_data)

    # Obliczenie wartości bezwzględnych różnic pomiędzy odpowiadającymi sobie elementami
    absolute_errors = np.abs(smoothed_array - ref_array)
    #print(absolute_errors)

    # Obliczenie średniej z wartości bezwzględnych różnic
    mean_absolute_error = np.mean(absolute_errors)
    return mean_absolute_error


# Wczytanie danych wygładzonych z pliku tekstowego
smoothed_data = []
with open("smoothed MAFuzzy.txt", "r") as file:
    for line in file:
        match = re.search(r'Point (\d+): Lat: ([\d.]+), Long: ([\d.]+)', line)
        if match:
            point_index = int(match.group(1))
            lat = float(match.group(2))
            lon = float(match.group(3))
            smoothed_data.append((point_index, lat, lon))

smoothed_data = np.array(smoothed_data)
ref_data = []
with open("referencyjne.txt", "r") as file:
    for line in file:
        match = re.search(r'([\d.]+), ([\d.]+)', line)
        if match:
            lon = float(match.group(1))
            lat = float(match.group(2))
            ref_data.append((lat, lon))
ref_data = np.array(ref_data)
interpolated_ref_data = np.array(interpolate_reference(ref_data, len(smoothed_data)))
mean_error = calculate_mean_euclidean_error(smoothed_data, interpolated_ref_data)
mse = calculate_mse(smoothed_data, interpolated_ref_data)
mae = calculate_mae(smoothed_data, interpolated_ref_data)

print("Średni błąd: ", mean_error)
print("MSE: ", mse)
print("MAE: ", mae)
# Wczytanie danych oryginalnych z pliku tekstowego
original_data = []
with open("original.txt", "r") as file:
    for line in file:
        match = re.search(r'Point (\d+):Latitude:([\d.]+)\sLongitude:([\d.]+)', line)
        if match:
            point_index = int(match.group(1))
            lat = float(match.group(2))
            lon = float(match.group(3))
            original_data.append((point_index, lat, lon))

original_data = np.array(original_data)
mean_error2 = calculate_mean_euclidean_error(original_data, interpolated_ref_data)
mse2 = calculate_mse(original_data, interpolated_ref_data)
mae2 = calculate_mae(original_data, interpolated_ref_data)
print("Średni błąd2: ", mean_error2)
print("MSE2: ", mse2)
print("MAE2: ", mae2)
# Obliczenie błędów

errors = np.linalg.norm(np.array(interpolated_ref_data) - smoothed_data[:, 1:], axis=1)


# Obliczenie mediany
#median_center = np.median(original_data[:, 1:], axis=0)

# Tworzenie wykresów
fig, axs = plt.subplots(1, 2, figsize=(15, 10))

# Wykres linii czasowej
# axs[0, 0].plot(smoothed_data[:, 0], smoothed_data[:, 2], label='Smoothed Path')
# axs[0, 0].set_xlabel('Index')
# axs[0, 0].set_ylabel('Latitude')
# axs[0, 0].legend()

# Wykres punktowy
axs[0].scatter(original_data[:, 1], original_data[:, 2], label='Original points')
axs[0].scatter(smoothed_data[:, 1], smoothed_data[:, 2], label='Smoothed points')
axs[0].scatter(interpolated_ref_data[:, 0], interpolated_ref_data[:, 1], label='Referential points')
axs[0].set_xlabel('Latitude')
axs[0].set_ylabel('Longitude')
axs[0].legend()

max_distance = 0.1

# Wykres linii
original_path = original_data[:, 1:3]
smoothed_path = smoothed_data[:, 1:3]
ref_path = interpolated_ref_data

# Rysuj linię między punktami blisko siebie
for i in range(len(original_path) - 1):
    if euclidean_distance(original_path[i], original_path[i + 1]) < max_distance:
        axs[1].plot([original_path[i, 0], original_path[i + 1, 0]], [original_path[i, 1], original_path[i + 1, 1]],
                    c='b', label="Original path")

for i in range(len(smoothed_path) - 1):
    if euclidean_distance(smoothed_path[i], smoothed_path[i + 1]) < max_distance:
        axs[1].plot([smoothed_path[i, 0], smoothed_path[i + 1, 0]], [smoothed_path[i, 1], smoothed_path[i + 1, 1]],
                    c='orange', label="Smoothed path")
for i in range(len(ref_path) - 1):
    if euclidean_distance(ref_path[i], ref_path[i + 1]) < max_distance:
        axs[1].plot([ref_path[i, 0], ref_path[i + 1, 0]],
                    [ref_path[i, 1], ref_path[i + 1, 1]],
                    c='g', label="Referential path")

axs[1].set_xlabel('Latitude')
axs[1].set_ylabel('Longitude')
axs[1].legend(handles=[
    plt.Line2D([], [], color='blue', label='Original path'),
    plt.Line2D([], [], color='orange', label='Smoothed path'),
    plt.Line2D([], [], color='green', label='Referential path')
])

plt.tight_layout()
plt.show()

fig, axs = plt.subplots(1, 3, figsize=(15, 10))

# Wykres błędów
axs[0].plot(smoothed_data[:, 0], errors, label='Errors')
axs[0].set_xlabel('Index')
axs[0].set_ylabel('Error')
axs[0].legend()

# Wykres heatmapy
hb = axs[1].hexbin(smoothed_data[:, 1], smoothed_data[:, 2], gridsize=50, cmap='inferno')
axs[1].set_xlabel('Latitude')
axs[1].set_ylabel('Longitude')
plt.colorbar(hb, ax=axs[1], label='Frequency')

hb = axs[2].hexbin(original_data[:, 1], original_data[:, 2], gridsize=50, cmap='inferno')
axs[2].set_xlabel('Latitude')
axs[2].set_ylabel('Longitude')
plt.colorbar(hb, ax=axs[2], label='Frequency')

# Wykres dla mediany
# axs[1, 2].scatter(original_data[:, 1], original_data[:, 2], label='Original Points')
# axs[1, 2].scatter(median_center[0], median_center[1], c='r', label='Median Center')
# axs[1, 2].set_xlabel('Latitude')
# axs[1, 2].set_ylabel('Longitude')
# axs[1, 2].legend()

plt.tight_layout()
plt.show()

# Stworzenie figury 3D
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

# Rysowanie linii między punktami blisko siebie dla danych oryginalnych
original_path = original_data[:, 1:4]
for i in range(len(original_path) - 1):
    if euclidean_distance(original_path[i], original_path[i + 1]) < max_distance:
        ax.plot([original_data[i, 1], original_data[i + 1, 1]], [original_data[i, 2], original_data[i + 1, 2]],
                [original_data[i, 0], original_data[i + 1, 0]], c='blue')

# Rysowanie linii między punktami blisko siebie dla danych wygładzonych
smoothed_path = smoothed_data[:, 1:4]
for i in range(len(smoothed_path) - 1):
    if euclidean_distance(smoothed_path[i], smoothed_path[i + 1]) < max_distance:
        ax.plot([smoothed_data[i, 1], smoothed_data[i + 1, 1]], [smoothed_data[i, 2], smoothed_data[i + 1, 2]],
                [smoothed_data[i, 0], smoothed_data[i + 1, 0]], c='orange')



# Ustawienie etykiet osi
ax.set_xlabel('Latitude')
ax.set_ylabel('Longitude')
ax.set_zlabel('Index')

ax.legend(handles=[
    plt.Line2D([], [], color='blue', label='Original Path'),
    plt.Line2D([], [], color='orange', label='Smoothed Path')
])

#ax.legend(['Original Path (blue)', 'Smoothed Path (orange)', 'Index (red)'])


plt.show()
