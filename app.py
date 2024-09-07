from pyhomebroker import HomeBroker
import datetime
import matplotlib.pyplot as plt
import pandas as pd
import credenciales


hb = HomeBroker(credenciales.broker)

# Authenticate with the homebroker platform
hb.auth.login(dni=credenciales.dni, user=credenciales.user,
              password=credenciales.password, raise_exception=True)

ticker01 = 'TZX27'
ticker02 = 'TZX28'

window = 20  # Ventana de días para la EMA y las bandas de Bollinger

period = 80  # Cantidad de días para el análisis

# --------------------------------------------------------------

# Get daily information from platform
data01 = hb.history.get_daily_history(
    ticker01, datetime.date(2020, 1, 1), datetime.date.today())

data02 = hb.history.get_daily_history(
    ticker02, datetime.date(2020, 1, 1), datetime.date.today())

# Convertir la columna 'date' a tipo datetime y ordenar los DataFrames
data01['date'] = pd.to_datetime(data01['date'])
data02['date'] = pd.to_datetime(data02['date'])
data01 = data01.sort_values('date')
data02 = data02.sort_values('date')

# Unir los DataFrames por la columna 'date'
merged_data = pd.merge(data01[['date', 'close']], data02[[
                       'date', 'close']], on='date', suffixes=(f'_{ticker01}', f'_{ticker02}'))

# Filtrar los últimos datos (período solicitado más ventana)
merged_data = merged_data.tail(period+window)

# Calcular el ratio de los valores de cierre
merged_data['ratio'] = merged_data[f'close_{ticker01}'] / \
    merged_data[f'close_{ticker02}']

# Calcular la media móvil exponencial (EMA) y las Bandas de Bollinger

merged_data['EMA'] = merged_data['ratio'].ewm(span=window, adjust=False).mean()
merged_data['std_dev'] = merged_data['ratio'].rolling(window=window).std()
merged_data['bollinger_upper'] = merged_data['EMA'] + \
    (merged_data['std_dev'] * 2)
merged_data['bollinger_lower'] = merged_data['EMA'] - \
    (merged_data['std_dev'] * 2)

# Filtrar el período solicitado
merged_data = merged_data.tail(period)

print(merged_data.tail())

# Graficar el ratio y las Bandas de Bollinger
plt.figure(figsize=(10, 5))

plt.plot(merged_data['date'], merged_data['ratio'],
         label=f'Ratio {ticker01}/{ticker02}', color='green')
plt.plot(merged_data['date'], merged_data['EMA'],
         label=f'EMA {window} días', color='blue')
plt.plot(merged_data['date'], merged_data['bollinger_upper'],
         label='Banda de Bollinger Superior', color='red', linestyle='--')
plt.plot(merged_data['date'], merged_data['bollinger_lower'],
         label='Banda de Bollinger Inferior', color='red', linestyle='--')

# Añadir líneas horizontales para mejorar la visualización
plt.grid(visible=True, which='both', axis='both',
         linestyle='--', linewidth=0.7)

# Añadir título y etiquetas
plt.title(
    f'Ratio de precios de cierre y Bandas de Bollinger con EMA (Últimos {period} datos)')
plt.xlabel('Fecha')
plt.ylabel('Ratio de precios de cierre')
plt.legend()

# Mostrar el gráfico
plt.show()
