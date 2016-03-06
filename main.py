from flask import Flask
from flask import request
from flask import render_template
from plotarea import plot

app = Flask(__name__)


@app.route('/')
def my_form():
    return render_template("form.html")


@app.route('/', methods=['POST'])
def form():
    drug1 = request.form['drug1']
    dose1 = request.form['dose1']
    processed_text = drug1 + dose1
    return processed_text
    # return render_template('form.html')


if __name__ == '__main__':
    app.debug = True
    app.run()
