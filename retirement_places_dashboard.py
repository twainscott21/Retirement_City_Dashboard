import numpy as np
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go

df = pd.read_csv("C:/Users/timot/OneDrive/Documents/Personal Projects/Dad Retirement Place/usnews_retirement_places.csv")
df['Ranking'] = df.index.values + 1
df.drop(columns={'Coordinates'}, inplace=True)
df_cols = df[['Population', 'Ranking', 'Average Commute (min)', 'Median Monthly Rent ($)', 'Median Household Income ($)', 'Median Home Value ($)']]

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("Interactive Retirement City Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            html.Label("Select X-Axis Measurement:"),
            dcc.Dropdown(
                id='x-dropdown',
                options=[{'label':col, 'value':col} for col in df_cols],
                value='Ranking',
                clearable=False
            ),
        ], style={'width':'30%', 'display':'inline-block', 'paddingRight':'20px'}),

        html.Div([
            html.Label("Select Y-Axis Measurement:"),
            dcc.Dropdown(
                id='y-dropdown',
                options=[{'label':col, 'value':col} for col in df_cols],
                value='Median Home Value ($)',
                clearable=False
            ),
        ], style={'width':'30%', 'display':'inline-block', 'paddingRight':'20px'}),

        html.Div([
            html.Label("Select Color Measurement:"),
            dcc.Dropdown(
                id='color-dropdown',
                options=[{'label':col, 'value':col} for col in df_cols],
                value='Ranking',
                clearable=False
            ),
        ], style={'width':'30%', 'display':'inline-block', 'paddingRight':'20px'})
    ], style={'textAlign':'center', 'paddingBottom':'20px'}),
    
    html.Div([
        html.Div([
            html.Label("Select Plot Type:"),
            dcc.RadioItems(
                id='plot-type-radio',
                options=[
                    {'label':'Bar Plot', 'value':'bar'},
                    {'label':'Scatter Plot', 'value':'scatter'}
                ],
                value='bar',
                inline=True,
            ),
            ], style={'width':'30%', 'display':'inline-block', 'paddingRight':'20px', 'verticalAlign':'middle'}),

        html.Div([
            html.Label("Select Plot Type:"),
            dcc.RadioItems(
                id='sort-radio',
                options=[
                    {'label':'X Increasing', 'value':'x'},
                    {'label':'Y Increasing', 'value':'y'}
                ],
                value='x',
                inline=True,
            ),
            ], style={'width':'30%', 'display':'inline-block', 'paddingRight':'20px', 'verticalAlign':'middle'}),
    ], style={'textAlign':'center'}), 

    html.Div([
        html.Div([
            dcc.RangeSlider(
                id='y-slider',
                min=df['Median Home Value ($)'].min(),
                max=df['Median Home Value ($)'].max(),
                value=[df['Median Home Value ($)'].min(), df['Median Home Value ($)'].max()],
                step=int((df['Median Home Value ($)'].max() - df['Median Home Value ($)'].min()) / 15),
                tooltip={"placement": "bottom", "always_visible": True},
                vertical=True
            )
        ], style={'width':'5%', 'display':'inline-block', 'verticalAlign':'middle', 'height':'500px'}),

        html.Div([
            dcc.Graph(id='graph', style={'height': '550px'})
        ], style={'width':'80%', 'display':'inline-block'}), 

        html.Div([
            dcc.RangeSlider(
                id='colorbar-slider',
                min=df['Ranking'].min(),
                max=df['Ranking'].max(),
                value=[df['Ranking'].min(), df['Ranking'].max()],
                step=1,
                tooltip={"placement":"bottom", "always_visible": True},
                vertical=True
            )
        ], style={'width':'5%', 'display':'inline-block', 'verticalAlign':'middle', 'height':'500px'})

    ], style={'display':'flex', 'justifyContent':'center'}),

    html.Div([
        html.Div([
            dcc.RangeSlider(
                id='x-slider',
                min=df['Ranking'].min(),
                max=df['Ranking'].max(),
                value=[df['Ranking'].min(), df['Ranking'].max()],
                step=1,
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={'width':'85%', 'display':'inline-block', 'verticalAlign':'middle', 'height':'20px'})
    ], style={'textAlign':'center', 'paddingBottom':'20px'})
])

@app.callback(
    Output('y-slider', 'min'),
    Output('y-slider', 'max'),
    Output('y-slider', 'step'),
    Output('y-slider', 'value'),
    Input('y-dropdown', 'value')
)

def update_y_slider(selected_y):
    y_min = df[selected_y].min()
    y_max = df[selected_y].max()
    step = int((y_max - y_min) / 15)
    return y_min, y_max, step, [y_min, y_max]

@app.callback(
    Output('x-slider', 'min'),
    Output('x-slider', 'max'),
    Output('x-slider', 'step'),
    Output('x-slider', 'value'),
    Input('x-dropdown', 'value')
)
def update_x_slider(selected_x):
    x_min = df[selected_x].min()
    x_max = df[selected_x].max()
    step = int((x_max - x_min) / 15)
    return x_min, x_max, step, [x_min, x_max]

@app.callback(
    Output('colorbar-slider', 'min'),
    Output('colorbar-slider', 'max'),
    Output('colorbar-slider', 'step'),
    Output('colorbar-slider', 'value'),
    Input('color-dropdown', 'value')
)
def update_colorbar_slider(color_col):
    min_val = df[color_col].min()
    max_val = df[color_col].max()
    step = int((max_val - min_val) / 15)
    return min_val, max_val, step, [min_val, max_val]

@app.callback(
    Output('graph', 'figure'),
    Output('graph', 'style'),
    Input('x-dropdown', 'value'),
    Input('y-dropdown', 'value'),
    Input('color-dropdown', 'value'),
    Input('x-slider', 'value'),  
    Input('y-slider', 'value'),  
    Input('colorbar-slider', 'value'),
    Input('plot-type-radio', 'value'),
    Input('sort-radio', 'value')
)

def update_plot(x_col, y_col, color, x_range, y_range, color_range, plot_type, sort_by):
    df_filtered = df[
                    (df[x_col] >= x_range[0]) & (df[x_col] <= x_range[1]) &
                    (df[y_col] >= y_range[0]) & (df[y_col] <= y_range[1])
                    ].copy()

    if sort_by == 'x':
        df_sort = df_filtered.sort_values(by=x_col, ascending=True).reset_index(drop=True)
    else:
        df_sort = df_filtered.sort_values(by=y_col, ascending=True).reset_index(drop=True)

    hover_extra_cols = [
        c for c in ['Ranking', 'Median Home Value ($)', 'Population', 'Average Commute (min)',
                    'Median Monthly Rent ($)', 'Median Household Income ($)'] if c not in [x_col, y_col]
    ]
    customdata = df_sort[hover_extra_cols].values if hover_extra_cols else None

    if customdata is not None:
        if len(customdata.shape) == 1:
            customdata = customdata.reshape(-1,1)
        customdata_hover = np.hstack([df_sort[x_col].values.reshape(-1,1), customdata])
    else:
        customdata_hover = df_sort[x_col].values.reshape(-1,1)

    hover_template = f'<b>%{{text}}</b><br>{y_col}: %{{y:,.0f}}<br>{x_col}: %{{customdata[0]:,}}<br>'
    for i, col in enumerate(hover_extra_cols):
        if pd.api.types.is_numeric_dtype(df_sort[col]):
            hover_template += f'{col}: %{{customdata[{i+1}]:,}}<br>'  
        else:
            hover_template += f'{col}: %{{customdata[{i+1}]}}<br>'
    hover_template += '<extra></extra>'

    if plot_type == 'bar':
        positions = np.arange(len(df_sort))
        fig = go.Figure(
            go.Bar(
                x = positions,
                y = df_sort[y_col].values,
                marker = dict(
                    color = df_sort[color].values,
                    colorscale = 'Viridis_r',
                    cmin = color_range[0],
                    cmax = color_range[1],
                    colorbar = dict(title=color, len=0.8, thickness=20, x=1.05, y=0.5),
                ),
                width = 0.8,
                text = df_sort['Location'],  
                customdata = customdata_hover,
                hovertemplate = hover_template
            )
        )

        step = max(1, len(df_sort) // 10)
        tickvals = positions[::step]
        ticktext = [str(v) for v in df_sort[x_col].values[::step]]
        fig.update_xaxes(tickmode = 'array', tickvals = tickvals, ticktext = ticktext, tickangle = -45, title = x_col)
        fig.update_layout(yaxis = dict(range = [y_range[0], y_range[1]], title = y_col),
                          width = 1200, height = 600, margin = dict(l=60, r=120, t=70, b=120))
        
        style_dict = {'height':'550px'}


    else:
        if sort_by == 'y':
            x_vals = np.arange(len(df_sort))
            ticktext_vals = df_sort[x_col].values
        else:
            x_vals = df_sort[x_col].values
            ticktext_vals = None

        fig = go.Figure(
            go.Scatter(
                x = x_vals,
                y = df_sort[y_col].values,
                mode = 'markers',
                marker = dict(
                    color = df_sort[color].values,
                    colorscale = 'Viridis_r',
                    cmin = color_range[0],
                    cmax = color_range[1],
                    colorbar = dict(title=color)
                ),
                text = df_sort['Location'],
                customdata = customdata_hover,
                hovertemplate = hover_template
            )
        )

        if ticktext_vals is not None:
            step = max(1, len(df_sort) // 10)
            tickvals = x_vals[::step]
            ticktext = ticktext_vals[::step]
            fig.update_xaxes(tickmode = 'array', tickvals = tickvals, ticktext = ticktext, title = x_col)
        else:
            fig.update_xaxes(title = x_col)

        fig.update_layout(title = f"{y_col} vs {x_col}", width = 1200, height = 600,
                          margin = dict(l=60, r=120, t=70, b=60))
        fig.update_yaxes(range = [y_range[0], y_range[1]], title = y_col)

        style_dict = {'height':'600px'}

    return fig, style_dict

if __name__ == "__main__":
    app.run(debug=True)