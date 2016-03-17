from flask import render_template
from app import app
@app.route('/')
@app.route('/index')

def index():
    user = {'nickname': 'JY'}
    posts = [
            {
                'author': {'nickname': 'JY'},
                'body': 'I do hate web apps...'
            },
            {
                'author': {'nickname': 'Kylie'},
                'body': 'Me too..'
            }
            ]
    return render_template('index.html', title='Home', user=user, posts=posts)
