from flask import Flask
from flask import request
from flask import render_template
import pandas as pd

import sys
sys.path.insert(0, './kinetizer')
sys.path.insert(0, './plotter')
from plotarea import plot
# from kinetizer import *

app = Flask(__name__)

# placeholders for functions to be imported
def rafalsfunction(list):
    return None, None
def druvasfunction():
    pass


@app.route('/')
def my_form():
    return render_template("form.html")


@app.route('/', methods=['POST'])
def form():
    name = request.form['name']
    drug1 = request.form['drug1']
    dose1 = request.form['dose1']
    drug2 = request.form['drug2']
    dose2 = request.form['dose2']
    drug3 = request.form['drug3']
    dose3 = request.form['dose3']
    drug4 = request.form['drug4']
    dose4 = request.form['dose4']

    # check if drugs are specified
    drugsinput = []
    for drug in [drug1, drug2, drug3, drug4]:
        if len(drug) > 0:
            drugsinput.append(drug)

    concdict, scheddict = rafalsfunction(drugsinput)
    concdf = pd.DataFrame.from_dict(concdict)
    plot(concdf, "areaplot.html")
    druvasfunction(scheddict, "areaplot.html", "report.html")
    # processed_text = drug1 + dose1
    # return processed_text
    return render_template('report.html')


if __name__ == '__main__':
    app.debug = True
    app.run()
