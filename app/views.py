from flask import Flask, flash, request, render_template, g, redirect, Response, url_for, session
from app import app
from server import test_server, fakesteam_server
import gc
import sys


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
    cursor = g.conn.execute("SELECT gameid, title, url FROM games")
    games = []
    for result in cursor:
        game = {}
        game['gameid'] = result['gameid']
        game['title'] = result['title']
        game['url'] = result['url']
        games.append(game)
    cursor.close()

    filtered_games = []
    # apply filter
    filtered_os = list(request.args.getlist('filtered_os'))
    filtered_gameplay = list(request.args.getlist('filtered_gameplay'))
    filtered_genre = list(request.args.getlist('filtered_genre'))
    excluded = filtered_os + filtered_gameplay + filtered_genre

    print excluded
    for i in range(len(games)):
        gameid = games[i].get('gameid')
        if unicode(gameid) not in excluded:
            filtered_games.append(games[i])

    user = None
    if session.has_key('name'):
        user = session['name']

    permissions = None
    if session.has_key('permissions'):
        permissions = session['permissions']

    return render_template('index.html', games=filtered_games, name=user, permissions=permissions)

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

            # check if user is developer, gamer, or admin
            cmd = "select * from gamers where gamers.uid=%s"
            cursor = g.conn.execute(cmd, (uid))
            # gamer
            if cursor.rowcount > 0:
                session['permissions'] = 'gamer'
            else:
                # developer
                cmd = "select * from developers where developers.uid=%s"
                cursor = g.conn.execute(cmd, (uid))
                if cursor.rowcount > 0:
                    session['permissions'] = 'dev'
                # admin
                else:
                    session['permissions'] = 'admin'

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

        # check uid valid
        if int(uid) <= 0 or int(uid) >= sys.maxint / 100:
            flash("Invalid ID! The value you entered is either too large or negative.")
            return render_template('register_gamer.html')

        # check uid unique
        cmd = "select * from users where users.uid =%s"
        cursor = g.conn.execute(cmd, (uid))
        if cursor.rowcount > 0:
            flash("That ID is already taken! Choose another one.")
            return render_template('register_gamer.html')

        # check username unique
        cmd = "select * from gamers where gamers.username=%s"
        cursor = g.conn.execute(cmd, (username))
        if cursor.rowcount > 0:
            flash("That username is already taken! Choose another one.")
            return render_template('register_gamer.html')

        cmd = "insert into users values(%s, %s)"
        g.conn.execute(cmd, (uid, name))
        cmd = "insert into gamers values(%s, %s)"
        g.conn.execute(cmd, (uid, username))


        # generate empty library
        cmd = "insert into library_owned values(%s)"
        g.conn.execute(cmd, (uid))
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

        # check uid valid
        if int(uid) <= 0 or int(uid) >= sys.maxint / 100 or int(yrs_dev) < 0:
            flash("Invalid ID or EXP! The value you entered is either too large or negative.")
            return render_template('register_gamer.html')
        cmd = "select * from users where users.uid =%s"
        cursor = g.conn.execute(cmd, (uid))

        # check uid unique
        if cursor.rowcount > 0:
            flash("That ID is already taken! Choose another one.")
            return render_template('register_dev.html')
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


@app.route('/filter/', methods=['GET', 'POST'])
def filter():
    if request.method == 'POST':
        os = request.form['os']
        gameplay = request.form['gameplay']
        genre = request.form['genre']

        filtered_os = []
        # filter OS:
        if os != "all":
            cmd = "select games.gameid from games except (select games.gameid from games, systemrequirements_has where games.gameid = systemrequirements_has.gameid and systemrequirements_has.OS=%s)"
            filtered_os = filter_game(cmd, os)

        filtered_gameplay = []
        # filter gameplay:
        if gameplay != "all":
            cmd = "select games.gameid from games where games.gameplay !=%s"
            filtered_gameplay = filter_game(cmd, gameplay)

        filtered_genre = []
        # filter genre
        if genre != "all":
            cmd = "select games.gameid from games where games.genre !=%s"
            filtered_genre = filter_game(cmd, genre)

        print filtered_os
        print filtered_gameplay
        print filtered_genre
        return redirect(url_for('index', filtered_os=filtered_os, filtered_gameplay=filtered_gameplay, filtered_genre=filtered_genre))

    return redirect(url_for('index'))


def filter_game(cmd, arg):
    games = []
    cursor = g.conn.execute(cmd, (arg))
    for result in cursor:
        games.append(result['gameid'])

    return games