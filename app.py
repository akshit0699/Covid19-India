import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime, timedelta
import dash_table
from dash.dependencies import Input, Output

import pandas as pd
import plotly_express as px
import numpy as np
import requests

import plotly.graph_objects as go


app = dash.Dash(__name__,external_stylesheets=['https://codepen.io/akshit0699/pen/JjdQQyp.css'])
app.title = "Covid19-India"
server = app.server

# Time updates
dt = datetime.now()
dt1 = dt + timedelta(hours = 5, minutes = 30)
update = dt1.strftime('%B ,%d at %H:%M')
up_time = "Last updated on:  " + update + ", directly from the MoHFW portal"

# Getting the data and cleaning it
scrapedData = pd.read_html("https://www.mohfw.gov.in/")[-1]

scrapedData.columns = ['S. No.','State', 'Confirmed', 'Recovered', 'Deaths']
scrapedData.drop('S. No.', axis = 1, inplace = True)
star = scrapedData.iloc[-1][0][0]
scrapedData = scrapedData.drop(scrapedData.index[-1])
if(star == "*"):
    scrapedData = scrapedData.drop(scrapedData.index[-1])
cols = scrapedData.columns.drop('State')
scrapedData[cols] = scrapedData[cols].apply(pd.to_numeric, errors='coerce')
scrapedData['Active'] = scrapedData['Confirmed'] - scrapedData['Recovered'] - scrapedData['Deaths']

new = scrapedData.copy()
sc = scrapedData.copy()
sc1 = scrapedData.copy()

sc.sort_values(by = "Confirmed", inplace = True)
sc1.sort_values(by = "State", inplace = True)
sc1["Mortality Rate(per 100)"]= np.round(np.nan_to_num(100*sc1["Deaths"]/sc1["Confirmed"]),1)
sc1.columns = [' STATE/UT ', ' CONFIRMED ', ' RECOVERED ', ' DEATHS ', ' ACTIVE CASES ', ' MORTALITY RATE ']
sc1[' STATE/UT '].replace({'Andaman and Nicobar Islands': 'Andaman & Nicobar'}, inplace = True)


prev = pd.read_csv("prev.csv")
prev_count = prev['Confirmed'].sum()
curr = prev.copy()

# picking up the count from the scraped data to show on the tiles
confirmed_count = new['Confirmed'].sum()
Recovered_count = new['Recovered'].sum()
dead_count = new['Deaths'].sum()
active_count = new['Active'].sum()


# A count check so that false updates are prevented
if(confirmed_count != prev_count):
        curr = new.copy()


curr.sort_values(by = 'Confirmed', inplace = True)
# GETTING THE PER DAY CASES
curr['Confirmed'] = curr['Confirmed'].sub(curr['State'].map(prev.set_index('State')['Confirmed']), fill_value = 0)
curr['Recovered'] = curr['Recovered'].sub(curr['State'].map(prev.set_index('State')['Recovered']), fill_value = 0)
curr['Deaths'] = curr['Deaths'].sub(curr['State'].map(prev.set_index('State')['Deaths']), fill_value = 0)
curr['Active'] = curr['Active'].sub(curr['State'].map(prev.set_index('State')['Active']), fill_value = 0)


# Directly scraping timeline data
df = pd.read_html("https://indiacovid19.github.io/")[-1]
df.drop('Doubling Time*', axis=1, inplace=True)

df.columns = ['Date', 'Total Cases', 'New Cases', 'Growth', 'Active Cases',
       'Recovered Cases', 'Death Cases', 'References*']
df = df.drop(df.index[[1,7,38]]) ########## TO UPDATE THIS WHEN NEXT MONTH STARTS######
growth = df.iloc[-1][3]


df1 = df.copy()
cols = ['Active Cases', 'Recovered Cases', 'Death Cases']
df1[cols] = df1[cols].apply(pd.to_numeric, errors='coerce')
active_growth = '+' + str (round (((df1.iloc[-1][4] - df1.iloc[-2][4]) / df1.iloc[-2][4] *100 ) , 0)).split('.')[0] + '%'
Recovered_growth = '+' + str (round (((df1.iloc[-1][5] - df1.iloc[-2][5]) / df1.iloc[-2][5] *100 ) , 0)).split('.')[0] + '%'
death_growth = '+' + str (round (((df1.iloc[-1][6] - df1.iloc[-2][6]) / df1.iloc[-2][6] *100 ) , 0) ).split('.')[0] + '%'

#COLOR SCHEME
colors = {
    'background': '#111111',
    'text': '#BEBEBE',
    'grid': '#333333'
}
#PLOTS DEFINED HERE


# NEW CASES, PLOT 1
fig_newcases = go.Figure()
fig_newcases.add_trace(go.Scatter(
    x= df['Date'],
    y= df['New Cases'],
    line_shape = 'spline',
    text = df['Growth'],
    fill='tozeroy',
    mode='lines+markers',
    marker=dict(size=4, color='#4E62FF',line=dict(width=1, color='#4E62FF')),
    line_color='rgba(55,5,255,0.6)',
    hovertemplate = "New cases as on %{x}<br><b>Growth: %{text}</b><br>Count: %{y}" ,
    showlegend=False,
    name='New Cases')
)
fig_newcases.update_layout(
    xaxis={'title': 'Timeline','fixedrange':True},
    yaxis={'title': 'New Confirmed Cases','fixedrange':True},
    font=dict(color=colors['text']),
    paper_bgcolor=colors['background'],
    plot_bgcolor=colors['background'],
    height = 700,
    hovermode='closest',
    showlegend=True,

)


# NEW STATE CASES, PLOT 2
figstates_new = px.scatter(curr, x="Confirmed", y = "State" , color = "State", size = "Confirmed", hover_name="State", hover_data=["Recovered", "Deaths", "Active"], template="simple_white")
figstates_new.update_layout(
    xaxis={'title': 'The numbers represent increased counts in past 12 hours for each state','fixedrange':True, 'gridcolor': colors['grid']},
    yaxis={'title': 'State/UT','fixedrange':True, 'gridcolor': colors['grid'],
    'autorange' : True, 'showgrid': True, 'showticklabels': False, 'ticks': ''
    },
    hovermode='closest',
    font=dict(color=colors['text']),
    paper_bgcolor=colors['background'],
    plot_bgcolor=colors['background'],
    height = 700,
)


#LAYOUT INFORMATION

app.layout = html.Div(id = 'intro', style= {'backgroundColor': colors['background'] },
children=[

    html.H1(children='COVID-19 IN INDIA',
        style={
            'textAlign': 'center',
            'color': colors['text']
            }
        ),
    html.H4(children=up_time, style={
        'textAlign': 'center',
        'color': colors['text'],
        }),


    html.Div(
    id = "number_plate",

                children =
                [

                html.Div(
                style={'width': '96%', 'height': '100%', 'backgroundColor':colors['background'], 'display': 'inline-block',
                                'marginRight': '1.8%', 'verticalAlign': 'top','marginTop': '1.8%',  'marginLeft': '1.8%',
                                'box-shadow':'0px 0px 10px #ededee', 'border': '1px solid #ededee'},
                        children=[
                            html.H3(style={'textAlign': 'center',
                                                 'fontWeight': 'bold', 'color': '#2674f6'},
                                               children=[
                                                   html.P(style={'color': colors['text'], 'fontSize': 22, 'height': '10px'},
                                                              children='ACTIVE CASES'),
                                                    html.P(style={'color': 'grey',  'fontSize': 20,'height': '5px'},
                                                                          children=active_growth),
                                                   html.P(style={'textAlign': 'center', 'fontSize': 36, 'height': '14px', 'color': '#3705ff'},
                                                                children=active_count)

                                               ]),


                        ]),
                html.Div(
                style={'width': '96%', 'height': '100%', 'backgroundColor':colors['background'], 'display': 'inline-block',
                                'marginRight': '1.8%', 'verticalAlign': 'top','marginTop': '1.8%','marginLeft': '1.8%',
                                'box-shadow':'0px 0px 10px #ededee', 'border': '1px solid #ededee'},
                        children=[
                            html.H3(style={'textAlign': 'center',
                                                 'fontWeight': 'bold', 'color': '#2674f6'},
                                               children=[
                                                   html.P(style={'color': colors['text'], 'fontSize': 22, 'height': '10px'},
                                                              children='CONFIRMED CASES'),
                                                    html.P(style={'color': 'grey',  'fontSize': 20,'height': '5px'},
                                                                          children=growth),
                                                   html.P(style={'textAlign': 'center', 'fontSize': 36, 'height': '14px', 'color': '#8F1F20'},
                                                                children=confirmed_count)

                                               ]),

                        ]),
                html.Div(
                style={'width': '96%', 'height': '100%', 'backgroundColor':colors['background'], 'display': 'inline-block',
                                'marginRight': '1.8%', 'verticalAlign': 'top','marginTop': '1.8%','marginLeft': '1.8%',
                                'box-shadow':'0px 0px 10px #ededee', 'border': '1px solid #ededee'},
                        children=[
                            html.H3(style={'textAlign': 'center',
                                                 'fontWeight': 'bold', 'color': '#2674f6'},
                                               children=[
                                                   html.P(style={'color': colors['text'], 'fontSize': 22, 'height': '10px'},
                                                              children='RECOVERED'),
                                                    html.P(style={'color': 'grey',  'fontSize': 20,'height': '5px'},
                                                                          children=Recovered_growth),
                                                   html.P(style={'textAlign': 'center', 'fontSize': 36, 'height': '14px', 'color': '#2CA02C'},
                                                                children=Recovered_count)

                                               ]),

                        ]),
                html.Div(
                style={'width': '96%', 'height': '100%', 'backgroundColor':colors['background'], 'display': 'inline-block',
                                'marginRight': '1.8%', 'verticalAlign': 'top','marginTop': '1.8%', 'marginLeft': '1.8%',
                                'box-shadow':'0px 0px 10px #ededee', 'border': '1px solid #ededee'},
                        children=[
                            html.H3(style={'textAlign': 'center',
                                                 'fontWeight': 'bold', 'color': '#2674f6'},
                                               children=[
                                                   html.P(style={'color': colors['text'], 'fontSize': 22, 'height': '10px'},
                                                              children='DEATHS'),
                                                    html.P(style={'color': 'grey',  'fontSize': 20,'height': '5px'},
                                                                          children=death_growth),
                                                   html.P(style={'textAlign': 'center', 'fontSize': 36, 'height': '14px', 'color': 'grey'},
                                                                children=dead_count)

                                               ]),

                        ]),

        ]),


        html.Div(
        id = "fresh_pane",
        children =
        [
            html.H2(children='DAY-WISE RISE IN CONFIRMED CASES',
                style={
                    'textAlign': 'center',
                    'color': colors['text'],
                    'marginTop': '7%'
                    }
                ),
            html.P(children='The plot below shows the rise in confirmed cases each day since the first case was identified. Touch the plot (or move your mouse on it) on the plot to see the actual values for that day',
                style={
                    'textAlign': 'center',
                    'color': colors['text'],
                    'fontSize': 18,
                    'marginRight': '2.8%',
                    'marginLeft': '2.8%'
                    }
                ),

            html.Div(
                style = { 'width': '96%', 'height': '200%','backgroundColor':colors['background'],
                                'display': 'inline-block',
                                'marginRight': '1.8%', 'verticalAlign': 'top', 'marginTop': '0%',  'marginLeft': '1.8%','marginBottom': '1.8%'},
                children = [
                    html.Div(
                    dcc.Graph(id = 'new_cases', figure = fig_newcases)
                    )

                ]),

                html.H2(children='STATE-WISE RISE IN CONFIRMED CASES',
                    style={
                        'textAlign': 'center',
                        'color': colors['text'],
                        'marginTop': '7%'
                        }
                    ),
                html.P(children='The plot below shows the increased counts in past 12 hours for each state. Each state is shown as a circle, and the size of the cricle is dependent on the rise in confirmed cases in that state. You can touch or move your mouse on the circles to see values',
                    style={
                        'textAlign': 'center',
                        'color': colors['text'],
                        'fontSize': 18,
                        'marginRight': '2.8%',
                        'marginLeft': '2.8%'
                        }
                    ),
                html.Div(
                    style = {'width': '95%','height': '100%', 'backgroundColor':colors['background'],
                                    'display': 'inline-block',
                                    'marginRight': '1.8%', 'verticalAlign': 'top','marginTop': '1.8%',  'marginLeft': '1.8%','marginBottom': '1.8%'},
                    children = [
                        html.Div(
                        dcc.Graph(id = 'statewise_new', figure = figstates_new)
                        )

                    ]

                )

        ]),


        html.Div(
        id = "drop_downs",
        children =
            [
            html.H2(children='TRENDS IN COVID-19 CASES IN INDIA',
                style={
                    'textAlign': 'center',
                    'color': colors['text'],
                    'marginTop': '7%'
                    }
                ),
            html.P(children='The plot below contains the trend for "Confirmed Cases", "Recovered Cases", "Active Cases", "Deaths". By default, the plot will show all the trends. You can choose the trends you want to see by using the drop-down menu below',
                style={
                    'textAlign': 'center',
                    'color': colors['text'],
                    'fontSize': 18,
                    'marginRight': '2.8%',
                    'marginLeft': '2.8%'
                    }
                ),

                html.Div(
                    style = {'width': '95%','height': '10%', 'backgroundColor':colors['background'],
                                    'display': 'inline-block',
                                    'marginRight': '1.8%', 'verticalAlign': 'top','marginTop': '0%',  'marginLeft': '1.8%','marginBottom': '1.8%'},

                    children = [
                        html.Div(
                            dcc.Dropdown(id='chooser',
                                multi= True,
                                options=[{'label': i, 'value': i} for i in ['Total Cases', 'Active Cases', 'Recovered Cases', 'Death Cases']],
                                value=['Total Cases', 'Recovered Cases','Active Cases','Death Cases' ],
                                style={'color': colors['background'], 'backgroundColor': 'white',
                                }),

                        )]),


                        html.Div(
                            style = {'width': '94%','height': '100%', 'backgroundColor':colors['background'],
                                            'display': 'inline-block',
                                            'marginRight': '1.8%', 'verticalAlign': 'top','marginTop': '0%',  'marginLeft': '1.8%','marginBottom': '1.8%'},
                            children = [
                                html.Div(
                                dcc.Graph(id = 'overall_trend', figure = "overall_trend")
                                )

                            ]),


            ]),

        html.Div(
        id = "overview_pane",
        children =
        [
        html.H2(children='STATEWISE COUNT OF CONFIRMED CASES',
            style={
                'textAlign': 'center',
                'color': colors['text'],
                'marginTop': '7%'
                }
            ),
        html.P(children='The plot below contains the total confirmed cases in each state. Using the buttons, you can choose to see "Deaths", "Recovered Cases" or "Active Cases" as well',
            style={
                'textAlign': 'center',
                'color': colors['text'],
                'fontSize': 18,
                'marginRight': '2.8%',
                'marginLeft': '2.8%'
                }
            ),

                html.Div(
                style = {'width': '95%','height': '10%', 'backgroundColor':colors['background'],'marginBottom': '1.8%',
                                'display': 'inline-block','marginRight': '1.8%', 'verticalAlign': 'top','marginTop': '1.8%',  'marginLeft': '1.8%','marginBottom': '1.8%'},
                children = [
                    dcc.Dropdown(id='scatter_chooser',
                        options=[{'label': i, 'value': i} for i in ['Confirmed', 'Recovered', 'Deaths', 'Active']],
                        value='Confirmed',
                        style={'color': colors['background'] , 'backgroundColor': 'white',
                        }),

                ]),

                html.Div(
                    style = {'width': '94%','height': '100%', 'backgroundColor':colors['background'],
                                    'display': 'inline-block',
                                    'marginRight': '1.8%', 'verticalAlign': 'top','marginTop': '1.8%',  'marginLeft': '1.8%','marginBottom': '1.8%'},
                    children = [
                        html.Div(
                        dcc.Graph(id = 'statewise_trend', figure = 'statewise_trend')
                        )

                    ]

                )

        ]),

        html.Div(
        id = "extra info",
        children=[
            html.Div(
                style = {'width': '65%','height': '100%', 'backgroundColor':colors['background'],
                                'display': 'inline-block',
                                'marginRight': '1.8%', 'verticalAlign': 'top','marginTop': '1.8%',  'marginLeft': '20%','marginBottom': '1.8%'},
                children = [
                    html.H2(children='STATE WISE UPDATES DIRECTLY FROM MoHFW PORTAL',
                        style={
                            'textAlign': 'left',
                            'color': colors['text'],
                            'marginTop' : '1%',

                            }
                        ),

                    html.Div(
                    dash_table.DataTable(
                        id='table',
                        columns=[{"name": i, "id": i} for i in sc1.columns],
                        data=sc1.to_dict('records'),
                        style_header={'backgroundColor': 'rgb(30, 30, 30)'},
                        fixed_rows={ 'headers': True, 'data': 0 },
                        style_table = {
                        'maxHeight': '500px',

                        'overflowY': 'scroll'
                        },
                        style_cell={
                            'backgroundColor': colors['background'],
                            'color': colors['text'],
                            'width': '100px'

                        },
                        )
                    ),
                ]),
        ]
        ),

         html.Div(dcc.Markdown(' '),
        style={
            'textAlign': 'center',
            'color': '#FEFEFE',
            'width': '100%',
            'float': 'center',
            'display': 'inline-block'}),

    html.Div(html.P(children = "© Akshit Arora",
            style={
                'textAlign': 'center',
                'color': '#FEFEFE',
                'width': '100%',
                'float': 'center',
                'display': 'inline-block',
                'fontSize': 19 }
            )),

    html.Div(
    children = dcc.Markdown('''[LinkedIn](https://www.linkedin.com/in/akshit-arora-31aa1911a/)
            '''),
            style={
                'marginTop': '0%',
                'textAlign': 'center',
                'color': '#FEFEFE',
                'width': '100%',
                'float': 'center',
                'display': 'inline-block',
                'fontSize': 18 }
            ),
    html.Div(
    children = dcc.Markdown('''[Provide feedback here](https://docs.google.com/forms/d/1W7zYv-OsxmETAalT5xpF46nBt-2vZJUU-w6GYszKks4/edit)
            '''),
            style={
                'marginTop': '0%',
                'textAlign': 'center',
                'color': '#FEFEFE',
                'width': '100%',
                'float': 'center',
                'display': 'inline-block',
                'fontSize': 18 }
            ),
    html.Div(dcc.Markdown('''
            Source data: [Ministry of Health and Family Welfare, Government of India](https://www.mohfw.gov.in/index.html)
            '''),
            style={
                'textAlign': 'center',
                'color': '#FEFEFE',
                'width': '100%',
                'float': 'center',
                'display': 'inline-block'}
            )




])


#######################FUNCTION CALLS#########################################
# Output of the function is going to a a plot (as figure) called 'overall_trend'
# Input is coming from a radion button (as value) called 'chooser'


@app.callback(
        Output('overall_trend', 'figure'),
        [Input('chooser', 'value')])
def overall_trend(x):
    traces = []
    for view in x:
        if view == 'Total Cases':
            val = 'Total Cases'
        elif view == 'Active Cases':
            val = 'Active Cases'
        elif view == 'Recovered Cases':
            val = 'Recovered Cases'
        elif view == 'Death Cases':
            val = 'Death Cases'
        else:
            val = 'Total Cases'

        if(val == 'Total Cases'):
            x = '#1F77B4'
        elif(val == 'Active Cases'):
            x = '#FF7F0E'
        elif(val == 'Recovered Cases'):
            x = '#2CA02C'
        elif(val == 'Death Cases'):
            x = '#D62728'
        else:
            x = '#1F77B4'
        traces.append(
                    go.Scatter(

                        x = df['Date'],
                        y = df[val],
                        mode = 'lines',
                        line_shape = 'spline',
                        name = '{}'.format(val),
                        line=dict(width=4, color = x),
                        marker=dict(size=4,line=dict(width=1, color = 'white')),
                        hovertemplate = "%{x}<br><b>Count: %{y}</b>" ,


                    )
            )

    return{
            'data': traces,
            'layout': go.Layout(
                xaxis={'title': 'Timeline','fixedrange':True, 'gridcolor': colors['grid']},
                yaxis={'title': 'Cases Count','fixedrange':True, 'gridcolor': colors['grid']},
                hovermode='closest',
                font=dict(color=colors['text']),
                paper_bgcolor=colors['background'],
                plot_bgcolor=colors['background'],
                height = 700,
                # ticks, xaxis, yaxis modifications
            )
        }



@app.callback(
        Output('statewise_trend', 'figure'),
        [Input('scatter_chooser', 'value')])
def statewise_trend(view):
    if view ==  'Confirmed':
        val = 'Confirmed'
    elif view == 'Recovered':
        val = 'Recovered'
    elif view == 'Deaths':
        val = 'Deaths'
    elif view == 'Active':
        val = 'Active'
    else:
        val = 'Confirmed'

    fig1 = px.histogram(sc,x=val, y = "State" , histfunc="sum",color = "State", hover_name = "State", orientation="h", template="seaborn")
    fig1.update_layout(
        xaxis={'title': 'Cases Count','fixedrange':True, 'gridcolor': colors['grid']},
        yaxis={'title': '','fixedrange':True, 'autorange' : True, 'gridcolor': colors['grid'], 'showgrid': True},
        hovermode='closest',
        font=dict(color=colors['text']),
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        showlegend = False,
        height = 700,
        # ticks, xaxis, yaxis modifications
    )
    return fig1;



if __name__ == '__main__':
    app.run_server(debug=False)
