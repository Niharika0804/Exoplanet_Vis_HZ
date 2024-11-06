import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go  # Import for advanced trace additions
import pandas as pd

# Load the dataset
df = pd.read_csv("hwc_3d_data.csv")


# Initialize the Dash app
def create_dash_app(flask_app):
    dash_app = dash.Dash(__name__, server=flask_app, url_base_pathname='/dashboard/')

    #px.defaults.layout.template = "plotly_dark"
    # Define the layout of the Dash app
    dash_app.layout = html.Div([
        html.H1("Exoplanet Habitability Dashboard"),

            html.H3("How to Interpret the Charts"),
            html.P(["Here’s how to interpret the different visualizations in the dashboard:",
                   html.Br(),
                   "Nothing much! Just read what the chart says about and dive into exploring the charts",
                   html.Br(),
                   "Use the cool plotly funtions to interact with the graphs.",
                   html.Br(),
                   "Happy Learning!"]),

        # Dropdown to select a factor to compare with Habitability Index
            html.H4("1. Habitability Index Bar Chart"),
            html.P("This chart shows the habitability index of different exoplanets. "
                   "The habitability index (0 for non-habitable and 1 for habitable) is shown for each planet. "
                   "If most bars are orange, it suggests that most of the exoplanets are considered habitable. "
                   "If most bars are skyblue, it indicates that a majority of the planets are non-habitable."),
        html.Label("Select a factor to compare with Habitability Index:"),
        dcc.Dropdown(
            id='factor-dropdown',
            options=[
                {'label': 'Distance from Star', 'value': 'S_DISTANCE'},
                {'label': 'Planet Radius', 'value': 'P_RADIUS'},
                {'label': 'Planet Mass', 'value': 'P_MASS'},
            ],
            value='S_DISTANCE'
        ),

        # Habitability Index Bar Chart
        dcc.Graph(id='habitability-bar-chart'),

        # Scatter plot for selected factor vs. Habitability Index
            html.H4("2. Scatter Plot (Factor vs Habitability Index)"),
            html.P("This scatter plot shows the relationship between a selected factor (such as distance from star, "
                   "planet radius, or mass) and the habitability index. "
                   "Look for patterns: Does a particular factor seem to correlate with habitability? "
                   "For example, if most planets that are far from the star are non-habitable, this suggests distance may be important."),

        dcc.Graph(id='habitability-scatter-plot'),

        # Dropdown for additional scatter plots
            html.H4("3. Additional Scatter Plot (Different Factors)"),
            html.P(
                "This plot allows you to compare additional factors like Mass vs. Radius or Equilibrium Temperature vs. Semi-Major Axis. "
                "You can explore how these characteristics correlate with habitability and check if certain combinations of mass, radius, or temperature seem to be linked to habitability."),

        html.Label("Select Additional Scatter Plot:"),
        dcc.Dropdown(
            id='scatter-dropdown',
            options=[
                {'label': 'Mass vs Radius', 'value': 'mass_radius'},
                {'label': 'Equilibrium Temperature vs Semi-Major Axis', 'value': 'temp_semi_major'},
                {'label': 'Earth Similarity Index vs Habitability', 'value': 'esi_habitability'}
            ],
            value='mass_radius'
        ),
        dcc.Graph(id='additional-scatter-plot'),

        # Dropdown for histogram selection
            html.H4("4. Histogram (Orbital Period or Planetary Types)"),
            html.P("This histogram shows the distribution of a specific variable (orbital period or planetary type). "
                   "For example, if the histogram of orbital periods shows a peak at shorter periods, it suggests that planets with shorter orbits are more common."),

        html.Label("Select Histogram:"),
        dcc.Dropdown(
            id='histogram-dropdown',
            options=[
                {'label': 'Distribution of Orbital Periods', 'value': 'P_PERIOD'},
                {'label': 'Distribution of Planetary Types', 'value': 'P_TYPE_TEMP'}
            ],
            value='P_PERIOD'
        ),
        dcc.Graph(id='histogram'),

        # Box Plot Dropdown
            html.H4("5. Box Plot (Mass and Radius by Planet Type or Temperature by Habitability)"),
            html.P("Box plots show the distribution of a variable across different categories. "
                   "You can compare the mass and radius of planets across different types, or look at the temperature distribution by habitability. "
                   "Outliers may be interesting for further analysis."),

        html.Label("Select Box Plot:"),
        dcc.Dropdown(
            id='boxplot-dropdown',
            options=[
                {'label': 'Mass and Radius by Planet Type', 'value': 'mass_radius_type'},
                {'label': 'Equilibrium Temperature by Habitability', 'value': 'temp_habitability'}
            ],
            value='mass_radius_type'
        ),
        dcc.Graph(id='boxplot'),

        # Bar Chart Dropdown
            html.H4("6. Bar Chart (Number of Exoplanets per Stellar Type or Habitability Count)"),
            html.P(
                "This chart shows the number of exoplanets per stellar type or the count of habitable vs. non-habitable planets. "
                "Are certain stellar types more likely to host habitable planets? A larger bar for one stellar type suggests this star type may be more conducive to habitability."),

        html.Label("Select Bar Chart:"),
        dcc.Dropdown(
            id='barchart-dropdown',
            options=[
                {'label': 'Number of Exoplanets per Stellar Type', 'value': 'stellar_type'},
                {'label': 'Count of Habitable vs Non-Habitable Planets', 'value': 'habitability_count'}
            ],
            value='stellar_type'
        ),
        dcc.Graph(id='barchart'),

        # Correlation Heatmap
            html.H4("7. Correlation Heatmap"),
            html.P(
                "The correlation heatmap shows how different factors correlate with each other and with habitability. "
                "Look for high correlations between variables and habitability. For example, if mass and radius are highly correlated, it means these two variables tend to increase together. "
                "You can also see if habitability is strongly correlated with specific factors, which might indicate that these factors are important for determining habitability."),

        html.Label("Correlation Heatmap:"),
        dcc.Graph(id='heatmap')
    ])

    # Dash callbacks for charts
    @dash_app.callback(
        [Output('habitability-bar-chart', 'figure'),
         Output('habitability-scatter-plot', 'figure')],
        [Input('factor-dropdown', 'value')]
    )
    def update_habitability_charts(selected_factor):
        df['P_HABITABLE'] = df['P_HABITABLE'].astype('category')

        # Bar chart for habitability index
        bar_chart = px.bar(
            df,
            x='P_NAME',
            y='P_HABITABLE',
            title="Habitability Index of Exoplanets",
            color='P_HABITABLE',
            color_discrete_sequence=['orange', 'skyblue'],  # Blue and red palette
            labels={'P_NAME': 'Planet Name', 'P_HABITABLE': 'Habitability Index'},
            category_orders={"P_HABITABLE": [0, 1]}
        )
        bar_chart.update_yaxes(tickvals=[0, 1])
        bar_chart.update_traces(marker=dict(line=dict(width=2, color='black')))

        # Scatter plot of selected factor vs. habitability index
        scatter_plot = px.scatter(
            df,
            x=selected_factor,
            y='P_HABITABLE',
            hover_name='P_NAME',
            title=f"{selected_factor.replace('_', ' ')} vs. Habitability Index",
            color='P_HABITABLE',  # Color by habitability
            color_continuous_scale='Viridis',  # Color scale
            labels={selected_factor: selected_factor.replace('_', ' '), 'P_HABITABLE': 'Habitability Index'},
            category_orders={"P_HABITABLE": [0, 1]}
        )
        scatter_plot.update_yaxes(tickvals=[0, 1])
        return bar_chart, scatter_plot

    @dash_app.callback(
        Output('additional-scatter-plot', 'figure'),
        [Input('scatter-dropdown', 'value')]
    )
    def update_additional_scatter(selected_scatter):
        df['P_HABITABLE'] = df['P_HABITABLE'].astype('category')

        if selected_scatter == 'mass_radius':
            fig = px.scatter(df, x="P_MASS", y="P_RADIUS", hover_name='P_NAME', title="Mass vs Radius", color='P_HABITABLE', color_continuous_scale='Viridis')
        elif selected_scatter == 'temp_semi_major':
            fig = px.scatter(df, x="P_SEMI_MAJOR_AXIS", y="P_TEMP_EQUIL", hover_name='P_NAME', title="Equilibrium Temperature vs Semi-Major Axis", color='P_HABITABLE', color_continuous_scale='Viridis')
        elif selected_scatter == 'esi_habitability':
            fig = px.scatter(df, x="P_ESI", y="P_HABITABLE", hover_name='P_NAME', title="Earth Similarity Index vs Habitability", color='P_HABITABLE', color_continuous_scale='Viridis')
        return fig

    @dash_app.callback(
        Output('histogram', 'figure'),
        [Input('histogram-dropdown', 'value')]
    )
    def update_histogram(selected_histogram):
        df['P_HABITABLE'] = df['P_HABITABLE'].astype('category')

        if selected_histogram == 'P_PERIOD':
            fig = px.histogram(df, x="P_PERIOD", hover_name='P_NAME', title="Distribution of Orbital Periods", color='P_HABITABLE', color_discrete_sequence=['orange', 'skyblue'])
        elif selected_histogram == 'P_TYPE_TEMP':
            fig = px.histogram(df, x="P_TYPE_TEMP", hover_name='P_NAME', title="Distribution of Planetary Types", color='P_TYPE_TEMP', color_discrete_sequence=['red', 'skyblue', 'orange'])
        return fig

    @dash_app.callback(
        Output('boxplot', 'figure'),
        [Input('boxplot-dropdown', 'value')]
    )
    def update_boxplot(selected_boxplot):
        df['P_HABITABLE'] = df['P_HABITABLE'].astype('category')

        if selected_boxplot == 'mass_radius_type':
            fig = px.box(df, x="P_TYPE_TEMP", y="P_MASS", hover_name='P_NAME', title="Mass by Planet Type", color='P_HABITABLE', color_discrete_sequence=['orange', 'skyblue'])
            fig.add_trace(go.Box(x=df["P_TYPE_TEMP"], y=df["P_RADIUS"], name="Radius", marker=dict(color='lightgreen')))
        elif selected_boxplot == 'temp_habitability':
            fig = px.box(df, x="P_HABITABLE", y="P_TEMP_EQUIL", hover_name='P_NAME', title="Equilibrium Temperature by Habitability", color='P_HABITABLE', color_discrete_sequence=['orange', 'skyblue'])
        return fig

    @dash_app.callback(
        Output('barchart', 'figure'),
        [Input('barchart-dropdown', 'value')]
    )
    def update_barchart(selected_barchart):
        df['P_HABITABLE'] = df['P_HABITABLE'].astype('category')

        if selected_barchart == 'stellar_type':
            fig = px.bar(df, x="S_TYPE", hover_name='P_NAME', title="Number of Exoplanets per Stellar Type", color='P_HABITABLE', color_discrete_sequence=['orange', 'skyblue'])
        elif selected_barchart == 'habitability_count':
            habitability_counts = df['P_HABITABLE'].value_counts().reset_index()
            fig = px.bar(habitability_counts, x='index', y='P_HABITABLE', title="Count of Habitable vs Non-Habitable Planets", color='index', color_discrete_map={0: '#FF5733', 1: '#28A745'})
        return fig

    @dash_app.callback(
        Output('heatmap', 'figure'),
        [Input('factor-dropdown', 'value')]
    )
    def update_heatmap(_):
        df['P_HABITABLE'] = df['P_HABITABLE'].astype('category')

        # Correlation heatmap
        correlation_columns = ["P_MASS", "P_RADIUS", "P_TEMP_EQUIL", "P_ESI", "P_HABITABLE"]
        correlation_df = df[correlation_columns].corr()
        fig = px.imshow(correlation_df, text_auto=True, title="Correlation Heatmap", color_continuous_scale='Viridis')
        return fig

    return dash_app
