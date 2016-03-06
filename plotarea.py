import pandas as pd
import seaborn as sns
import numpy as np
from bokeh.charts import Area
from bokeh.plotting import output_file
# sns.set_palette('dark')


def plot(concdf, outputfile):
    Area(concdf, legend='top_left',
         title="Plasma Concentration over Time",
         xlabel="Time", ylabel="Concentration")
    output_file(outputfile, title="Concentraion Plot")
    return
