# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# Personal Finance Witteke

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
from dash import Dash, html, Input, Output, State, dash_table
import nbconvert
import base64
import io

# +
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = JupyterDash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
])

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            parse_contents.df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')),sep = ";")
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            parse_contents.df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            parse_contents.df.to_dict('records'),
            [{'name': i, 'id': i} for i in parse_contents.df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

if __name__ == '__main__':
    url=webbrowser.open('http://127.0.0.1:8050/')
    app.run_server(debug=True)
# -

data = parse_contents.df

# only necessary columns
data = data.drop(columns=['Rekening', 'Rekeninguittrekselnummer', 'Transactienummer', 'Rekening tegenpartij', 'Naam tegenpartij bevat', 'Straat en nummer', 'Postcode en plaats', 'Transactie','Valutadatum', 'BIC', 'Landcode'], axis = 1)

# change data type
data["Boekingsdatum"] = pd.to_datetime(data["Boekingsdatum"], format = "%d/%m/%Y")
data["Bedrag"] = data["Bedrag"].str.replace(',', '.').astype(float)

# make monthly information
data["year_month"] = data["Boekingsdatum"].dt.strftime("%Y") + ", " + data["Boekingsdatum"].dt.strftime("%m")

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

df = data[data["Bedrag"] < 0] 
df["Bedrag"] = df['Bedrag']*(-1) 
Total_Monthly_Expenses_Table = df.groupby('year_month')['Bedrag'].sum().reset_index(name = 'sum')
Total_Monthly_Expenses_Chart = px.bar(Total_Monthly_Expenses_Table, x = "year_month", y = "sum", title = "Total Monthly Expenses")
Total_Monthly_Expenses_Chart.update_yaxes(title = 'Expenses (€)', visible = True, showticklabels = True)
Total_Monthly_Expenses_Chart.update_xaxes(title = 'Date', visible = True, showticklabels = True)

# +
Total_Monthly_Table = data.groupby('year_month')['Bedrag'].sum().reset_index(name = 'sum')
Total_Monthly_Chart = px.bar(Total_Monthly_Table, x = "year_month", y = "sum", title = "Total Monthly", color = Total_Monthly_Table["sum"],
                            color_continuous_scale= ["red","green"])

Total_Monthly_Chart.update_yaxes(title = 'Savings (€)', visible = True, showticklabels = True)
Total_Monthly_Chart.update_xaxes(title = 'Date', visible = True, showticklabels = True)
# -

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
        style_cell={
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'maxWidth': 0
        },
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

# +
# Build App
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
app.run_server(mode='external')
# -


