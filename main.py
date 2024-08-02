import math

from mpl_toolkits.mplot3d.art3d import Line3D
import matplotlib.pyplot as plt
import numpy as np
import re
from scipy.interpolate import interp1d
import yaml
import os


def euclidean_distance(p1, p2):
    return np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def haversine_distance(coord1, coord2):
    """
    Calculate the Haversine distance between two geographical coordinates.
    """
    R = 6371.0  # Earth radius in kilometers

    lat1, lon1 = np.radians(coord1)
    lat2, lon2 = np.radians(coord2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    distance = R * c
    return distance


def interpolate_reference(data, num_points):
    """
    Interpolates additional reference points to obtain evenly spaced points along the path.
    """
    total_distance = 0
    distances = [0]
    for i in range(1, len(data)):
        print(data[i])
        print(i.__str__())
        dist = haversine_distance(data[i], data[i - 1])
        total_distance += dist
        distances.append(total_distance)

    f_lat = interp1d(distances, [point[0] for point in data], kind='linear')
    f_lon = interp1d(distances, [point[1] for point in data], kind='linear')
    new_distances = np.linspace(0, total_distance, num_points)
    interpolated_data = [(f_lat(dist), f_lon(dist)) for dist in new_distances]
    return interpolated_data


# Ścieżka do pliku konfiguracyjnego
config_path = 'config.yaml'

# Odczyt pliku konfiguracyjnego
with open(config_path, 'r') as config_file:
    config = yaml.safe_load(config_file)

# Pobranie ścieżek do plików z danymi
data_files = config['data_files']
original_data = []
smoothed_data = []
ref_data = []

# Ładowanie danych z plików
for file_path in data_files:
    full_path = os.path.join(os.getcwd(), file_path)
    with open(full_path, 'r') as data_file:
        for line in data_file:
            match = re.search(r'Point (\d+):Latitude:([\d.]+)\sLongitude:([\d.]+)', line)
            if match:
                point_index = int(match.group(1))
                lat = float(match.group(2))
                lon = float(match.group(3))
                original_data.append((point_index, lat, lon))
    with open(full_path, "r") as file:
        for line in file:
            match = re.search(
                r'Point (\d+): Lat: ([\d.]+), Long: ([\d.]+), MAE: ([\d.E+-]+), Group: (\d+), Time: (\d+)', line)
            if match:
                point_index = int(match.group(1))
                lat = float(match.group(2))
                lon = float(match.group(3))
                mae = float(match.group(4))
                group = int(match.group(5))
                time = int(match.group(6))
                smoothed_data.append((point_index, lat, lon, mae, group, time))
    with open(full_path, "r") as file:
        for line in file:
            match = re.search(r'([\d.]+), ([\d.]+)', line)
            if match:
                lat = float(match.group(1))
                lon = float(match.group(2))
                ref_data.append((lat, lon))

smoothed_data = np.array(smoothed_data)
original_data = np.array(original_data)

ref_data = np.array(ref_data)
interpolated_ref_data = np.array(interpolate_reference(ref_data, len(smoothed_data)))
smoothed_coords = smoothed_data[:, 1:3]
interpolated_smoothed_coords = np.array(interpolate_reference(smoothed_coords, len(smoothed_data)))


def group_data(data):
    grouped_data = {}
    for point in data:
        group = point[4]
        if group not in grouped_data:
            grouped_data[group] = []
        grouped_data[group].append(point)
    return grouped_data


def group_data_by_original(original_data, smoothed_data):
    """
    Grupuje dane oryginalne według grup z danych wygładzonych.
    """
    grouped_data = {}
    for smooth_point, orig_point in zip(smoothed_data, original_data):
        group = smooth_point[4]  # Grupa z danych wygładzonych
        if group not in grouped_data:
            grouped_data[group] = []
        grouped_data[group].append(orig_point)
    return grouped_data


def calculate_groups_errors(grouped_smoothed_data, grouped_original_data, ref_data):
    total_error_smoothed = 0
    total_error_original = 0
    total_squared_error_smoothed = 0
    total_squared_error_original = 0
    total_absolute_error_smoothed = 0
    total_absolute_error_original = 0
    errors_smoothed = []
    errors_original = []
    num_groups = len(grouped_smoothed_data)

    for group, group_points_smoothed in grouped_smoothed_data.items():
        # Find the representative point in the smoothed group closest to any reference point
        rep_point_smoothed, rep_point_index = min(
            ((p[1:3], idx) for idx, p in enumerate(group_points_smoothed)),
            key=lambda pi: euclidean_distance(pi[0], find_closest_point(pi[0], ref_data))
        )
        closest_ref_point = find_closest_point(rep_point_smoothed, ref_data)

        # Find the closest point in the original group to the representative point of the smoothed group
        group_points_original = grouped_original_data[group]
        closest_point_original, closest_point_index = min(
            ((p[1:3], idx) for idx, p in enumerate(group_points_original)),
            key=lambda pi: euclidean_distance(rep_point_smoothed, pi[0])
        )

        # Calculate errors
        error_smoothed = euclidean_distance(rep_point_smoothed, closest_ref_point)
        error_original = euclidean_distance(closest_point_original, closest_ref_point)

        total_error_smoothed += error_smoothed
        total_error_original += error_original

        total_squared_error_smoothed += error_smoothed ** 2
        total_squared_error_original += error_original ** 2

        total_absolute_error_smoothed += abs(error_smoothed)
        total_absolute_error_original += abs(error_original)

        errors_smoothed.append(error_smoothed)
        errors_original.append(error_original)

        # Print selected indices
        # print(
        #    f'Group: {group}, Selected smoothed point index: {rep_point_index}, Selected original point index: {closest_point_index}')

    mean_error_smoothed = total_error_smoothed / num_groups
    mean_error_original = total_error_original / num_groups

    mse_smoothed = total_squared_error_smoothed / num_groups
    mse_original = total_squared_error_original / num_groups

    mae_smoothed = total_absolute_error_smoothed / num_groups
    mae_original = total_absolute_error_original / num_groups

    rmse_smoothed = math.sqrt(mse_smoothed)
    rmse_original = math.sqrt(mse_original)

    median_error_smoothed = np.median(errors_smoothed)
    median_error_original = np.median(errors_original)

    return mean_error_smoothed, mean_error_original, mse_smoothed, mse_original, mae_smoothed, mae_original, rmse_smoothed, rmse_original, median_error_smoothed, median_error_original, errors_smoothed


def calculate_group_mean(grouped_data, ref_data):
    total_error = 0
    num_groups = len(grouped_data)
    for group_points in grouped_data.values():
        # Find the representative point as the one closest to any reference point
        rep_point = min(group_points, key=lambda p: euclidean_distance(p[1:3], find_closest_point(p[1:3], ref_data)))[
                    1:3]
        closest_ref_point = find_closest_point(rep_point, ref_data)
        error = euclidean_distance(rep_point, closest_ref_point)
        total_error += error
    mean_error = total_error / num_groups
    return mean_error


def find_closest_point(target_point, reference_points):
    """
    Znajduje najbliższy punkt do target_point wśród reference_points.
    """
    closest_point = reference_points[0]
    min_distance = euclidean_distance(target_point, closest_point)
    for point in reference_points[1:]:
        distance = euclidean_distance(target_point, point)
        if distance < min_distance:
            min_distance = distance
            closest_point = point
    return closest_point


def calculate_mean_euclidean_error(smoothed_data, ref_data):
    """
    Oblicza błąd pomiędzy danymi wygładzonymi a danymi referencyjnymi.
    """
    errors = []
    total_error = 0
    num_points = len(smoothed_data)
    for i in range(num_points):
        error = euclidean_distance(smoothed_data[i][1:], ref_data[i])
        errors.append(error)
        total_error += error
    mean_error = total_error / num_points
    print("mediana dla kolejnych punktów bez uwzględniania grup:", np.median(errors))
    return mean_error, errors


def calculate_mse(smoothed_data, ref_data):
    """
    Oblicza MSE
    """
    errors = []
    total_error = 0
    num_points = len(smoothed_data)
    for i in range(num_points):
        error = pow(euclidean_distance(smoothed_data[i][1:], ref_data[i]), 2)
        errors.append(error)
        total_error += error
    mean_error = total_error / num_points
    return mean_error


def calculate_rmse(smoothed_data, ref_data):
    """
    Oblicza RMSE
    """
    errors = []
    total_error = 0
    num_points = len(smoothed_data)
    for i in range(num_points):
        error = pow(euclidean_distance(smoothed_data[i][1:], ref_data[i]), 2)
        errors.append(error)
        total_error += error
    mean_error = total_error / num_points
    return math.sqrt(mean_error)


def calculate_mae(smoothed_data, ref_data):
    """
    Oblicza MAE
    """
    errors = []
    total_error = 0
    num_points = len(smoothed_data)
    for i in range(num_points):
        error = abs(euclidean_distance(smoothed_data[i][1:], ref_data[i]))
        errors.append(error)
        total_error += error
    mean_error = total_error / num_points
    return mean_error


grouped_smoothed_data = group_data(smoothed_data)  # Grupy dla wygładzonych danych
grouped_original_data = group_data_by_original(original_data,
                                               smoothed_data)  # Grupy dla oryginalnych danych na podstawie grup z wygładzonych danych
print("Ilość grup:", len(grouped_smoothed_data))
print("Ilość grup2:", len(grouped_original_data))
mean_error, mean_error3, mse, mse2, mae, mae2, rmsd, rmsd2, median, median2, errors = calculate_groups_errors(
    grouped_smoothed_data, grouped_original_data, interpolated_ref_data)
mean_error2 = calculate_group_mean(grouped_smoothed_data, ref_data)
mean_error_no_groups, errors2 = calculate_mean_euclidean_error(smoothed_data, interpolated_ref_data)
mse_no_groups = calculate_mse(smoothed_data, interpolated_ref_data)
mae_no_groups = calculate_mae(smoothed_data, interpolated_ref_data)
rmse = calculate_rmse(smoothed_data, interpolated_ref_data)
print("Średni błąd najlepszych z grup wygładzonych: ", mean_error)
print("Średni błąd najlepszych z grup wygładzonych względem niezinterpolowanych: ", mean_error2)
print("MSE najlepszych z grup wygładzonych: ", mse)
#print("MAE najlepszych z grup wygładzonych: ", mae)
print("RMSE najlepszych z grup wygładzonych: ", rmsd)
print("Błąd medianowy z grup wygładzonych: ", median)
print("Średni błąd odległości euklidesowych bez uwzględniania grup danych wygładzonych: ", mean_error_no_groups)
print("Średni błąd MSE bez uwzględniania grup danych wygładzonych: ", mse_no_groups)
#print("Średni błąd MAE bez uwzględniania grup danych wygładzonych: ", mae_no_groups)
print("Średni błąd RMSE bez uwzględniania grup danych wygładzonych : ", rmse)
print("-------------------------------------")
print(len(interpolated_ref_data))
print(len(original_data))
print(len(smoothed_data))
mean_error4 = calculate_group_mean(grouped_original_data, ref_data)
mean_error_no_groups2 = calculate_mean_euclidean_error(original_data, interpolated_ref_data)
mse_no_groups2 = calculate_mse(original_data, interpolated_ref_data)
mae_no_groups2 = calculate_mae(original_data, interpolated_ref_data)
rmse_no_groups2 = calculate_rmse(original_data, interpolated_ref_data)
print("Średni błąd najlepszych z grup oryginalnych: ", mean_error3)
print("Średni błąd najlepszych z grup oryginalnych względem niezinterpolowanych: ", mean_error4)
print("MSE najlepszych z grup oryginalnych: ", mse2)
print("RMSE najlepszych z grup oryginalnych: ", rmsd2)
print("Błąd medianowy z grupy oryginalnych: ", median2)
print("Średni błąd odległości euklidesowych bez uwzględniania grup danych oryginalnych: ", mean_error_no_groups2)
print("Średni błąd MSE bez uwzględniania grup danych oryginalnych: ", mse_no_groups2)
print("Średni błąd RMSE bez uwzględniania grup danych oryginalnych: ", rmse_no_groups2)
interpolated_ref_data_np = np.array(interpolated_ref_data)
smoothed_coords_np = np.array(interpolated_smoothed_coords)
#errors = [euclidean_errors(interpolated_ref_data_np[i], smoothed_coords_np[i]) for i in range(len(interpolated_ref_data))]
print(errors)

# Tworzenie wykresu, gdzie każda grupa ma inny kolor
group_colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'orange', 'purple', 'brown']

fig, ax = plt.subplots(figsize=(10, 7))

# Rysowanie punktów oryginalnych danych z kolorami grup
for group, points in grouped_original_data.items():
    points = np.array(points)
    ax.scatter(points[:, 1], points[:, 2], label=f'Group {int(group)}', color=group_colors[int(group) % len(group_colors)])

ax.set_xlabel('Latitude')
ax.set_ylabel('Longitude')
ax.legend(bbox_to_anchor=(1.05, 1.2), loc='upper left')
plt.title('Wykres punktów oryginalnych z podziałem na grupy.')
plt.show()

# Obliczenie mediany
# median_center = np.median(original_data[:, 1:], axis=0)

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

max_distance = 0.00018

# Wykres linii
original_path = original_data[:, 1:3]
smoothed_path = smoothed_data[:, 1:3]
smoothed_data = smoothed_data[np.lexsort((smoothed_data[:, 5], smoothed_data[:, 4]))]
ref_path = interpolated_ref_data

# Rysuj linię między punktami blisko siebie
for i in range(len(original_path) - 1):
    axs[1].plot([original_data[i, 1], original_data[i + 1, 1]],  # Lat
                [original_data[i, 2], original_data[i + 1, 2]],  # Lon
                c='blue', label="Original path")

for i in range(len(smoothed_data) - 1):
    axs[1].plot([smoothed_data[i, 1], smoothed_data[i + 1, 1]],  # Lat
             [smoothed_data[i, 2], smoothed_data[i + 1, 2]],  # Lon
             c='orange')

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

# Wykres błędów errors2 dla Kalmana
axs[0].plot(np.arange(0, 28), errors, label='Errors')
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

# ax.legend(['Original Path (blue)', 'Smoothed Path (orange)', 'Index (red)'])

plt.show()