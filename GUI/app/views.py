
from app import app
from flask import render_template

@app.route('/')
def index():    
    return render_template('public/index.html')

@app.route('/jinja')
def jinja():
    my_name = "martina"
    age = 54
    langs = ['python','java']
    return render_template('public/jinja.html',my_name= my_name,age = age,langs = langs)

