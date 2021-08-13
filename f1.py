import flask
from flask import Flask,render_template
app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index_1.html')

@app.route('/se')
def hello_world_1():
    name="Amrit Parijat"
    return render_template('about_1.html',name2=name)

@app.route('/sej')
def hi():
    return 'Heya'
app.run(debug=True)

