from dash import html,dcc
import dash_bootstrap_components as dbc
from app import app
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import dash
import json
from dash.exceptions import PreventUpdate
from .api_service import regis_data_to_postgres, get_accounts_data

app.css.append_css({
    'external_url': 'styles.css'
})

geojson_path = r"D:\projectTool\zeroClass\us-states.json"
with open(geojson_path) as f:
    geojson = json.load(f)

inputStyte = {
    "width": "100%",
    "padding": "12px 20px",
    "margin": "8px 0",
    "display": "inline-block",
    "border": "1px solid",
    "border-radius": "4px",
    "box-sizing": "border-box",
}
states = [feature['properties']['name'] for feature in geojson['features']]
optionsState = [{"label": state, "value": state} for state in states]

layout = html.Div([    
    html.Div(
    [   
        dcc.Store(id='user-info',data = [] ,storage_type='session'),
        dbc.Alert("Register Member success!", id="regis_alert", is_open=False, duration=4000),        
        html.Div([
            dbc.Button("Login", id="login", n_clicks=0, style={'position': 'relative', 'top': '10px', 'right': '30px'}),
            dbc.Button("Sign up", id="signup", n_clicks=0, style={'position': 'relative', 'top': '10px', 'right': '10px'}
        )], style={'text-align': 'right'}),        
        #html.Div([            
        #    html.Img(src='/assets/image1.png', style={'height':'96%', 'width':'96%'}),            
        #]),
        html.Br(),
        dbc.Carousel(
            items=[
                {"key": "1", "src": "/assets/1.png"},
                {"key": "2", "src": "/assets/2.png"},
                {"key": "3", "src": "/assets/3.png"},
                {"key": "4", "src": "/assets/4.png"},
                {"key": "5", "src": "/assets/5.png"},
                {"key": "6", "src": "/assets/6.png"},
                {"key": "7", "src": "/assets/7.png"},
                {"key": "8", "src": "/assets/8.png"},
                {"key": "9", "src": "/assets/9.png"},
                {"key": "10", "src": "/assets/10.png"},
                {"key": "11", "src": "/assets/11.png"},
                {"key": "12", "src": "/assets/12.png"},
                {"key": "13", "src": "/assets/13.png"},
                {"key": "14", "src": "/assets/14.png"},
                {"key": "15", "src": "/assets/15.png"},
                {"key": "16", "src": "/assets/16.png"},
                {"key": "17", "src": "/assets/17.png"}
            ],
            controls=True,
            indicators=False,
        ),

        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Register Member")),
                dbc.ModalBody([            
                    html.Form([
                        dbc.Label("Username"),
                        dbc.Input(id="username", placeholder="Input your username...", type="text",style=inputStyte,required=True),
                        dbc.Label("Password"),
                        dbc.Input(id="password", placeholder="Input your password...", type="password",style=inputStyte,required=True),
                        dbc.Label("Fullname"),
                        dbc.Input(id="name", placeholder="Input your name...", type="text",style=inputStyte,required=True),
                        dbc.Label("Email"),
                        dbc.Input(id="email", placeholder="Input your email...", type="email",style=inputStyte),
                        dbc.Label("State"),
                        dbc.Select(id="country-select",options=optionsState),
                        html.Div(id='map-container')
                    ])         
                ],style={"padding": "20px"}),               
                dbc.ModalFooter(
                    html.Div([
                            dbc.Button("Submit", id="submit", className="me-3", n_clicks=0,style={'margin-right': '10px'}),
                            dbc.Button("Close", id="close", n_clicks=0)                            
                    ], className="d-flex justify-content-end")                    
                ),
            ],
            id="modal",size="lg",is_open=False,
        ),

        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Login")),
                dbc.ModalBody([            
                    html.Form([
                        dbc.Label("Username"),
                        dbc.Input(id="username2", placeholder="Input your username...", type="text",style=inputStyte,required=True),
                        dbc.Label("Password"),
                        dbc.Input(id="password2", placeholder="Input your password...", type="password",style=inputStyte,required=True),
                        html.Label('Login failed, please check your username and password are correct.', id='loginfail', hidden=True, style={'color' :'red'})
                    ])         
                ],style={"padding": "20px"}),               
                dbc.ModalFooter(
                    html.Div([
                        dbc.Button("Submit", id="submit2", className="ms-auto", n_clicks=0,style={'margin-right': '10px'}),
                        dbc.Button("Close", id="close2", n_clicks=0)                            
                    ], className="d-flex justify-content-end")                    
                ),
            ],
            id="modal2",size="lg",is_open=False,
        )
    ])   
])

# ---------------------- Open Model signup -------------------------
@app.callback(
    Output("modal", "is_open",allow_duplicate=True),
    [Input("signup", "n_clicks"), Input("close", "n_clicks")],
    State("modal", "is_open"),
    prevent_initial_call='initial_duplicate'
    #prevent_initial_call=True
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# ---------------------- Clear lable Close Model Login -------------------------
@app.callback(
    [Output('username', 'value'), Output('password', 'value'), Output('name', 'value'), Output('email', 'value'), Output('country-select', 'value')],
    [Input('close', 'n_clicks')],
    [State('modal', 'is_open')],
    #prevent_initial_call=True
)
def reset_input(close_clicks, is_open):
    if close_clicks and is_open:
        return '', '', '', '', ''
    return dash.no_update 

# ---------------------- Model signup -------------------------
@app.callback(
    [Output('modal', 'is_open'), Output('regis_alert', 'is_open')],
    [Input('submit', 'n_clicks')],
    [State('username', 'value'), State('password', 'value'), State('name', 'value'), State('email', 'value'), State('country-select', 'value')],
    prevent_initial_call=True
)
def form_submission(n_clicks, username, password, fullname, email, address):
    if n_clicks is None:
        raise PreventUpdate
    else:
        regis_data_to_postgres(username, password, fullname, email, address)        
        return False, True

# ---------------------- Open Model Login -------------------------
@app.callback(
    Output("modal2", "is_open",allow_duplicate=True),
    [Input("login", "n_clicks"),Input("close2", "n_clicks")],
    [State("modal2", "is_open")],
    prevent_initial_call='initial_duplicate'
    #prevent_initial_call=True
)
def toggle_modalLogin(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# ---------------------- Clear lable Close Model Login -------------------------
@app.callback(
    [Output('username2', 'value'), Output('password2', 'value'), Output('loginfail', 'hidden',allow_duplicate=True)],
    [Input('close2', 'n_clicks')],
    [State('modal2', 'is_open')],
    prevent_initial_call='initial_duplicate'
    #prevent_initial_call=True
)
def reset_input(close_clicks, is_open):
    if close_clicks and is_open:
        return '', '', True
    return dash.no_update 

# ---------------------- Model Login -------------------------
@app.callback(
    [Output('modal2', 'is_open'), Output('loginfail', 'hidden'), Output('user-info', 'data')],
    Input('submit2', 'n_clicks'),
    [State('username2', 'value'),State('password2', 'value'),State('user-info', 'data')],
    prevent_initial_call=True
)
def checkUserPassword(n_clicks, username, password, user_info):
    if n_clicks is None:   
        return PreventUpdate

    allAccount = get_accounts_data()
    for account in allAccount:
        if username == account['username'] and password == account['password']:
            user_info = {'id': account['id'],'name': account['name'], 'userrole': account['userrole']}
            print("Data : ",user_info)
            return False, True, user_info    

    return True, False, '' 

# ---------------------- America Map -------------------------
@app.callback(
    Output('map-container', 'children'),
    [Input('country-select', 'value')]
)

def update_map(selected_state):
    fig = go.Figure()

    fig.add_trace(
        go.Choropleth(
            locations=[state for state in states],
            z=[1] * len(states),
            locationmode='USA-states',
            marker_line_color='white',
            marker_line_width=0.5,
            colorscale='burgyl',
            showscale=False           
        )
    )

    # Highlight selected state with blue color
    if selected_state:
        fig.add_trace(
            go.Choropleth(
                geojson=geojson,
                locations=[selected_state],
                featureidkey='properties.name',
                z=[2],
                colorscale='Bluyl',               
                marker_line_width=0,    
                showscale=False                
            )
        )

    fig.update_layout(
        geo_scope='usa',
        height=300,
        margin={"r":0,"t":0,"l":0,"b":0}
    )

    return dcc.Graph(figure=fig,config={'displayModeBar': False})
