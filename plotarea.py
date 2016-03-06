# import pandas as pd
# import seaborn as sns
# import numpy as np
from bokeh.charts import Area
from bokeh.plotting import output_file, show
# sns.set_palette('dark')


def plot(concdf, outputfile):
    area = Area(concdf, legend='top_left',
                title="Plasma Concentration over Time",
                xlabel="Time", ylabel="Concentration")
    output_file(outputfile, title="Concentraion Plot")
    show(area)
    return
