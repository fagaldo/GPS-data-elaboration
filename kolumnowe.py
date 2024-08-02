import matplotlib.pyplot as plt
import numpy as np

# Dane z Tabeli 11
methods_1 = ['SMA', 'LOWESS', 'FMA', 'Filtr Kalmana', 'WMA', 'Dane oryginalne']
med_1 = [3.374e-5, 3.3725e-5, 3.4033e-5, 2.2605e-5, 3.4946e-5, 3.5587e-5]
mse_1 = [1.6257e-9, 1.6246e-9, 1.6784e-9, 9.4652e-10, 1.7996e-9, 1.9281e-9]
rmse_1 = [4.032e-5, 4.03e-5, 4.0968e-5, 3.0765e-5, 4.2422e-5, 4.391e-5]
mediana_1 = [3.183e-5, 3.1821e-5, 2.9865e-5, 1.5439e-5, 3.1458e-5, 2.952e-5]

# Dane z Tabeli 12
methods_2 = ['SMA', 'LOWESS', 'FMA', 'Filtr Kalmana', 'WMA', 'Dane oryginalne']
med_2 = [0.000144, 0.0001439, 0.0001417, 0.000133, 0.0001423, 0.000134]
mse_2 = [2.8323e-8, 2.8313e-8, 2.7473e-8, 2.1475e-8, 2.7803e-8, 2.1485e-8]
rmse_2 = [0.00016829, 0.00016826, 0.0001657, 0.0001465, 0.0001667, 0.0001560]
mediana_2 = [0.00012749, 0.00012747, 0.0001261, 0.0001389, 0.0001271, 0.0001398]

x = np.arange(len(methods_1))  # pozycje na osi X
width = 0.2  # szerokość kolumn

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 14))

# Tworzenie kolumn dla każdego parametru dla Tabeli 1
rects1_1 = ax1.bar(x - 1.5*width, med_1, width, label='MED')
rects1_2 = ax1.bar(x - 0.5*width, mse_1, width, label='MSE')
rects1_3 = ax1.bar(x + 0.5*width, rmse_1, width, label='RMSE')
rects1_4 = ax1.bar(x + 1.5*width, mediana_1, width, label='Mediana')

# Dodawanie etykiet i tytułu dla Tabeli 1
ax1.set_xlabel('Metoda')
ax1.set_ylabel('Wartość błędu')
ax1.set_yscale('log')  # Ustawienie skali logarytmicznej
ax1.set_title('Wizualizacja wartości błędów z tabeli 11')
ax1.set_xticks(x)
ax1.set_xticklabels(methods_1)
ax1.legend()

# Tworzenie kolumn dla każdego parametru dla Tabeli 2
rects2_1 = ax2.bar(x - 1.5*width, med_2, width, label='MED')
rects2_2 = ax2.bar(x - 0.5*width, mse_2, width, label='MSE')
rects2_3 = ax2.bar(x + 0.5*width, rmse_2, width, label='RMSE')
rects2_4 = ax2.bar(x + 1.5*width, mediana_2, width, label='Mediana')

# Dodawanie etykiet i tytułu dla Tabeli 2
ax2.set_xlabel('Metoda')
ax2.set_ylabel('Wartość błędu')
ax2.set_yscale('log')  # Ustawienie skali logarytmicznej
ax2.set_title('Wizualizacja wartości błędów z tabeli 12')
ax2.set_xticks(x)
ax2.set_xticklabels(methods_2)
ax2.legend()

# Funkcja do dodawania wartości nad kolumnami
def autolabel(ax, rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height:.2e}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

# Dodawanie wartości nad kolumnami
autolabel(ax1, rects1_1)
autolabel(ax1, rects1_2)
autolabel(ax1, rects1_3)
autolabel(ax1, rects1_4)
autolabel(ax2, rects2_1)
autolabel(ax2, rects2_2)
autolabel(ax2, rects2_3)
autolabel(ax2, rects2_4)

fig.tight_layout()
plt.show()
# Dane z Tabeli 13
methods_3 = ['SMA', 'LOWESS', 'FMA', 'Filtr Kalmana', 'WMA', 'Dane oryginalne']
med_3 = [4.48645e-5, 4.47666e-5, 4.49794e-5, 3.51071e-5, 4.56157e-5, 4.7689e-5]
mse_3 = [2.49556e-9, 2.48883e-9, 2.50379e-9, 1.70718e-9, 2.52859e-9, 2.81510e-9]
rmse_3 = [4.995559e-5, 4.988826e-5, 5.003796e-5, 4.131814e-5, 5.028517e-5, 5.305759e-5]
mediana_3 = [4.556783e-5, 4.552557e-5, 4.558475e-5, 3.345327e-5, 4.82769e-5, 4.85030e-5]

# Dane z Tabeli 14
methods_4 = ['SMA', 'LOWESS', 'FMA', 'Filtr Kalmana', 'WMA', 'Dane oryginalne']
med_4 = [0.0002031668, 0.0002030674, 0.00020466, 0.0001962, 0.00021854, 0.0001971]
mse_4 = [6.224568e-8, 6.221389e-8, 6.322511e-8, 5.460528e-8, 7.16250e-8, 5.51674e-8]
rmse_4 = [0.00024949, 0.000249427, 0.000251446, 0.00023367, 0.00026762, 0.0002384]
mediana_4 = [0.000158516, 0.000158523, 0.000168508, 0.00015230, 0.00018144, 0.000156997]


x = np.arange(len(methods_3))  # pozycje na osi X
width = 0.2  # szerokość kolumn

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 14))

# Tworzenie kolumn dla każdego parametru dla Tabeli 3
rects3_1 = ax1.bar(x - 1.5*width, med_3, width, label='MED')
rects3_2 = ax1.bar(x - 0.5*width, mse_3, width, label='MSE')
rects3_3 = ax1.bar(x + 0.5*width, rmse_3, width, label='RMSE')
rects3_4 = ax1.bar(x + 1.5*width, mediana_3, width, label='Mediana')

# Dodawanie etykiet i tytułu dla Tabeli 3
ax1.set_xlabel('Metoda')
ax1.set_ylabel('Wartość błędu')
ax1.set_yscale('log')  # Ustawienie skali logarytmicznej
ax1.set_title('Wizualizacja wartości błędów z tabeli 13')
ax1.set_xticks(x)
ax1.set_xticklabels(methods_3)
ax1.legend()

# Tworzenie kolumn dla każdego parametru dla Tabeli 4
rects4_1 = ax2.bar(x - 1.5*width, med_4, width, label='MED')
rects4_2 = ax2.bar(x - 0.5*width, mse_4, width, label='MSE')
rects4_3 = ax2.bar(x + 0.5*width, rmse_4, width, label='RMSE')
rects4_4 = ax2.bar(x + 1.5*width, mediana_4, width, label='Mediana')

# Dodawanie etykiet i tytułu dla Tabeli 4
ax2.set_xlabel('Metoda')
ax2.set_ylabel('Wartość błędu')
ax2.set_yscale('log')  # Ustawienie skali logarytmicznej
ax2.set_title('Wizualizacja wartości błędów z tabeli 14')
ax2.set_xticks(x)
ax2.set_xticklabels(methods_4)
ax2.legend()


# Dodawanie wartości nad kolumnami
autolabel(ax1, rects3_1)
autolabel(ax1, rects3_2)
autolabel(ax1, rects3_3)
autolabel(ax1, rects3_4)
autolabel(ax2, rects4_1)
autolabel(ax2, rects4_2)
autolabel(ax2, rects4_3)
autolabel(ax2, rects4_4)

fig.tight_layout()
plt.show()
