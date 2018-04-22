# -*- coding: utf-8 -*-
import pickle
import datetime as dt

import pandas as pd
from flask import Flask
from flask_cors import CORS
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
from data_manager import DataManager
import plotly.graph_objs as go

dm = DataManager('./vgsales.csv')

year_options={}
for year in dm.data['Year'].unique():
	if not np.isnan(year):
		year_options[int(year)]={'label':int(year), 'style':{'font-size':'10px','margin-left':'10'}}

app = dash.Dash(__name__)
app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})  # noqa: E501
server = app.server
CORS(server)
app.layout = html.Div(
    [
        html.Div(
            [
                html.H1(
                    'Video Games Sales Dashboard',
                    className='eight columns',
                ),
                
            ],
            className='row'
        ),
        html.Div(
            [
                html.H5(
                    '',
                    id='well_text',
                    className='two columns'
                ),
                html.H5(
                    '',
                    id='production_text',
                    className='eight columns',
                    style={'text-align': 'center'}
                ),
                html.H5(
                    '',
                    id='year_text',
                    className='two columns',
                    style={'text-align': 'right'}
                ),
            ],
            className='row'
        ),
      	html.Div(
            [
                html.Div(
                    [
                    	html.H5(
		                    'Sales by Region'
		                    
		                ),
		                
					    dcc.Dropdown(
					        id='region-dropdown',
					        value='Global_Sales',
					        options=[{'label':'NA_Sales','value':'NA_Sales'}, 
					        		{'label':'EU_Sales','value':'EU_Sales'}, 
					        		{'label':'JP_Sales','value':'JP_Sales'}, 
					        		{'label':'Other_Sales','value':'Other_Sales'}, 
					        		{'label':'Global_Sales','value':'Global_Sales'}],
					        multi=True,
					        
					    ),
                        dcc.Graph(id='graph-with-slider',
                        	figure=go.Figure(
                        		data= [go.Scatter(
										x=dm.group_sales_by_stateless(dm.data,'Year')['Year'],
										y=dm.group_sales_by_stateless(dm.data,'Year')['Global_Sales'],
										text='Global_Sales',
										name='Global_Sales'
								)],
								layout= go.Layout(
									xaxis={'title': 'Year'},
						 			yaxis={'title': 'Sales'},
									margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
									legend={'x': 0, 'y': 1},
									hovermode='closest'
								)
							)
                        ),
                       
                        dcc.RangeSlider(
                        	id='year-slider',
						    marks=year_options,
						    min=dm.data['Year'].min(),
						    max=dm.data['Year'].max(),
						    value=[dm.data['Year'].min(), dm.data['Year'].max()],
						    allowCross=True,
						)

                    ],
                    className='twelve columns',
                    style={'margin-top': '20'}
                ),
                
            ],
            className='row'
        ),
        html.Div(
            [
                html.Div(
                    [	
                    	
                    	dcc.Dropdown(
					        id='criterion-dropdown',
					        options=[{'label':'Genre','value':'Genre'}, 
					        		{'label':'Publisher','value':'Publisher'},
					        		{'label':'Platform','value':'Platform'},
					        		{'label':'Region','value':'Region'}
					        		],
					        
					        value='Genre'
					    ),
					    html.H5(
		                    '',
		                    id='year-text',
		         
		                ),
                        dcc.Graph(id='pie-graph',
                        	figure=go.Figure(
                        		data= [go.Pie(
										labels = dm.group_sales_by_stateless(dm.data,'Genre')['Genre'],
										values =dm.group_sales_by_stateless(dm.data,'Genre').sum(1),
										name= 'Genre',
										textinfo ='none'
								)]
								
							)
                        )
                    ],
                    className='seven columns',
                    style={'margin-top': '50'}
                ),
                
                html.Div(
                    [
                        dcc.Dropdown(
					        id='most-popular-dropdown',
					        options=[{'label':'Genre','value':'Genre'}, 
					        		{'label':'Publisher','value':'Publisher'},
					        		{'label':'Platform','value':'Platform'},
					        		
					        		],
					        
					        value='Genre'
					    ),
					    html.H5(
		                    '',
		                    id='criterion-text',
		                    style={'margin-bottom:': '10'}
		                ),
					    dcc.Graph(id='graph-with-popularity'
                        ),
                    ],
                    className='five columns',
                    style={'margin-top': '50', 'margin-left':'30'}
                ),
            ],
            className='row'
        ),
    ],
    className='ten columns offset-by-one'
)

@app.callback(
    dash.dependencies.Output('graph-with-slider', 'figure'),
    [dash.dependencies.Input('year-slider', 'value'),dash.dependencies.Input('region-dropdown', 'value')])
def update_figure(selected_year,selected_region):
	if type(selected_region) is not list:
		
		selected_region=[selected_region]
	dm.filter_by_range(column_name='Year', min_val=selected_year[0], max_val=selected_year[1], include_max=True)

	dm.group_sales_by(column_name='Year')
	traces = []
	
	for i in selected_region:
		
		traces.append(go.Scatter(
			x=dm.data['Year'],
			y=dm.data[i],
			text=i,
			name=i
		))
	dm.reset_data()
	return {
		'data': traces,
		'layout': go.Layout(
			xaxis={'title': 'Year'},
 			yaxis={'title': 'Sales'},
			margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
			legend={'x': 0, 'y': 1},
			hovermode='closest'
		)
	}


@app.callback(
    dash.dependencies.Output('graph-with-popularity', 'figure'),
    [dash.dependencies.Input('most-popular-dropdown', 'value')])
def update_popular(criterion):
	data=get_popularity_data(criterion)
	
		
	
	return {
		'data': [go.Scatter(
						x=data['Year'],
						y=data[criterion],
						text=[str(x) for x in data["Agg_Sales"]],
						name=criterion,
						mode='markers',
						
					    marker=dict(
					        size=[(int(x)/10)+2 for x in data['Agg_Sales']],
					     	
					    )
					)
		],
		'layout': go.Layout(
			xaxis={'title': 'Year',
					'showticklabels':True,
			        'tickangle':45,
			        'tickfont':{
			            
			            'size':10
			            
        			},
			},
			yaxis={
					'showticklabels':True,
			        'tickangle':-50,
			        'tickfont':{
			            
			            'size':10
			            
        			},
			},
 			
			margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
			legend={'x': 0, 'y': 1},
			hovermode='closest'
		)
	}

@app.callback(
    dash.dependencies.Output('pie-graph', 'figure'),
    [dash.dependencies.Input('year-slider', 'value'),dash.dependencies.Input('criterion-dropdown', 'value')])
def update_pie(selected_year,selected_criterion):
	dm.filter_by_range(column_name='Year', min_val=selected_year[0], max_val=selected_year[1], include_max=True)

	
	traces = []
	if selected_criterion=='Region':
		labels=['NA_Sales','EU_Sales','JP_Sales','Other_Sales']
		values=[dm.data.sum()[x] for x in labels]
		dm.reset_data()
		return {
			'data':[go.Pie(
				labels = labels,
				values = values,
				name= 'Region',
				textinfo ='none'
			)],
			'layout': go.Layout(
				
				

			)
		}
	else:
		dm.group_sales_by(column_name=selected_criterion)
		labels=dm.data[selected_criterion]
		values=dm.data.sum(1)
		dm.reset_data()
		return {
			'data':[go.Pie(
				labels = labels,
				values = values,
				name= selected_criterion,
				textinfo ='none'
			)],
			'layout': go.Layout(
				
				legend=dict(x=1, y=1.2, font=dict(
			            family='sans-serif',
			            size=8,
			            color='#000'
			        	),
				),
				height=400,
				width=600,
				margin={'l': 50, 'b': 50, 't': 50, 'r': 50},
				
			)
		}

@app.callback(Output('criterion-text', 'children'),
              [Input('most-popular-dropdown', 'value')])
def update_year_text(criterion):
    return "Most Popular {} by Year by Sales".format(criterion)

	
@app.callback(Output('year-text', 'children'),
              [Input('year-slider', 'value')])
def update_year_text(selected_year):
    return "Displaying data from {} to {}".format(selected_year[0], selected_year[1])

def get_popularity_data(criterion):
	df=dm.data[['EU_Sales','JP_Sales','NA_Sales','Other_Sales','Global_Sales']]
	dm.data['Agg_Sales']=df.sum(1)
	
	df=dm.data[['Year',criterion,'Agg_Sales']]
	
	dm.reset_data()
	df_agg = df.groupby(['Year',criterion]).agg({'Agg_Sales':sum})
	g = df_agg['Agg_Sales'].groupby(level=0, group_keys=False).nlargest(1).to_frame()
	
	g.reset_index(level=g.index.names, inplace=True)
	return g

if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
