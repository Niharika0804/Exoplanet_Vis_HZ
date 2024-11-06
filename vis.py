from flask import Flask, render_template
import pandas as pd
from test8 import generate_plots  # Importing all the plotting functions
from dash_app import create_dash_app #importing the dash_app.py file

app = Flask(__name__)

dash_app = create_dash_app(app)

df = pd.read_csv("hwc_3d_data.csv")

@app.route('/')
def index():
    plots_html = generate_plots(df)
    return render_template('index.html', plots=plots_html)


@app.route('/<star_system>')
def show_star_system(star_system):
    star_data = df[df['S_NAME'] == star_system]

    if star_data.empty:
        return f"No data available for {star_system}", 404
    star_info = star_data.iloc[0]

    return render_template('star_systems.html', star_system=star_system, star_info=star_info)

@app.route('/<star_system>_vis')
def show_star_system_vis(star_system):
    star_data = df[df['S_NAME'] == star_system]

    if star_data.empty:
        return f"No data available for {star_system}", 404

    plots_html = generate_plots(star_data)  # Call the function from plotting.py for this star system
    return render_template('star_system_vis.html', plots=plots_html, star_system=star_system)

if __name__ == '__main__':
    app.run(debug=True)
