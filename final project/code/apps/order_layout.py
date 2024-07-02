from dash import dcc, html, Input, Output
from app import app
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from .api_service import save_order_to_postgres, translator
from dash.exceptions import PreventUpdate

layout = html.Div([    
    dbc.Alert("Send message success!", id="order_success_alert", is_open=False, duration=4000),
    html.H1('Let us help you'),  
    html.Div([               
        dcc.Textarea(id='customer_order', style={'width': '100%', 'height': 300}),
        dbc.Button("Submit", id="submit", className="ms-auto", n_clicks=0)                     
    ])    
])  

@app.callback(
    [Output('customer_order', 'value'),Output('order_success_alert', 'is_open')],
    Input('submit', 'n_clicks'), 
    [State('customer_order', 'value'), State('userData', 'data')],
    prevent_initial_call=True
)
def save_order(n_clicks, order_details, user):
    if n_clicks is None:
        raise PreventUpdate

    else:        
        zeroClass = translator(order_details)
        type_value = zeroClass['type'] ,
        scores_value = "{:.2f}".format(zeroClass['scores'] * 100),
        user_id = user.get('id')
        if user_id is not None:
            save_order_to_postgres(user_id=user_id, order_details=order_details, status='waiting', types=type_value, percent=scores_value)                      
            return '', True
        else:
            raise PreventUpdate
