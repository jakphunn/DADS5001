from dash import dcc, html, Input, Output, dash_table
from app import app
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from .api_service import get_orders_data
import pandas as pd
import dash

def format_timestamp(timestamp):
    return timestamp.strftime("%d/%m/%Y %H:%M")

layout = html.Div([    
    html.H1('Orders History'),
    html.Div(id='table-container')
])

@app.callback(
    Output('table-container', 'children'), 
    Input('userData', 'data'),
    State('userData', 'data')    
)
def checkUserTable(userData, userData_state):
    if userData is None:
        return dash.no_update
        
    else:       
        listOrder = get_orders_data()
        columnsOrder = ['id', 'timestamp', 'order_details', 'status']
        filtered_orders = [order for order in listOrder if order['user_id'] == userData.get('id')]

        for order in filtered_orders:
            order['timestamp'] = format_timestamp(order['timestamp'])
        
        return dash_table.DataTable(
            id='tableOrder',
            data=filtered_orders,
            columns=[{"name": col, "id": col} for col in columnsOrder],
            style_header={'backgroundColor': '#007bff','color': 'white','fontWeight': 'bold'},
            style_header_conditional=[
                {'if': {'column_id': col}, 'backgroundColor': '#007bff', 'color': 'white'} 
                for col in columnsOrder
            ],
            style_data_conditional=[
                {
                    'if': {'column_id': 'status', 'filter_query': '{status} = "waiting"'},
                    'fontWeight': 'bold',
                    'color': 'blue'
                },
                {
                    'if': {'column_id': 'status', 'filter_query': '{status} = "on-process"'},
                    'fontWeight': 'bold',
                    'color': 'orange'
                },
                {
                    'if': {'column_id': 'status', 'filter_query': '{status} = "completed"'},
                    'fontWeight': 'bold',
                    'color': 'green'
                }
            ],style_cell={'textAlign': 'left'}
        )