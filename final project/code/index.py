from dash import dcc, html, Input, Output, State, no_update
from app import app
from apps import home_layout, dashboard_layout, order_layout, history_layout
import dash_bootstrap_components as dbc

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [   
        dcc.Store(id='userData',data = [] ,storage_type='session'),
        dcc.Store(id='haveLogout', storage_type='session'),       
        html.Img(src='/assets/fox.png', style={'height':'100px', 'width':'100px','margin-left': '55px'}),
        html.H2("PPG, Inc.", className="display-5",style={'font-weight': 'bold'}),
        html.Hr(),
        html.P("Your comfy dream home!", className="lead"),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("DashBoard", href='/apps/dashboard_layout', active="exact",id='dashboard',style={'display': 'none'}),
                dbc.NavLink("Ask for Service", href='/apps/order_layout', active="exact", id='service',style={'display': 'none'}),
                dbc.NavLink("History", href='/apps/history_layout', active="exact", id='history',style={'display': 'none'}),                       
                html.Hr(),
                html.Label(id='showUser', style={'margin-left': 'auto','font-weight': 'bold'}),
                dbc.Button('Logout', id='logout', style={'margin-left': 'auto', 'font-weight': 'bold', 'display': 'none'}),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

@app.callback(Output('page-content', 'children'),[Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/dashboard_layout':
        return dashboard_layout.layout
    if pathname == '/apps/history_layout':
        return history_layout.layout
    if pathname == '/apps/order_layout':
        return order_layout.layout 
    if pathname == '/':
        return home_layout.layout

@app.callback(
    Output('userData', 'data'),Output('user-info', 'data',allow_duplicate=True),Output('haveLogout', 'data',allow_duplicate=True),
    Input('user-info', 'data'),
    State('user-info', 'data'),State('haveLogout', 'data'),
    prevent_initial_call=True
)
def transfer_data(user,user_info,logout_click ):
    if user_info is not None and logout_click is None :
        return user_info, user_info, None
    elif user_info is not None and logout_click is not None:
        return None, None, None        
    
@app.callback(
    [Output('showUser', 'children'),
     Output('logout', 'style'),
     Output("login", 'hidden'),
     Output("signup", 'hidden'),      
     Output('service', 'style'),
     Output('dashboard', 'style'),
     Output('history', 'style')],        
    Input('userData', 'data'),
    #prevent_initial_call=True
)    
def login_user(userData):    
    if userData and 'name' in userData:   
        logout_style = {
            'margin-left': 'auto', 
            'font-weight': 'bold', 
            'display': 'block', 
            'background-color': '#dc3545', 
            'border': 'none',
            'margin-top': '10px'
            }

        if userData.get('userrole') == 'admin':
            return userData['name'], logout_style, True, True, {'display': 'block'}, {'display': 'block'}, {'display': 'block'}

        if userData.get('userrole') == 'customer':
            return userData['name'], logout_style, True, True, {'display': 'block'}, {'display': 'none'}, {'display': 'block'}

        else:
            return userData['name'], logout_style, True, True, {'display': 'none'}, {'display': 'block'}, {'display': 'none'}

    return '',{'display': 'none'},False,False,{'display': 'none'},{'display': 'none'}, {'display': 'none'}

@app.callback(
    Output('userData', 'data',allow_duplicate=True),Output('url', 'pathname'),Output('haveLogout', 'data'),
    [Input('logout', 'n_clicks')],
    [State('userData', 'data')],
    prevent_initial_call='initial_duplicate' 
    #prevent_initial_call=True
)
def clear_user_data(n_clicks, user_data):
    if n_clicks is None:
        return no_update       
    else:
        return None, '/', n_clicks

if __name__ == '__main__':
    app.run_server(debug=False)
    
