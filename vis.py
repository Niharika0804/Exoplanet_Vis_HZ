from flask import Flask, render_template
import pandas as pd
from test import generate_plots  # Importing all the plotting functions

app = Flask(__name__)

df = pd.read_csv("hwc_3d_data.csv")

@app.route('/')
def index():
    plots_html = generate_plots(df)
    return render_template('index.html', plots=plots_html)

if __name__ == '__main__':
    app.run(debug=True)
