from flask import Flask, render_template
from pandas import read_csv
import sys
app = Flask(__name__)


@app.route("/")
def template_test(  ):
    #return render_template('img_template.html', my_string="Dieee!", my_list=[0,1,2,3,4,5])


    plot_file='static/plot4.html'
    schedule_file='static/example_table.txt'


    if len(sys.argv)==3:
        plot_file=sys.argv[2]
        schedule_file=sys.argv[1]
    elif len(sys.argv)==2:
        schedule_file=sys.argv[1]

    schedule=read_csv( schedule_file, delimiter="\t")
    return render_template('Example_Report.html', schedule_table=schedule, plot=plot_file)
    #return render_template('Example_Report.html', schedule_table=schedule, plot=plot_file)
    #return render_template('img_template.html')

if __name__ == '__main__':
    #args=sys.argv[1:]
    #plot_file=args[0]
    #schedule_file=args[1]
    #effects_file=args[3]

    #app.run(plot_file, schedule_file, debug=True)
    app.run( debug=True)