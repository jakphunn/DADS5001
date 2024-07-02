from dash import dcc, html, Input, Output, State, no_update, callback_context,ALL
import plotly.express as px
import json
from app import app
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from .api_service import get_accounts_data, get_orders_data, update_order_to_postgres, active_send_line
import pandas as pd

geojson_path = r"D:\projectTool\zeroClass\us-states.json"
with open(geojson_path) as f:
    geojson = json.load(f)

states = [feature['properties']['name'] for feature in geojson['features']]
optionsState = [{"label": state, "value": state} for state in states]

listOrderAll = get_orders_data()
timeOrder = pd.DataFrame(listOrderAll)
allYearInOrder = pd.to_datetime(timeOrder['timestamp']).dt.year.unique()

colors_list = {
    'waterworks': 'rgb(31, 119, 180)',
    'electrical': 'rgb(255, 127, 14)',
    'structural': 'rgb(148, 103, 189)',
    'arborist': 'rgb(44, 160, 44)',
    'pesticide': 'rgb(214, 39, 40)'
}

layout = html.Div([  
    dbc.Alert(id="msgStatus", is_open=False, duration=4000),
    html.Div([     
        html.Div([   
            html.Div([
                html.H3("Location"),
                html.P(id='labelLocation'),
                html.Div(id='map'),
            ], style={'width': '50%', 'display': 'inline-block'}),
                 
            html.Div([                               
                html.Div(id='table-problem')    
            ], style={'width': '50%', 'display': 'inline-block'}),
        ], style={'display': 'flex', 'flex-direction': 'row'})
    ], className='row', style={'height':'50%'}),    
    html.Br(),
    html.Br(),
    html.Div([             
        html.Div([   
            html.Div([
                html.H3("Pie Chart"),            
                html.Div(id='pieChart'),
            ], style={'width': '50%', 'display': 'inline-block'}),
                 
            html.Div([
                html.H3("Bar Chart"),
                html.Div([
                    html.Span('Year: ', style={'padding': '5px','backgroundColor': '#f0f0f0'}),html.Div([dcc.Dropdown( id='year-dropdown', options=[{'label': str(year), 'value': year} for year in allYearInOrder])], style={'width': '50%', 'display': 'inline-block','margin-right': '10px'}),
                    #html.Span('State: ',style={'padding': '5px','backgroundColor': '#f0f0f0'}),html.Div([dcc.Dropdown( id='state-dropdown', options=[{'label': str(state), 'value': state} for state in states])], style={'width': '50%', 'display': 'inline-block'})  
                ], style={'display': 'flex', 'flex-direction': 'row'}),               
                html.Div(id="barChart")
            ], style={'width': '50%', 'display': 'inline-block'}),
        ], style={'display': 'flex', 'flex-direction': 'row'})
    ], className='row', style={'height':'50%'}),
])

@app.callback(
    Output('map', 'children'),Output('labelLocation', 'children'),
    Input('userData', 'data'),
    State('userData', 'data')    
)
def update_map(userData, userData2):
    if userData is None:
        return '',''
    else:        
        listUser = get_accounts_data()
        listOrder = get_orders_data()
        role = userData.get('userrole')
        filterOrders = [order for order in listOrder if order['type'] == userData.get('userrole')]
        if filterOrders:
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
           
            state_problems = {}         
            for userId in filterOrders:             
                locationProblems = [user['address'] for user in listUser if user['id'] == userId['user_id']]
                for location in locationProblems:
                    state = location.split(',')[-1].strip()
                    state_problems[state] = state_problems.get(state, 0) + 1

                for state, count in state_problems.items():
                    fig.add_trace(
                        go.Choropleth(
                            geojson=geojson,
                            locations=[state],
                            featureidkey='properties.name',
                            z=[count],                       
                            colorscale=[[0, colors_list[role]], [1, colors_list[role]]] ,
                            marker_line_width=0,
                            showscale=False,
                            name='',     
                            customdata=[state]*len(locationProblems),                       
                        )
                    )
              
            fig.update_layout(
                geo_scope='usa',
                height=300,
                margin={"r":0,"t":0,"l":0,"b":0},
                dragmode=False          
            )
        else:
            return '',''

        return dcc.Graph(id='map-graph',figure=fig, config={'displayModeBar': False,"scrollZoom": False}), "Type : " + role

@app.callback(
    Output('table-problem', 'children'),
    Input('map-graph', 'clickData'),
    State('userData', 'data'),
    #prevent_initial_call=True
)
def displayTable(clickData, userData):
    if clickData is not None:
        listUser = get_accounts_data()
        listOrder = get_orders_data()
        state_name = clickData['points'][0]['location']
        user_role = userData.get('userrole', '')                
        workTypeFiltered = [order for order in listOrder if order['type'] == user_role]        
        user_ids = {order['user_id'] for order in workTypeFiltered} 
        userLocation = [user for user in listUser if user['address'] == state_name and user['id'] in user_ids]

        details = []
        for user in userLocation:
            for order in workTypeFiltered:
                if order['user_id'] == user['id']:
                    details.append({
                        'Order ID': order['id'],
                        'User ID': user['id'],
                        'Name': user['name'],
                        'Timestamp': order['timestamp'].strftime("%d/%m/%Y %H:%M"),
                        'Order Details': order['order_details'],
                        'Status': order['status'],
                        'Change Status': '',
                        'Prediction': order['percent']
                    })

        if details:
            return html.Div([
                html.H3(f"Order details at {state_name}"),
                html.Table([
                    html.Thead(
                        html.Tr([
                            html.Th(col, style={'border': '1px solid black', 'padding': '5px','backgroundColor': f'{colors_list[user_role]}','color': 'white'}) 
                            for col in details[0].keys()
                        ])
                    ),
                    html.Tbody([
                        html.Tr([
                            html.Td(detail['Order ID'], style={'border': '1px solid black', 'padding': '5px'}),
                            html.Td(detail['User ID'], style={'border': '1px solid black', 'padding': '5px'}),
                            html.Td(detail['Name'], style={'border': '1px solid black', 'padding': '5px'}),
                            html.Td(detail['Timestamp'], style={'border': '1px solid black', 'padding': '5px'}),
                            html.Td(detail['Order Details'], style={'border': '1px solid black', 'padding': '5px'}),
                            html.Td(detail['Status'], style={'border': '1px solid black', 'padding': '5px', 
                                                             'color': 'blue' if detail['Status'] == 'waiting' else
                                                                      'orange' if detail['Status'] == 'on-process' else
                                                                      'green' if detail['Status'] == 'completed' else
                                                                      'black'}),
                            html.Td(                               
                                html.Button("Active",                                             
                                            id={'type': 'activeButton', 'index': detail['Order ID']},
                                            value = detail['Order ID'],                                             
                                            type='button',
                                            style={'backgroundColor': 'green' if detail['Status'] == 'waiting' else 'white',
                                                   'color': 'white' if detail['Status'] == 'waiting' else 'grey'},
                                            disabled=(detail['Status'] != 'waiting')
                                            ), 
                                style={'border': '1px solid black', 'text-align': 'center'}
                            ),
                            html.Td(
                                html.Button("Show", 
                                            id={'type': 'pieButton', 'index': detail['Order ID']},                                             
                                            value=detail['Prediction'],
                                            style={'backgroundColor': 'blue', 'color': 'white'}), 
                                style={'border': '1px solid black', 'text-align': 'center'}
                            )
                        ])
                        for detail in details
                    ])
                ], style={'width': '100%', 'border-collapse': 'collapse'})
            ])
        else:
            return html.Div([
                html.H3(f"No details available for {state_name}")
            ])
    return html.Div([html.H4("Click on a state to see details.")])

@app.callback(
    Output('msgStatus', 'is_open'),Output('msgStatus', 'children'),
    [Input({'type': 'activeButton', 'index': ALL}, 'n_clicks')],
    State('userData', 'data')
    #prevent_initial_call=True
)
def saveStatus(n_clicks , userData):
    if n_clicks == [None]or not any(n_clicks):
        return no_update

    else:
        ctx = callback_context
        if not ctx.triggered:
            return no_update
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        order_id = json.loads(button_id)['index']  

        listUser = get_accounts_data()
        listOrder = get_orders_data()
        user_role = userData.get('userrole', '')
        filterOrders = [order for order in listOrder if order['type'] == userData.get('userrole') and order['id'] == order_id ]        
        customerName = [user['name'] for order in filterOrders for user in listUser if user['id'] == order['user_id']]
        locationProblems = [user['address'] for order in filterOrders for user in listUser if user['id'] == order['user_id']]

        details = {
            'Order ID': [order['id'] for order in filterOrders],
            'User ID': [order['user_id'] for order in filterOrders],
            'Name': customerName,
            'Timestamp': [order['timestamp'].strftime("%d/%m/%Y %H:%M") for order in filterOrders],
            'Order Details': [order['order_details'] for order in filterOrders],
            'Prediction': [order['percent'] for order in filterOrders],
            'Location' : locationProblems
        }

        try:
            update_order_to_postgres(order_id=order_id, status='on-process')
            active_send_line(user_role,details)

            return True, f"Order {order_id} status updated to 'on-process'."
        except Exception as e:
            return True, f"Failed to update Order {order_id}: {str(e)}"

@app.callback(
    Output('pieChart', 'children'),
    [Input({'type': 'pieButton', 'index': ALL}, 'n_clicks'),
     Input({'type': 'pieButton', 'index': ALL}, 'value')],
    State('userData', 'data'),
    #prevent_initial_call=True
)
def showPiePredict(n_clicks, values, userData):
    if not any(n_clicks):
        return []

    ctx = callback_context
    if not ctx.triggered:
        return []
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    order_id = json.loads(button_id)['index']           
    value = ctx.inputs['{"index":' + str(order_id) + ',"type":"pieButton"}.value']

    data = []
    labels = ['waterworks', 'electrical', 'structural', 'arborist', 'pesticide']
    sizes = [1] * len(labels)
    exceptionType = userData.get('userrole', '') 

    colors = [colors_list[exceptionType] if label == exceptionType else 'lightgrey' for label in labels]
    pull_values = [0.05 if label == exceptionType else 0 for label in labels]
    fig = go.Figure()
    fig.add_trace(go.Pie(labels=labels, values=sizes, hole=0.5, marker=dict(colors=colors),pull=pull_values, textinfo='none'))
    fig.update_layout(
        legend=dict(font=dict(size=16),x = 0,y = 1),
        title_text=f"Predict departemnt for order : {order_id}", 
        title_x=0.5)
    
    fig.add_annotation(
        x=0.5,
        y=0.5,
        text=f'Predict Value =\n {value}%',
        showarrow=False,
        font=dict(
            size=16,
            color="black"
        )       
    )

    return html.Div(
        id='pieChart',
        children=[
            dcc.Graph(
                id={'type': 'pieChart', 'index': order_id},
                figure=fig,
                style={'width': '100%', 'height': '600px'}
            )
        ]
    ) 

@app.callback(
    Output('barChart', 'children'),
    Input('year-dropdown', 'value'),    
    State('userData', 'data'),
    #prevent_initial_call=True
)
def totalProblemYear(year, userData):
    if year is None:
        return no_update

    listOrder = get_orders_data()
    user_role = userData.get('userrole', '')
    filterOrders = [order for order in listOrder if order['type'] == userData.get('userrole')]

    df = pd.DataFrame(filterOrders)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df[df['timestamp'].dt.year == year]
    df = df[df['type'] == user_role]

    df['month'] = df['timestamp'].dt.month
    result = df.groupby('month').size().reset_index(name='problem_count')

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    result['month_name'] = result['month'].apply(lambda x: months[x-1])

    total = sum(result.values[:, 1])
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=result['month_name'],
        y=result['problem_count'],
        name=f'Problems Reported in {year} for Role: {user_role}',
        marker_color=colors_list[user_role]
    ))
    fig.update_layout(title=f'Annual {user_role} Problems : {total}',
                      xaxis_title='Month',
                      yaxis_title='Problem Count')

    return html.Div([   
        dcc.Graph(figure=fig)
    ])
