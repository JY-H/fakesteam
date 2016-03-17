from flask import render_template
from app import app

@app.route('/')
def index():
    games = [
        {'name': 'Dota 2',
         'url': 'http://cdn.akamai.steamstatic.com/steam/apps/570/header.jpg?t=1457137796'
        },
        {'name': 'Tom Clancy: The Division',
         'url': 'http://cdn.akamai.steamstatic.com/steam/apps/365590/header.jpg?t=1457537972'}
    ]
    return render_template('index.html', title='Home', games=games)
