#!/usr/bin/env python
# coding: utf-8

# Personal Finance Witteke

# In[78]:


import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import plotly.express as px               #to create interactive charts
import plotly.graph_objects as go         #to create interactive charts
from jupyter_dash import JupyterDash      #to build Dash apps from Jupyter environments
import dash_core_components as dcc        #to get components for interactive user interfaces
import dash_html_components as html       #to compose the dash layout using Python structures
import webbrowser
from dash import Dash, html, Input, Output, dash_table
import nbconvert


# In[79]:


# reading data
data1 = pd.read_csv("/Users/wouterdewitte/Downloads/BE13%200635%209867%204739%202022-04-16%2015-35-43%201.csv", sep=';', skiprows = 12)
data2 = pd.read_csv("/Users/wouterdewitte/Downloads/BE13%200635%209867%204739%202022-04-16%2015-35-48%202.csv", sep=';', skiprows = 12)
data3 = pd.read_csv("/Users/wouterdewitte/Downloads/BE13%200635%209867%204739%202022-04-16%2015-35-52%203.csv", sep=';', skiprows = 12)
data4 = pd.read_csv("/Users/wouterdewitte/Downloads/BE13%200635%209867%204739%202022-04-16%2015-35-56%204.csv", sep=';', skiprows = 12)


data = pd.concat([data1, data2, data3, data4])


# In[80]:


# only necessary columns
data = data.drop(columns=['Rekening', 'Rekeninguittrekselnummer', 'Transactienummer', 'Rekening tegenpartij', 'Naam tegenpartij bevat', 'Straat en nummer', 'Postcode en plaats', 'Transactie','Valutadatum', 'BIC', 'Landcode'], axis = 1)


# In[81]:


# change data type
data["Boekingsdatum"] = pd.to_datetime(data["Boekingsdatum"], format = "%d/%m/%Y")
data["Bedrag"] = data["Bedrag"].str.replace(',', '.').astype(float)


# In[82]:


# make monthly information
data["year_month"] = data["Boekingsdatum"].dt.strftime("%Y") + ", " + data["Boekingsdatum"].dt.strftime("%m")


# In[83]:


Net_Worth_Table = data.groupby('year_month')['Bedrag'].sum().reset_index(name ='sum')
Net_Worth_Table['cumulative sum'] = Net_Worth_Table['sum'].cumsum()
Net_Worth_Chart = go.Figure(
    data = go.Scatter(x = Net_Worth_Table["year_month"], y = Net_Worth_Table["cumulative sum"]),
    layout = go.Layout(
        title = go.layout.Title(text = "Net Worth Over Time")
    )
)
Net_Worth_Chart.update_layout(
    xaxis_title = "Date",
    yaxis_title = "Net Worth (€)",
    hovermode = 'x unified'
    )
Net_Worth_Chart.update_xaxes(
    tickangle = 45)


# In[84]:


df = data[data["Bedrag"] < 0] 
df["Bedrag"] = df['Bedrag']*(-1) 
Total_Monthly_Expenses_Table = df.groupby('year_month')['Bedrag'].sum().reset_index(name = 'sum')
Total_Monthly_Expenses_Chart = px.bar(Total_Monthly_Expenses_Table, x = "year_month", y = "sum", title = "Total Monthly Expenses")
Total_Monthly_Expenses_Chart.update_yaxes(title = 'Expenses (€)', visible = True, showticklabels = True)
Total_Monthly_Expenses_Chart.update_xaxes(title = 'Date', visible = True, showticklabels = True)


# In[85]:


Total_Monthly_Table = data.groupby('year_month')['Bedrag'].sum().reset_index(name = 'sum')
Total_Monthly_Chart = px.bar(Total_Monthly_Table, x = "year_month", y = "sum", title = "Total Monthly", color = Total_Monthly_Table["sum"],
                            color_continuous_scale= ["red","green"])

Total_Monthly_Chart.update_yaxes(title = 'Savings (€)', visible = True, showticklabels = True)
Total_Monthly_Chart.update_xaxes(title = 'Date', visible = True, showticklabels = True)


# In[86]:


Data_Table = dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": True, "selectable": True} for i in data.columns
        ],
        data=data.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        row_selectable="multi",
        row_deletable=True,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current= 0,
        page_size= 10,
        style_cell_conditional=[
            {
                'if': {'column_id': c},
                'textAlign': 'left'
            } for c in ['Date', 'Region']
        ],
        style_data={
            'color': 'black',
            'backgroundColor': 'white'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(220, 220, 220)',
            }
        ],
        style_header={
            'backgroundColor': 'rgb(210, 210, 210)',
            'color': 'black',
            'fontWeight': 'bold'
        }
    )


# In[87]:


# Build App
app = JupyterDash(__name__)

app.layout = html.Div([   
    html.Div([
        html.H1(" Personal Finance Witteke",style={'text-align':'center'}),
        dcc.Graph(figure = Net_Worth_Chart),
        dcc.Graph(figure = Total_Monthly_Expenses_Chart),
        dcc.Graph(figure = Total_Monthly_Chart),
        Data_Table
    ]),    
])
    
# Run app and display result
url=webbrowser.open('http://127.0.0.1:8050/')
app.run_server(mode='external')


# In[88]:


# convert to .py
get_ipython().system('jupyter nbconvert --to script Personal_Finance.ipynb')

