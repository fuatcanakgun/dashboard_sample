import os
import json
import base64
import pymssql
import dash_auth
import pandas as pd
from flask import request
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash.dash_table.Format import Format, Group, Scheme, Trim
from dash import Dash, dash_table, html, dcc, Input, Output, State

##Functions for the app
def get_user(json_file_loc):
    with open(json_file_loc, "r") as file:
        psw = json.load(file)
    return psw

def get_img():
    image_filename = 'assests/img/logo.jpg'
    encoded_image = base64.b64encode(open(image_filename, 'rb').read())
    return 'data:image/png;base64,{}'.format(encoded_image.decode())

def modal_body():
    dict = {"color": "black",
            "fontWeight": "bold",
            "font-family": "Calibri",
            "textAlign": "center",
            "font-size": "30px"
            }
    return dict

def user():
    dict = {"color": "white",
            "fontSize": "15px",
            "font-family": "Calibri",
            "border": "2px solid black",
            "borderRadius": "20px",
            "width": "auto",
            "marginLeft": "1px"
            }
    return dict

def h1():
    dict = {"color": "white",
        "textAlign": "left",
        "marginTop": "5px",
        "font-family": "Calibri",
        "font-style": "normal",
        "font-weight": "700",
        "font-size": "27px",
        "whiteSpace": "pre-line"
        }
    return dict

def img():
    dict = {"height": "66px",
        "width": "244px",
        "border": "2px solid white",
        "marginTop": "10px"
        }
    return dict

def iyi_label():
    dict = {"font-size": "30px",
            "color": "green",
            "font-family": "Calibri",
            "marginLeft":"10px",
            "fontWeight": "bold"
            }
    return dict

def table_header():
    dict = {"border": "2px solid #585858",
            "backgroundColor": "#FDBA12",
            "color": "black",
            "font-family": "Calibri",
            "font-style": "normal",
            "font-weight": "400",
            "font-size": "16px",
            "line-height": "22px",
            "textAlign": "center",
            "whiteSpace": "pre-line"
            }
    return dict

def table_cond():
    list = [{"if": {"state": "active"},
            "backgroundColor": "#FDBA12",
            "border": "2px solid #A61A17"
            },
            {"if": {"row_index": "odd"},
                "backgroundColor": "#E5E5E5",
            }]
    return list

def data_style():
    dict = {"backgroundColor": "white",
            "color": "black",
            "textAlign": "center",
            "font-family": "Calibri",
            "font-style": "normal",
            "font-weight": "400",
            "font-size": "16px",
            "line-height": "22px",
            "border": "2px solid #585858",
            "height": "auto",
            "width": "auto"
            }
    return dict

def fig():
    dict = {"position": "fixed",
            "height": "75%",
            "width": "45%"
            }
    return dict

## DB connection
conn = pymssql.connect(host='0.0.0.0', user='admin', password='admin', database='main')

## Data from DB for data tables
df = pd.read_sql("SELECT * FROM table", con=conn)

## Data tables column variable
columns = [{"name": i, "id": i} for i in df.columns]

## Tweak all options of columns for data table
for col in columns:
    if col["id"] == "date" or col["id"] == "price":
        col["editable"] = False
    if col["id"] == "date":
        col["type"] = "datetime"
    if col["id"] != "date":
        col["type"] = "numeric"
    if col["id"] == "net_price":
        col["format"] = Format(precision=0, scheme=Scheme.fixed).group(True)
    if col["id"] not in ["date","price","net_price"]:
        col["format"] = Format(precision=1, scheme=Scheme.fixed)
    if col["id"] == "variable":
        col["format"] = Format(precision=2, scheme=Scheme.fixed)

## Start the APP
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}],
    suppress_callback_exceptions=True)

app.title = "SAMPLE DASHBOARD"

## Profile selection with username & password
auth = dash_auth.BasicAuth(app, get_user("assests/credentials/user_login_info.json"))

## APP design
app.layout =\
html.Div([
    dbc.Modal([
        dbc.ModalHeader(
            dbc.ModalTitle("Attention!"), close_button=True),
            dbc.ModalBody("To save enter name", style=modal_body()),
            dbc.ModalBody(
                html.Div(dcc.Input(id="save-name", value="default", placeholder="file name holder"), style={"display": "flex", "justifyContent": "center"})),
            dbc.ModalFooter(
                dbc.Button("SAVE", id="close-button", color="success", className="btn btn-outline-success", n_clicks=0, style={"color": "white"}))],
                id="pop-up",
                centered=True,
                is_open=False),
    dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Row(html.H2(id="user", style=user())),
                dbc.Row(html.H1("SAMPLE DASHBOARD", style=h1()))], align="start", width=3),
            dbc.Col(html.Img(src=get_img(), style=img()), align = "start", width=3)],
            style={"backgroundColor":"#585858"},
            justify="between"),
        dbc.Row([    
            dbc.Col([
                dbc.Label("DATA TABLE", style=iyi_label()),
                dbc.Spinner(id="table-load", color="#FDBA12",
                children=[
                    dash_table.DataTable(
                        id="table",
                        columns=columns,
                        editable=True,
                        style_header=table_header(),
                        styletable_conditional=table_cond(),
                        styletable=data_style())]),
                html.Hr(style={"border": "1px solid black","width": "100%"})]),
            dbc.Col([
                dbc.Row([
                    dbc.Col(dbc.Button("button1", id="button", style={"color": "black","font-family": "Calibri", "marginTop": "4%","backgroundColor": "#FDBA12"}), width=2),
                    dbc.Col(dbc.Button("SAVE", id="save-button", style={"color": "black","font-family": "Calibri", "marginTop": "4%","backgroundColor": "#FDBA12"}), width=2),
                    dbc.Col(dcc.Dropdown(value="DB data", id="dropdown", style={"font-family": "Calibri", "marginTop": "4%", "backgroundColor": "#FDBA12"}), width=3)],
                justify="center"),
                dbc.Row(dcc.Graph(id="chart",style=fig()))])]),
        html.Br()], fluid=True),
        html.Div(id="none", children=[], style={"display": "none"})], 
        className="pad-row",
        style={"backgroundColor":"white"})

## Dummy callback function to get username
@app.callback(
    Output("user", "children"),
    Output("dropdown", "options"),
    Input("none", "children"))
def which_user(dummy):
    children = [x for x in os.listdir
                (f"/assests/data/{request.authorization['username']}")]
    username = str(request.authorization["username"])
    return str("User: ") + username, children

## Data selection for tables and graph
@app.callback(
    Output("table", "data"),
    Input("dropdown", "value"))
def get_savedtable_to_tables(selection):
    if selection == "DB data":
        return df.to_dict('records')
    elif selection == "data_zero":
        raise PreventUpdate
    else:
        return pd.read_csv(f"/assests/data/{request.authorization['username']}/{selection}.csv").to_dict('records')

## Update graph based on the changes on the table
@app.callback(
    Output("chart", "figure"),
    Input("table","data"),
    Input("table-load", "children"))
def get_chart(table): 
    df1 = pd.DataFrame(table)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df1["date"],y=df1["price"], name="sample", line={"dash": "solid"}, marker={"opacity": 0}))
    fig.update_layout(title="title", xaxis_title="date", yaxis_title="price",font=dict(family="Calibri", size=13, color="#A61A17"),)
    fig.update_traces(line_color="green", line_width=4, selector=dict(name="sample"))
    fig.update_layout(legend=dict(yanchor="bottom",y=1,xanchor="right",x=1),margin=dict(l=50,r=10,b=50,t=50))
    fig.update_layout(yaxis_range=[0,1])
    fig.update_yaxes(dtick=0.10)
    fig.update_xaxes(dtick="M5")
    fig.update_xaxes(tickangle = -70, title_standoff = 5, nticks=20)
    fig.update_yaxes(title_standoff = 0, nticks=20)
    return fig

# Save confirmation window
@app.callback(
    Output("pop-up","is_open"),
    Input("save-button", "n_clicks"),
    Input("close-button", "n_clicks"),
    State("pop-up","is_open"),
    State("table","data"),
    State("save-name", "value"),
    prevent_initial_call=True)
def save(n1, n2, is_open, table, filename):
    if is_open:
        try:
            os.makedirs(f"/assests/data/{request.authorization['username']}/{filename}")
        except:
            pass
        df = pd.DataFrame(table).fillna(0)
        df.to_csv(f"/assests/data/{request.authorization['username']}/{filename}.csv")
    if n1 or n2:
        return not is_open
    return is_open

## Simulate the scenario with loading component
@app.callback(
    Output("table-load", "children"),
    Output("dropdown", "value"),
    Input("button", "n_clicks"), 
    State("table", "data"),
    prevent_initial_call=True)
def save(n, table):
    df1 = pd.DataFrame(table)
    table = df1 * 2
    table = table.to_dict('records')
    if n:
        return\
        dash_table.DataTable(
            id="table",
            data=table,
            columns=columns,
            editable=True,
            style_header=table_header(),
            styletable_conditional=table_cond(),
            styletable=data_style()),\
\
        "sample data"

## Start the APP server
if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0")
