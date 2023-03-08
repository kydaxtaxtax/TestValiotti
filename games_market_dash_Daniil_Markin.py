from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

data = pd.read_csv('games.csv')
data['User_Score'] = pd.to_numeric(data['User_Score'], errors='coerce')
data = data.dropna()

#Фильтрыция даты
data['Year_of_Release'] = pd.to_datetime(data['Year_of_Release'], format='%Y')
data = data[(data['Year_of_Release'] > '2000-01-01')]
#Переводим дату в год
data.loc[:, 'Year_of_Release'] = data.loc[:, 'Year_of_Release'].dt.year

# переменные с жанрами и рейтингами для фильтрации
available_genre = sorted(data['Genre'].unique())
available_rating = sorted(data['Rating'].unique())

app = Dash(__name__)
app.layout = html.Div([
    html.Div([
        html.H1("Состояние игровой индустрии"),

        html.P(
            "Анализ игровой индустрии с 2000 года."
            " Используйте фильтры, чтобы увидеть результат."
        )
    ], style={
        'backgroundColor': 'rgb(230, 230, 250)',
        'padding': '10px 5px'
    }),

    html.Div([
        html.Div([
            html.Label('Жанры игр'),
            dcc.Dropdown(
                id='crossfilter-genre',
                options=[{'label': i, 'value': i} for i in available_genre],
                value=['Sports', 'Strategy'],
                multi=True
            )
        ],
            style={'width': '49%', 'display': 'inline-block'}),

        html.Div([
            html.Label('Рейтинги игр'),
            dcc.Dropdown(
                id='crossfilter-rating',
                options=[{'label': i, 'value': i} for i in available_rating],
                value=['T', 'E'],
                multi=True
            )
        ],
            style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    }),

    html.Div(
        id='textarea-output',
        style={'width': '100%', 'float': 'right', 'display': 'inline-block'}
    ),

    html.Div(
        dcc.Graph(id='histogram'),
        style={'width': '49%', 'display': 'inline-block'}
    ),

    html.Div(
        dcc.Graph(id='scatter-plot'),
        style={'width': '49%', 'float': 'right', 'display': 'inline-block'}
    ),

    html.Div(
        dcc.RangeSlider(
            id='crossfilter-year',
            min=data['Year_of_Release'].min(),
            max=data['Year_of_Release'].max(),
            value=[2004, 2014],
            step=None,
            marks={str(year):
                       str(year) for year in data['Year_of_Release'].unique()}
        ),
        style={'width': '49%', 'padding': '0px 20px 20px 20px'}
    )
])

@app.callback(
    Output('textarea-output', 'children'),
    [Input('crossfilter-genre', 'value'),
     Input('crossfilter-rating', 'value'),
     Input('crossfilter-year', 'value')])
def update_textarea(genre, rating, year):
    filtered_data = data[(data['Year_of_Release'] >= year[0]) &
                         (data['Year_of_Release'] <= year[1]) &
                         (data['Genre'].isin(genre)) &
                         (data['Rating'].isin(rating))]
    games_count = len(filtered_data.index)
    return 'Результат фильтрации: {}'.format(games_count)

@app.callback(
    Output('histogram', 'figure'),
    [Input('crossfilter-genre', 'value'),
     Input('crossfilter-rating', 'value'),
     Input('crossfilter-year', 'value')])
def update_stacked_area(genre, rating, year):
    filtered_data = data[(data['Year_of_Release'] >= year[0]) &
                         (data['Year_of_Release'] <= year[1]) &
                         (data['Genre'].isin(genre)) &
                         (data['Rating'].isin(rating))]
    filtered_data = filtered_data.groupby(['Year_of_Release', 'Platform']).agg('count').reset_index()
    figure = px.area(
        filtered_data,
        x=filtered_data['Year_of_Release'],
        y="Name",
        color=filtered_data['Platform'],
        labels={
           "Platform": "Платформа"
        },
        title="Выпуск игр по годам и платформам."
    )
    figure.update_layout(xaxis_title="Года", yaxis_title="Кол-во")
    return figure

@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('crossfilter-genre', 'value'),
     Input('crossfilter-rating', 'value'),
     Input('crossfilter-year', 'value')])
def update_scatter(genre, rating, year):
    filtered_data = data[(data['Year_of_Release'] >= year[0]) &
                         (data['Year_of_Release'] <= year[1]) &
                         (data['Genre'].isin(genre)) &
                         (data['Rating'].isin(rating))]
    figure = px.scatter(
        filtered_data,
        x=sorted(filtered_data["User_Score"]),
        y="Critic_Score",
        color="Genre",
        labels={
            "Genre": "Жанр"
        },
        title="Зависимость оценок от жанров"
    )
    figure.update_layout(xaxis_title="Оценка пользователей", yaxis_title="Оценка критиков"),
    return figure

if __name__ == '__main__':
    app.run_server()