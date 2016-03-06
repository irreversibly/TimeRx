from flask import Flask
from flask import request, jsonify
from flask import render_template

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


@app.route('/_add_numbers')
def add_numbers():
   """Add two numbers server side, ridiculous but well..."""
   drug = request.args.get('drug', 0, type=int)
   dose = request.args.get('dose', 0, type=int)
   times = request.args.get('times', 0, type=int)
   return jsonify(result=dose * times)


@app.route('/test')
def test():
   return render_template('jquery_test.html')


if __name__ == '__main__':
    app.debug = True
    app.run()
