import requests
import json
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from pymongo import MongoClient

URI = "mongodb+srv://Countries:Country1@cluster0.0b8ol.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
try:
    client = MongoClient(URI)
    print("Conectado a MongoDB")
except Exception as e:
    print("Error de conexión:", e)
    exit()

db = client['Parcial1']
collection = db['COVID']


def obtener_datos_covid():
    url = "https://api.covidtracking.com/v1/us/daily.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Error al obtener datos:", response.status_code)
        return None

datos_covid = obtener_datos_covid()
if datos_covid:
    for dato in datos_covid:
        if not collection.find_one({"date": dato["date"]}):  
            collection.insert_one(dato)
    print("Datos guardados exitosamente en MongoDB")
else:
    print("No hay datos para guardar")

data = list(collection.find({}, {'_id': 0}))
df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
df = df.sort_values(by='date')

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Evolución de Casos de COVID-19 en EE.UU."),
    dcc.Graph(
        id="grafico-casos",
        figure=px.line(df, x='date', y='positive', title='Casos Positivos a lo Largo del Tiempo')
    ),
    dcc.Graph(
        id="grafico-muertes",
        figure=px.line(df, x='date', y='death', title='Fallecimientos Acumulados a lo Largo del Tiempo')
    )
])

if __name__ == "__main__":
    app.run_server(debug=True)