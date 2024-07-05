import dask.dataframe as dd
import streamlit as st
import pandas as pd
import requests
import re
import time
from prometheus_client import Summary, Gauge, generate_latest, CollectorRegistry
import threading
from multiprocessing import Pool, Manager

# Crear un registro personalizado
registry = CollectorRegistry()

# Crear métricas de Prometheus en español
REQUEST_TIME = Summary('tiempo_procesamiento_solicitud_segundos', 'Tiempo invertido procesando la solicitud', registry=registry)
DATAFRAME_UPDATE_TIME = Summary('tiempo_actualizacion_dataframe_segundos', 'Tiempo invertido actualizando el DataFrame', registry=registry)
REQUEST_SUCCESS = Gauge('exito_solicitud', 'Indica si la solicitud fue exitosa (1) o no (0)', registry=registry)


# Iniciar el servidor de Prometheus en un hilo separado
def start_prometheus_server():
    from prometheus_client import start_http_server
    start_http_server(8000)

threading.Thread(target=start_prometheus_server).start()

st.title("Geolocalización y clima de la ciudad de Lima")

# URL de la API de WeatherAPI
url = "http://api.weatherapi.com/v1/current.json"
params = {
    'key': '9e8bd3955fa648be86f210808241006',
    'q': 'lima',  # lugar donde revisar el clima
    'aqi': 'yes'  # calidad de aire
}

def fetch_weather_data(url, params, return_dict):
    # Medir el tiempo de la solicitud
    start_time = time.time()
    response = requests.get(url, params=params)
    elapsed_time = time.time() - start_time
    REQUEST_TIME.observe(elapsed_time)
    return_dict['response'] = response

def update_dataframe(data, archivo_csv, return_dict):
    # Medir el tiempo de actualización del DataFrame
    start_time = time.time()
    
    # Crear el DataFrame
    df = pd.DataFrame([data])

    # Leer el archivo CSV existente o crear uno nuevo si no existe
    try:
        df_historico = dd.read_csv(archivo_csv)
    except FileNotFoundError:
        df_historico = dd.from_pandas(pd.DataFrame(), npartitions=1)

    # Convertir el DataFrame actual en un Dask DataFrame
    df_dask = dd.from_pandas(df, npartitions=1)

    # Apilar los nuevos datos al DataFrame histórico
    df_actualizado = dd.concat([df_historico, df_dask], axis=0)

    # Guardar el DataFrame actualizado en el archivo CSV
    df_actualizado.to_csv(archivo_csv, single_file=True, index=False)

    elapsed_time = time.time() - start_time
    DATAFRAME_UPDATE_TIME.observe(elapsed_time)

    return_dict['archivo_csv'] = archivo_csv

# Ejecutar las solicitudes de manera paralela utilizando multiprocessing
manager = Manager()
return_dict = manager.dict()

with Pool(processes=2) as pool:
    # Obtener los datos del clima y actualizar el DataFrame en paralelo
    pool.apply_async(fetch_weather_data, (url, params, return_dict))
    pool.close()
    pool.join()

response = return_dict['response']

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    REQUEST_SUCCESS.set(1)
    # Convertir la respuesta a formato JSON
    json_data = response.json()

    # Extraer los datos de 'location' y 'current' y combinarlos
    data = {**json_data['location'], **json_data['current'], **json_data['current']['condition'], **json_data['current']['air_quality']}
    # Eliminar claves innecesarias que han sido aplanadas
    data.pop('condition', None)
    data.pop('air_quality', None)

    archivo_csv = 'historico_datos.csv'

    # Actualizar el DataFrame en paralelo
    with Pool(processes=1) as pool:
        pool.apply_async(update_dataframe, (data, archivo_csv, return_dict))
        pool.close()
        pool.join()

    # Leer el archivo CSV actualizado para mostrarlo en Streamlit
    df_mostrar = dd.read_csv(return_dict['archivo_csv']).compute()

    st.header('Tabla del Historial de datos')
    st.dataframe(df_mostrar)

    st.header('Json en tiempo real de geolocalización y clima de la ciudad de Lima')
    st.json(json_data)
else:
    REQUEST_SUCCESS.set(0)
    st.error(f"Error: {response.status_code}")

# Extraer y mostrar métricas de Prometheus
st.header("Métricas de Prometheus")
metrics_data = generate_latest(registry).decode('utf-8')


# Función para interpretar y mostrar las métricas
def interpretar_metricas(metrics_data):
    metricas_interpretadas = []

    # Expresión regular para extraer el nombre y el valor de las métricas
    regex = r'^([^\s]+)\s+([^\s]+)\s*$'

    lines = metrics_data.strip().split('\n')
    for line in lines:
        if line.startswith('#'):
            # Ignorar líneas de ayuda y tipo
            continue
        match = re.match(regex, line)
        if match:
            nombre_metrica = match.group(1)
            valor_metrica = match.group(2)
            if nombre_metrica.endswith('_count'):
                metrica_explicacion = f"El número de eventos observados para {nombre_metrica}: {valor_metrica}"
            elif nombre_metrica.endswith('_sum'):
                metrica_explicacion = f"La suma total para {nombre_metrica}: {valor_metrica} segundos"
            elif nombre_metrica.endswith('_created'):
                metrica_explicacion = f"Timestamp de creación para {nombre_metrica}: {valor_metrica}"
            elif nombre_metrica == 'exito_solicitud':
                if valor_metrica == '1.0':
                    metrica_explicacion = "La última solicitud fue exitosa."
                else:
                    metrica_explicacion = "La última solicitud no fue exitosa."
            else:
                metrica_explicacion = f"Valor de {nombre_metrica}: {valor_metrica}"

            metricas_interpretadas.append(metrica_explicacion)

    return metricas_interpretadas


metricas_explicadas = interpretar_metricas(metrics_data)
# Mostrar las métricas interpretadas
texto = ""
for metrica in metricas_explicadas:
    texto += metrica + "\n\n"

st.markdown(texto)