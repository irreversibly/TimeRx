from flask import Flask
from flask import request
from flask import render_template
import pandas as pd
import os
import sys
sys.path.insert(0, './kinetizer')
sys.path.insert(0, './plotter')
from plotarea import plot
from kinetizer import Kinetizer

app = Flask(__name__)


def getdata(druglist):
    os.chdir("kinetizer")
    if len(druglist) == 3:
        drugs = ["nadolol", "simvastin", "atazanavir"]
        kin = Kinetizer(drugs)
        kin.load_demo()
        schedlist = kin.get_schedule()
    elif len(druglist) == 4:
        drugs = ["nadolol", "simvastin", "atazanavir", "vicodin"]
        kin = Kinetizer(drugs)
        kin.load_demo()
        schedlist = kin.get_schedule()
    else:
        drugs = druglist
        kin = Kinetizer(drugs)
        for i in range(len(drugs)):
            kin.drugs[drugs[i]] = {"start_time": 0}
    concdata = kin.return_dataframe()
    # schedule = kin.get_schedule()
    # schedule.to_csv("templates/schedule.csv")
    os.chdir("../")
    # return concdata, schedule
    return concdata, None
# # # placeholders for functions to be imported
# def druvasfunction():
#     pass


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

    concdict, scheddict = getdata(drugsinput)
    plot(concdict, "areaplot.html")
    # druvasfunction("templates/schedule.csv", "templates/areaplot.html", "report.html")
    # processed_text = drug1 + dose1
    # return processed_text
    # return render_template("areaplot.html")
    return render_template("Demo_Report.html")
    # return app.send_static_file('Demo_Report.html')

if __name__ == '__main__':
    app.debug = True
    app.run()
