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
    cursor = g.conn.execute("SELECT gameid, title, url FROM games WHERE gameid IN (SELECT gameid FROM evaluate)")
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

    uid, user, permissions = get_user_info()

    return render_template('index.html', games=filtered_games, name=user, permissions=permissions)

@app.route('/library/')
def library():
    owned_games = []
    uid, user, permissions = get_user_info()

    if uid:
        # get player owned games:
        cmd = "SELECT contains.gameid, games.title, games.url FROM library_owned, contains, games WHERE library_owned.uid =%s AND library_owned.libraryid = contains.libraryid AND contains.gameid IN (SELECT gameid FROM evaluate) AND contains.gameid = games.gameid"
        cursor = g.conn.execute(cmd, (uid))
        for result in cursor:
            game = {}
            game['gameid'] = result['gameid']
            game['title'] = result['title']
            game['url'] = result['url']
            owned_games.append(game)
        cursor.close()

    return render_template('library.html', games=owned_games, name=user, permissions=permissions)

@app.route('/submit/', methods=['GET', 'POST'])
def submit():
    uid, user, permissions = get_user_info()

    return render_template('submit.html', name=user, permissions=permissions)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uid = request.form['uid']
        cmd = "SELECT * FROM users WHERE users.uid =%s"
        cursor = g.conn.execute(cmd, (uid))

        if cursor.rowcount <= 0:
            flash("Invalid ID. Please try again.")
            cursor.close()
            return render_template('login.html')
        else:
            cmd = "SELECT name FROM users WHERE users.uid=%s"
            cursor = g.conn.execute(cmd, (uid))
            name = cursor.fetchone()

            # check if user is developer, gamer, or admin
            # have to be either of the three.
            cmd = "SELECT * FROM gamers WHERE gamers.uid=%s"
            cursor = g.conn.execute(cmd, (uid))
            # gamer
            if cursor.rowcount > 0:
                set_session_info(uid, str(name.name), 'gamer')
            else:
                # developer
                cmd = "SELECT * FROM developers WHERE developers.uid=%s"
                cursor = g.conn.execute(cmd, (uid))
                if cursor.rowcount > 0:
                    set_session_info(uid, str(name.name), 'dev')
                # admin
                else:
                    set_session_info(uid, str(name.name), 'admin')

            cursor.close()
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
        cmd = "SELECT * FROM users WHERE users.uid =%s"
        cursor = g.conn.execute(cmd, (uid))
        if cursor.rowcount > 0:
            flash("That ID is already taken! Choose another one.")
            cursor.close()
            return render_template('register_gamer.html')

        # check username unique
        cmd = "SELECT * FROM gamers WHERE gamers.username=%s"
        cursor = g.conn.execute(cmd, (username))
        if cursor.rowcount > 0:
            flash("That username is already taken! Choose another one.")
            cursor.close()
            return render_template('register_gamer.html')

        cmd = "INSERT INTO users VALUES(%s, %s)"
        g.conn.execute(cmd, (uid, name))
        cmd = "INSERT INTO gamers VALUES(%s, %s)"
        g.conn.execute(cmd, (uid, username))


        # generate empty library
        cmd = "INSERT INTO library_owned VALUES(%s)"
        g.conn.execute(cmd, (uid))
        cursor.close()
        gc.collect()

        set_session_info(uid, name, 'gamer')

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
        cmd = "SELECT * FROM users WHERE users.uid =%s"
        cursor = g.conn.execute(cmd, (uid))

        # check uid unique
        if cursor.rowcount > 0:
            flash("That ID is already taken! Choose another one.")
            cursor.close()
            return render_template('register_dev.html')
        else:
            cmd = "INSERT INTO users VALUES(%s, %s)"
            g.conn.execute(cmd, (uid, name))
            cmd = "INSERT INTO developers VALUES(%s, %s)"
            g.conn.execute(cmd, (uid, yrs_dev))
        cursor.close()
        g.conn.close()
        gc.collect()

        set_session_info(uid, name, 'dev')

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
            cmd = "SELECT evaluate.gameid FROM evaluate except (SELECT evaluate.gameid FROM evaluate, systemrequirements_has WHERE evaluate.gameid = systemrequirements_has.gameid AND systemrequirements_has.OS=%s)"
            filtered_os = filter_game(cmd, os)

        filtered_gameplay = []
        # filter gameplay:
        if gameplay != "all":
            cmd = "SELECT games.gameid FROM games WHERE games.gameplay !=%s AND games.gameid IN (SELECT gameid FROM evaluate)"
            filtered_gameplay = filter_game(cmd, gameplay)

        filtered_genre = []
        # filter genre
        if genre != "all":
            cmd = "SELECT games.gameid FROM games WHERE games.genre !=%s AND games.gameid IN (SELECT gameid FROM evaluate)"
            filtered_genre = filter_game(cmd, genre)

        print filtered_os
        print filtered_gameplay
        print filtered_genre
        return redirect(url_for('index', filtered_os=filtered_os, filtered_gameplay=filtered_gameplay, filtered_genre=filtered_genre))

    return redirect(url_for('index'))


def get_user_info():
    user = None
    permissions = None
    uid = None
    if session.has_key('uid'):
        uid = session['uid']
        user = session['name']
        permissions = session['permissions']

    return uid, user, permissions

def set_session_info(uid, name, permissions):
    session['logged_in'] = True
    session['uid'] = uid
    session['name'] = name
    session['permissions'] = permissions

def filter_game(cmd, arg):
    games = []
    cursor = g.conn.execute(cmd, (arg))
    for result in cursor:
        games.append(result['gameid'])

    cursor.close()
    return games