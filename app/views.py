import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
from app import app
from server import test_server, fakesteam_server

server = fakesteam_server()

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = server.engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


@app.route('/')
def index():
    cursor = g.conn.execute("SELECT title, url FROM games")
    games = []
    for result in cursor:
        game = {}
        game['title'] = result['title']
        game['url'] = result['url']
        games.append(game)
    cursor.close()

    print games
    return render_template('index.html', games=games)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/register/', methods=['GET', 'POST'])
def register():
    return render_template('register.html')