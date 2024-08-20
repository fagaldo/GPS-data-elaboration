import matplotlib.pyplot as plt
import numpy as np

##
# \file kolumnowe.py
# \brief Skrypt do wizualizacji danych błędów dla różnych metod wygładzania w formie wykresów kolumnowych.
#
# Skrypt wykorzystuje dane z tabeli, tworzy wykresy kolumnowe dla różnych parametrów błędów (MED, MSE, RMSE, Mediana) oraz
# wizualizuje je na wykresach w skali logarytmicznej. Wykresy przedstawiają porównanie metod dla różnych zestawów danych.

# Dane z Tabeli 1
methods_1 = ['SMA', 'LOWESS', 'FMA', 'Filtr Kalmana', 'WMA', 'Dane oryginalne']
med_1 = [2.426e-5, 2.405e-5, 2.422e-5, 1.79e-5, 2.252e-5, 2.5073e-5]
mse_1 = [7.712e-10, 7.627e-10, 7.569e-10, 4.457e-10, 6.931e-10, 8.63e-10]
rmse_1 = [2.777e-5, 2.762e-5, 2.751e-5, 2.111e-5, 2.632e-5, 2.9378e-5]
mediana_1 = [2.208e-5, 2.207e-5, 2.198e-5, 1.623e-6, 2.014e-5, 2.2815e-5]

# Dane z Tabeli 2
methods_2 = ['SMA', 'LOWESS', 'FMA', 'Filtr Kalmana', 'WMA', 'Dane oryginalne']
med_2 = [0.0001206, 0.0001204, 0.000121, 0.000107, 0.000119, 0.0001075]
mse_2 = [2.149e-8, 2.146e-8, 2.2e-8, 1.585e-8, 2.113e-8, 1.591e-8]
rmse_2 = [0.0001466, 0.0001462, 0.0001481, 0.0001259, 0.0001453, 0.0001261]
mediana_2 = [9.843e-5, 9.83e-5, 0.00010004, 9.704e-5, 0.00010073, 0.0001008]

x = np.arange(len(methods_1))  # pozycje na osi X
width = 0.2  # szerokość kolumn

##
# \brief Tworzenie wykresów kolumnowych dla zestawów danych z Tabeli 1 i Tabeli 2.
# \details Ustawienia osi X, Y oraz etykiet. Wykresy przedstawiają wartości błędów w skali logarytmicznej.

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
ax1.set_title('Wizualizacja wartości błędów z tabeli 1')
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
ax2.set_title('Wizualizacja wartości błędów z tabeli 2')
ax2.set_xticks(x)
ax2.set_xticklabels(methods_2)
ax2.legend()

##
# \brief Funkcja dodająca wartości błędów nad kolumnami na wykresach.
# \param ax Oś, na której umieszczony jest wykres.
# \param rects Lista kolumn, do których będą dodawane wartości błędów.

def autolabel(ax, rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height:.2e}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # Przesunięcie wartości o 3 punkty w górę
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

# Ustawienie układu i wyświetlenie wykresów
fig.tight_layout()
plt.show()


# Dane z tabeli 3 i 4
methods_3 = ['SMA', 'LOWESS', 'FMA', 'Filtr Kalmana', 'WMA', 'Dane oryginalne']
med_3 = [2.7245e-5, 2.5288e-5, 2.5782e-5, 1.3462e-5, 2.5942e-5, 3.0398e-5]
mse_3 = [8.8167e-10, 7.8341e-10, 7.7622e-10, 2.3869e-10, 8.1655e-10, 1.1928e-9]
rmse_3 = [2.9692e-5, 2.7989e-5, 2.786e-5, 1.5449e-5, 2.8575e-5, 3.4536e-5]
mediana_3 = [2.7446e-5, 2.661e-5, 2.7342e-5, 1.4534e-5, 2.3687e-5, 2.8072e-5]

methods_4 = ['SMA', 'LOWESS', 'FMA', 'Filtr Kalmana', 'WMA', 'Dane oryginalne']
med_4 = [0.0001258, 0.0001174, 0.0001245, 6.505e-5, 0.0001299, 5.986e-5]
mse_4 = [2.2271e-8, 1.9782e-8, 2.2558e-8, 6.7572e-9, 2.4743e-8, 4.3091e-9]
rmse_4 = [0.0001492, 0.0001406, 0.0001501, 8.2202e-5, 0.0001573, 6.5647e-5]
mediana_4 = [0.0001086, 0.000105, 0.0001074, 5.0468e-5, 0.0001117, 5.7155e-5]

x = np.arange(len(methods_3))  # pozycje na osi X
width = 0.2  # szerokość kolumn

##
# \brief Tworzenie wykresów kolumnowych dla zestawów danych z Tabeli 1 i Tabeli 2.
# \details Ustawienia osi X, Y oraz etykiet. Wykresy przedstawiają wartości błędów w skali logarytmicznej.

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
ax1.set_title('Wizualizacja wartości błędów z tabeli 3')
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
ax2.set_title('Wizualizacja wartości błędów z tabeli 4')
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

# Ustawienie układu i wyświetlenie wykresów
fig.tight_layout()
plt.show()
