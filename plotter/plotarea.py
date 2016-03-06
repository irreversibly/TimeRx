# from __future__ import division
import pandas as pd
# import seaborn as sns
# import numpy as np
from bokeh.charts import Area
from bokeh.plotting import output_file, save
import os
# sns.set_palette('dark')

# orange, green, blue, yellow
# colors = ["#F38C17", "#67BA67", "#92B1CA", "#F5E254"]


def plot(concdf, outputfile="test.html"):
    newtime = concdf
    newtime["Times"] = map(lambda x: (float(x)/60)-8, concdf["Times"])

    data = pd.melt(newtime, id_vars="Times")
    # oldtimes = data["Times"]
    # resettimes = []
    # for time in oldtimes:
    #     if time >= 24:
    #         resettimes.append(time-24)
    #     else:
    #         resettimes.append(time)
    # data["Times"] = resettimes
    area = Area(data, x="Times", y="value", legend='top_right',
                title="T-Rx Optimized Treatment Schedule",
                xlabel="Hours (post 8am)", ylabel="% Remaining in Patient", color="variable")
    output_file(outputfile, title="T-RxPlot")
    save(area)
    print os.getcwd()
    # show(area)
    return


def plot_stacked(concdf, outputfile="test.html"):
    # divide by 60 for time
    # get x val to be time
    data = concdf.set_index(['Times'])
    area = Area(data, legend='top_right', stack=True,
                title="Plasma Concentration over Time",
                xlabel="Time", ylabel="Concentration")
    output_file(outputfile, title="Concentraion Plot")
    # show(area)
    return
