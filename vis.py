from flask import Flask, render_template
import pandas as pd
from test import generate_plots  # Importing all the plotting functions

app = Flask(__name__)

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

    plots_html = generate_plots(star_data)  #function call from test.py for star system
    return render_template('star_system.html', plots=plots_html, star_system=star_system)

if __name__ == '__main__':
    app.run(debug=True)

