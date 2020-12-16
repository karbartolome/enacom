import pandas as pd
import numpy as np
from datetime import date
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output
import dash_table

import plotly.express as px

color_discrete_map = {'Claro': '#f56140', 
                      'Personal': '#5e9fff', 
                      'Movistar': '#74e667'}

API_KEY='kcnt0wo0ckfEcJpf8FnRjszitdGa0ihfnSf9IeO0'
INDICADOR = 'PORTA-NUMER-MOVIL-ALTAS-MENSU'
DESCRIPCION = 'Portabilidad numérica móvil: altas mensuales por operador'
url = 'http://api.datosabiertos.enacom.gob.ar/api/v2/datastreams/'+INDICADOR+'/data.csv/?auth_key='+API_KEY 
df = pd.read_csv(url)

for i in ['Personal','Movistar','Claro','Total general']:
    df[i]=[int(j.replace(',','')) for j in df[i]]
    
df['mes']=df['Año'].astype(str)+'-'+df['Mes'].astype(str)
df['mes']=pd.to_datetime(df['mes'])


df_melt = pd.melt(df[['Año','mes', 'Personal','Claro','Movistar']], 
                  id_vars=['Año','mes'], 
                  value_vars=['Personal', 'Claro','Movistar'])

df_melt=df_melt.rename({'variable':'empresa', 'value':'cantidad'}, axis=1)


#App
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app=dash.Dash(__name__, external_stylesheets=external_stylesheets)

#Server
server = app.server

#Layout
app.layout = html.Div([
    html.H1('Enacom'), 
    dcc.Tabs([
        dcc.Tab(id='Tab1', label='Telefonía móvil',  children=[
            html.H2('Portabilidad numérica móvil: altas mensuales por operador'),
            html.Div([
                html.Div([
                    html.H4('Seleccionar una empresa'),
                    dcc.Dropdown(id='dropdown_empresa', 
                             options=[{'label': i, 'value': i} for i in df_melt.empresa.unique()],
                             multi=True,
                             value=['Personal','Movistar','Claro'],
                             clearable=False), 
                    html.H4('Seleccionar un rango de años'),
                    dcc.RangeSlider(id='range_slider_años', 
                                   min=min(df['Año']), 
                                   max=max(df['Año']),     
                                   step=1, 
                                   value=[min(df['Año']), max(df['Año'])],
                                   marks={int(i):str(i) for i in df['Año'].unique()}
                                 ),
                    dcc.Graph(id='graph_2')
                ], className='four columns'), 
                html.Div([
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    dcc.Graph(id='graph_1')
                ], className='eight columns')
                ])
            
        ]), 
        dcc.Tab(id='Tab2', label='Acceso a internet')
    ])   
]) 



@app.callback(
    [Output(component_id='graph_1', component_property='figure'),
     Output(component_id='graph_2', component_property='figure')],
    [Input(component_id='dropdown_empresa', component_property='value'),
     Input(component_id='range_slider_años', component_property='value')]
)

def update_fig(empresa, años):
    df_filt = df_melt[(df_melt['empresa'].isin(empresa)) & df_melt['Año'].between(años[0],años[1])]
    
    figure_1b = px.line(df_filt,
                     x='mes', 
                     y='cantidad', 
                     color='empresa',
                     color_discrete_map=color_discrete_map,
                     title='Evolución en la cantidad de altas por empresa',
                     hover_name='empresa')

    figura_3 = px.bar(df_filt.groupby(['empresa'], as_index=False).cantidad.sum(),
                  x="empresa", 
                  y="cantidad", 
                  color="empresa", 
                  category_orders={"empresa": ["Personal", "Movistar","Claro"]},
                  color_discrete_map=color_discrete_map,
                  title="Cantidad de altas por empresa")
    
    return [figure_1b, figura_3]


#Ejecutar
if __name__ == '__main__':
    app.run_server() 
