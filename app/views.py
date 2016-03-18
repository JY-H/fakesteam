import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, flash, request, render_template, g, redirect, Response, url_for, session
from app import app
from server import test_server, fakesteam_server
import gc

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

    user = None
    if session.has_key('name'):
        user = session['name']

    return render_template('index.html', games=games, name=user)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uid = request.form['uid']
        cmd = "select * from users where users.uid =%s"
        cursor = g.conn.execute(cmd, (uid))

        if cursor.rowcount <= 0:
            flash("Invalid ID. Please try again.")
            return render_template('login.html')
        else:
            cmd = "select name from users where users.uid=%s"
            cursor = g.conn.execute(cmd, (uid))
            name = cursor.fetchone()

            session['uid'] = uid
            session['name'] = str(name.name)

            # check if user is developer or gamer
            cmd = "select * from gamers where gamers.uid=%s"
            cursor = g.conn.execute(cmd, (uid))
            if cursor.rowcount > 0:
                session['permissions'] = 'gamer'
            else:
                session['permissions'] = 'dev'
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/register_gamer/', methods=['GET', 'POST'])
def register_gamer():
    # if it's a POST request
    if request.method == 'POST':
        # get the information
        uid = request.form['uid']
        username = request.form['username']
        name = request.form['name']
        cmd = "select * from users where users.uid =%s"
        cursor = g.conn.execute(cmd, (uid))

        # check uid unique
        if cursor.rowcount > 0:
            flash("That ID is already taken! Choose another one.")
            return render_template('register.html')

        # check username unique
        cmd = "select * from gamers where gamers.username=%s"
        cursor = g.conn.execute(cmd, (username))
        if cursor.rowcount > 0:
            flash("That username is already taken! Choose another one.")
            return render_template('register.html')

        cmd = "insert into users values(%s, %s)"
        g.conn.execute(cmd, (uid, name))
        cmd = "insert into gamers values(%s, %s)"
        g.conn.execute(cmd, (uid, username))
        gc.collect()

        session['logged_in'] = True
        session['uid'] = uid
        session['name'] = name
        session['permissions'] = 'gamer'

        return redirect(url_for('index'))

    return render_template('register_gamer.html')


@app.route('/register_dev/', methods=['GET', 'POST'])
def register_dev():
    # if it's a POST request
    if request.method == 'POST':
        # get the information
        uid = request.form['uid']
        name = request.form['name']
        yrs_dev = request.form['exp_dev']
        cmd = "select * from users where users.uid =%s"
        cursor = g.conn.execute(cmd, (uid))

        # check uid unique
        if cursor.rowcount > 0:
            flash("That ID is already taken! Choose another one.")
            return render_template('register.html')
        else:
            cmd = "insert into users values(%s, %s)"
            g.conn.execute(cmd, (uid, name))
            cmd = "insert into developers values(%s, %s)"
            g.conn.execute(cmd, (uid, yrs_dev))
        g.conn.close()
        gc.collect()

        session['logged_in'] = True
        session['uid'] = uid
        session['name'] = name
        session['permissions'] = 'dev'

        return redirect(url_for('index'))

    return render_template('register_dev.html')