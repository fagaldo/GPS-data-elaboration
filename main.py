import math
import matplotlib.pyplot as plt
import numpy as np
import re
from scipy.interpolate import interp1d
import yaml
import os
##
# \file main.py
# \brief Główny skrypt obliczający błędy i generujący wykresy.
#
# Główny skrypt odpowiedzialny za wczytanie danych, przetworzenie ich i wygenerowanie wszystkich wykresów, a także obli
# czenie wartości błędów.

##
# @brief Oblicza odległość euklidesową pomiędzy dwoma punktami.
# @param p1 Pierwszy punkt w formacie (x, y).
# @param p2 Drugi punkt w formacie (x, y).
# @return Odległość euklidesowa pomiędzy p1 a p2.
def euclidean_distance(p1, p2):
    return np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

##
# @brief Oblicza odległość Haversine pomiędzy dwoma współrzędnymi geograficznymi.
# @param coord1 Pierwsza współrzędna w formacie (szerokość, długość).
# @param coord2 Druga współrzędna w formacie (szerokość, długość).
# @return Odległość w kilometrach pomiędzy coord1 a coord2.
def haversine_distance(coord1, coord2):
    R = 6371.0  # Promień Ziemi w kilometrach

    lat1, lon1 = np.radians(coord1)
    lat2, lon2 = np.radians(coord2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    distance = R * c
    return distance

##
# @brief Interpoluje dane referencyjne, aby uzyskać określoną liczbę punktów.
# @param data Lista punktów referencyjnych w formacie (szerokość, długość).
# @param num_points Liczba punktów do uzyskania po interpolacji.
# @return Lista interpolowanych punktów w formacie (szerokość, długość).
def interpolate_reference(data, num_points):
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

# Pobranie punktów danych z plików z danymi
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

##
# @brief Grupuje dane wygładzone według grup.
# @param data Dane wygładzone w formacie (indeks, szerokość, długość, MAE, grupa, czas).
# @return Słownik, gdzie kluczem jest numer grupy, a wartością lista punktów należących do tej grupy.
def group_data(data):
    grouped_data = {}
    for point in data:
        group = point[4]
        if group not in grouped_data:
            grouped_data[group] = []
        grouped_data[group].append(point)
    return grouped_data

##
# @brief Grupuje dane oryginalne na podstawie grup z danych wygładzonych.
# @param original_data Dane oryginalne w formacie (indeks, szerokość, długość).
# @param smoothed_data Dane wygładzone w formacie (indeks, szerokość, długość, MAE, grupa, czas).
# @return Słownik, gdzie kluczem jest numer grupy, a wartością lista punktów oryginalnych należących do tej grupy.
def group_data_by_original(original_data, smoothed_data):
    grouped_data = {}
    for smooth_point, orig_point in zip(smoothed_data, original_data):
        group = smooth_point[4]  # Grupa z danych wygładzonych
        if group not in grouped_data:
            grouped_data[group] = []
        grouped_data[group].append(orig_point)
    return grouped_data

##
# @brief Oblicza błędy dla grup danych wygładzonych i oryginalnych w odniesieniu do danych referencyjnych.
# @param grouped_smoothed_data Zgrupowane dane wygładzone.
# @param grouped_original_data Zgrupowane dane oryginalne.
# @param ref_data Dane referencyjne.
# @return Krotka zawierająca średnie błędy, MSE, MAE, RMSE i mediany błędów dla danych wygładzonych i oryginalnych.
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
        # Znalezienie reprezentatywnego punktu w grupie wygładzonej najbliższego dowolnemu punktowi referencyjnemu
        rep_point_smoothed, rep_point_index = min(
            ((p[1:3], idx) for idx, p in enumerate(group_points_smoothed)),
            key=lambda pi: euclidean_distance(pi[0], find_closest_point(pi[0], ref_data))
        )
        closest_ref_point = find_closest_point(rep_point_smoothed, ref_data)

        # Znalezienie najbliższego punktu w grupie oryginalnej do reprezentatywnego punktu grupy wygładzonej
        group_points_original = grouped_original_data[group]
        closest_point_original, closest_point_index = min(
            ((p[1:3], idx) for idx, p in enumerate(group_points_original)),
            key=lambda pi: euclidean_distance(rep_point_smoothed, pi[0])
        )

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

##
# @brief Znajduje najbliższy punkt do zadanego punktu docelowego wśród punktów referencyjnych.
# @param target_point Punkt docelowy (x, y).
# @param reference_points Lista punktów referencyjnych (x, y).
# @return Najbliższy punkt referencyjny do target_point.
def find_closest_point(target_point, reference_points):
    closest_point = reference_points[0]
    min_distance = euclidean_distance(target_point, closest_point)
    for point in reference_points[1:]:
        distance = euclidean_distance(target_point, point)
        if distance < min_distance:
            min_distance = distance
            closest_point = point
    return closest_point

##
# @brief Oblicza średni błąd euklidesowy między danymi wygładzonymi a referencyjnymi.
# @param smoothed_data Dane wygładzone.
# @param ref_data Dane referencyjne.
# @return Średni błąd euklidesowy i lista błędów dla każdego punktu.
def calculate_mean_euclidean_error(smoothed_data, ref_data):
    errors = []
    total_error = 0
    num_points = len(smoothed_data)
    for i in range(num_points):
        error = euclidean_distance(smoothed_data[i][1:], ref_data[i])
        errors.append(error)
        total_error += error
    mean_error = total_error / num_points
    print("Mediana dla kolejnych punktów bez uwzględniania grup:", np.median(errors))
    return mean_error, errors

##
# @brief Oblicza średni błąd kwadratowy (MSE).
# @param smoothed_data Dane wygładzone.
# @param ref_data Dane referencyjne.
# @return Wartość MSE.
def calculate_mse(smoothed_data, ref_data):
    errors = []
    total_error = 0
    num_points = len(smoothed_data)
    for i in range(num_points):
        error = pow(euclidean_distance(smoothed_data[i][1:], ref_data[i]), 2)
        errors.append(error)
        total_error += error
    mean_error = total_error / num_points
    return mean_error

##
# @brief Oblicza pierwiastek z średniego błędu kwadratowego (RMSE).
# @param smoothed_data Dane wygładzone.
# @param ref_data Dane referencyjne.
# @return Wartość RMSE.
def calculate_rmse(smoothed_data, ref_data):
    errors = []
    total_error = 0
    num_points = len(smoothed_data)
    for i in range(num_points):
        error = pow(euclidean_distance(smoothed_data[i][1:], ref_data[i]), 2)
        errors.append(error)
        total_error += error
    mean_error = total_error / num_points
    return math.sqrt(mean_error)

# Grupowanie danych wygładzonych
grouped_smoothed_data = group_data(smoothed_data)
# Grupowanie danych oryginalnych na podstawie grup danych wygładzonych
grouped_original_data = group_data_by_original(original_data, smoothed_data)
# Obliczanie różnych błędów dla danych wygładzonych i oryginalnych
mean_error, mean_error3, mse, mse2, mae, mae2, rmsd, rmsd2, median, median2, errors = calculate_groups_errors(
    grouped_smoothed_data, grouped_original_data, interpolated_ref_data)
# Obliczanie błędów bez uwzględniania grup
mean_error_no_groups, errors2 = calculate_mean_euclidean_error(smoothed_data, interpolated_ref_data)
mse_no_groups = calculate_mse(smoothed_data, interpolated_ref_data)
rmse = calculate_rmse(smoothed_data, interpolated_ref_data)
print("Średni błąd najlepszych z grup wygładzonych: ", mean_error)
print("MSE najlepszych z grup wygładzonych: ", mse)
print("RMSE najlepszych z grup wygładzonych: ", rmsd)
print("Błąd medianowy z grup wygładzonych: ", median)
print("Średni błąd odległości euklidesowych bez uwzględniania grup danych wygładzonych: ", mean_error_no_groups)
print("Średni błąd MSE bez uwzględniania grup danych wygładzonych: ", mse_no_groups)
print("Średni błąd RMSE bez uwzględniania grup danych wygładzonych : ", rmse)
print("-------------------------------------")
print(len(interpolated_ref_data))
print(len(original_data))
print(len(smoothed_data))
mean_error_no_groups2 = calculate_mean_euclidean_error(original_data, interpolated_ref_data)
mse_no_groups2 = calculate_mse(original_data, interpolated_ref_data)
rmse_no_groups2 = calculate_rmse(original_data, interpolated_ref_data)
print("Średni błąd najlepszych z grup oryginalnych: ", mean_error3)
print("MSE najlepszych z grup oryginalnych: ", mse2)
print("RMSE najlepszych z grup oryginalnych: ", rmsd2)
print("Błąd medianowy z grupy oryginalnych: ", median2)
print("Średni błąd odległości euklidesowych bez uwzględniania grup danych oryginalnych: ", mean_error_no_groups2)
print("Średni błąd MSE bez uwzględniania grup danych oryginalnych: ", mse_no_groups2)
print("Średni błąd RMSE bez uwzględniania grup danych oryginalnych: ", rmse_no_groups2)
interpolated_ref_data_np = np.array(interpolated_ref_data)
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

# Tworzenie wykresów
fig, axs = plt.subplots(1, 2, figsize=(15, 10))

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
axs[0].plot(np.arange(0, 273), errors2, label='Errors')
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

plt.tight_layout()
plt.show()
