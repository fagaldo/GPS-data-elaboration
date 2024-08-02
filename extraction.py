import matplotlib.pyplot as plt
import numpy as np
import re
from scipy.interpolate import interp1d, CubicSpline


# Function to calculate the Haversine distance between two geographical coordinates
def haversine_distance(coord1, coord2):
    R = 6371.0  # Earth radius in kilometers
    lat1, lon1 = np.radians(coord1)
    lat2, lon2 = np.radians(coord2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distance = R * c
    return distance

# Function to interpolate additional reference points to obtain evenly spaced points along the path
def interpolate_reference(data, num_points):
    # Calculate cumulative distances
    distances = [0]
    total_distance = 0
    for i in range(1, len(data)):
        total_distance += haversine_distance(data[i - 1], data[i])
        distances.append(total_distance)

    # Create an interpolating function based on cumulative distances
    distances = np.array(distances)
    f_lat = CubicSpline(distances, data[:, 0])
    f_lon = CubicSpline(distances, data[:, 1])

    # Generate new set of evenly spaced distances
    new_distances = np.linspace(0, total_distance, num_points)

    # Interpolate latitudes and longitudes based on the new set of distances
    new_lats = f_lat(new_distances)
    new_lons = f_lon(new_distances)

    interpolated_data = np.column_stack((new_lats, new_lons))
    return interpolated_data
# Reading the data from file
def read_data(file_path):
    ref_data = []
    with open(file_path, "r") as file:
        for line in file:
            match = re.search(r'([\d.]+), ([\d.]+)', line)
            if match:
                lon = float(match.group(1))
                lat = float(match.group(2))
                ref_data.append((lat, lon))
    return np.array(ref_data)

# Main function
def main():
    ref_data = read_data("referencyjneT4.txt")
    interpolated_ref_data = np.array(interpolate_reference(ref_data, 700))

    fig, axs = plt.subplots(1, 1, figsize=(15, 10))
    axs.scatter(interpolated_ref_data[:, 1], interpolated_ref_data[:, 0], label='Referential points', s=10)
    axs.set_xlabel('Latitude')
    axs.set_ylabel('Longitude')
    axs.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
