from flask import Flask, flash, request, render_template, g, redirect, Response, url_for, session
from app import app
from server import test_server, fakesteam_server
from constants import sql_queries, messages
import gc
import sys

# start server
server = fakesteam_server()
# initiate helpers
queries = sql_queries()
msgs = messages()

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
    """
    Function for retrieving info and displaying the store page.
    :return:
    """
    cursor = g.conn.execute(queries.DISPLAY_STORE)
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

    for i in range(len(games)):
        gameid = games[i].get('gameid')
        if unicode(gameid) not in excluded:
            filtered_games.append(games[i])

    uid, user, permissions = get_user_info()

    return render_template('index.html', games=filtered_games, name=user, permissions=permissions)

@app.route('/library/')
def library():
    """
    Displays all gamer-owned games.
    :return:
    """
    owned_games = []
    uid, user, permissions = get_user_info()

    if uid:
        # get player owned games:
        cursor = g.conn.execute(queries.GAMER_LIBRARY, (uid))
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
    """
    Allows for submission of a new game, given valid fields.
    :return:
    """
    uid, user, permissions = get_user_info()
    if request.method == 'POST':
        uid = session['uid']
        gameid = request.form['gameid']
        price = request.form['price']
        title = request.form['title']
        description = request.form['description']
        genre = request.form['genre']
        gameplay = request.form['gameplay']
        url = request.form['url']

        # check price at least 0
        if int(price) < 0:
            flash(msgs.NEGATIVE_PRICE)
            return render_template('submit.html', name=user, permissions=permissions)

        # check gameid valid
        if not is_valid(gameid):
            flash(msgs.BAD_ID)
            return render_template('submit.html', name=user, permissions=permissions)

        # check gameid unique
        if not is_unique(queries.SELECT_GAME, gameid):
            flash(msgs.REDUNDANT_ID)
            return render_template('submit.html', name=user, permissions=permissions)

        # add game
        g.conn.execute(queries.ADD_GAME, (gameid, title, description, genre, gameplay, price, url))

        # add system requirements
        processor = request.form['windows-processor']
        graphics = request.form['windows-graphics']
        g.conn.execute(queries.ADD_SYSREQS, (gameid, 'windows', processor, graphics))

        # add other sys reqs if input exists
        if request.form['mac-processor'] and request.form['mac-graphics']:
            processor = request.form['mac-processor']
            graphics = request.form['mac-graphics']
            g.conn.execute(queries.ADD_SYSREQS, (gameid, 'mac', processor, graphics))
        elif request.form['linux-processor'] and request.form['linux-graphics']:
            processor = request.form['linux-processor']
            graphics = request.form['linux-graphics']
            g.conn.execute(queries.ADD_SYSREQS, (gameid, 'linux', processor, graphics))

        # add to submit table
        g.conn.execute(queries.SUBMIT_GAME, (uid, gameid))

        flash(msgs.SUCCESSFUL_GAME_SUBMISSION)
        return render_template('submit.html', name=user, permissions=permissions)


    return render_template('submit.html', name=user, permissions=permissions)

@app.route('/rate/', methods=['GET', 'POST'])
def rate():
    """
    Allows the addition of a review to a game.
    :return:
    """
    uid, user, permissions = get_user_info()

    return render_template('rate.html', name=user, permissions=permissions)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    """
    Checks user credentials and changes page display based on his or her permissions
    :return:
    """
    if request.method == 'POST':
        uid = request.form['uid']
        cursor = g.conn.execute(queries.SELECT_USER, (uid))

        if cursor.rowcount <= 0:
            flash(msgs.INVALID_LOGIN)
            cursor.close()
            return render_template('login.html')
        else:
            cursor = g.conn.execute(queries.GET_USER_NAME, (uid))
            name = cursor.fetchone()

            # check if user is developer, gamer, or admin
            # have to be either of the three.
            cursor = g.conn.execute(queries.SELECT_GAMER, (uid))
            # gamer
            if cursor.rowcount > 0:
                set_session_info(uid, str(name.name), 'gamer')
            else:
                # developer
                cursor = g.conn.execute(queries.SELECT_DEVELOPER, (uid))
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
    """
    Clears session
    :return:
    """
    session.clear()
    return redirect(url_for('index'))

@app.route('/register_gamer/', methods=['GET', 'POST'])
def register_gamer():
    """
    Creates a new user as a gamer.
    An empty library is created as well.
    :return:
    """
    # if it's a POST request
    if request.method == 'POST':
        # get the information
        uid = request.form['uid']
        username = request.form['username']
        name = request.form['name']

        # check uid valid
        if not is_valid(uid):
            flash(msgs.BAD_ID)
            return render_template('register_gamer.html')

        # check uid unique
        if not is_unique(queries.SELECT_USER, uid):
            flash(msgs.REDUNDANT_ID)
            return render_template('register_gamer.html')

        # check username unique
        if not is_unique(queries.GET_GAMER_USERNAME, username):
            flash(msgs.REDUNDANT_USERNAME)
            return render_template('register_gamer.html')

        g.conn.execute(queries.ADD_USER, (uid, name))
        g.conn.execute(queries.ADD_GAMER, (uid, username))

        # generate empty library
        g.conn.execute(queries.ADD_LIBRARY, (uid))
        gc.collect()

        set_session_info(uid, name, 'gamer')

        return redirect(url_for('index'))

    return render_template('register_gamer.html')


@app.route('/register_dev/', methods=['GET', 'POST'])
def register_dev():
    """
    Creates a new user as a developer.
    :return:
    """
    # if it's a POST request
    if request.method == 'POST':
        # get the information
        uid = request.form['uid']
        name = request.form['name']
        yrs_dev = request.form['exp_dev']

        # check valid exp
        if int(yrs_dev) < 0:
            flash(msgs.NEGATIVE_EXP)
            return render_template('register_gamer.html')

        # check uid valid
        if not is_valid(uid):
            flash(msgs.BAD_ID)
            return render_template('register_gamer.html')
        cmd = "SELECT * FROM users WHERE users.uid =%s"
        cursor = g.conn.execute(cmd, (uid))

        # check uid unique
        if not is_unique(queries.SELECT_USER, uid):
            flash(msgs.REDUNDANT_ID)
            return render_template('register_dev.html')
        else:
            g.conn.execute(queries.ADD_USER, (uid, name))
            g.conn.execute(queries.ADD_DEVELOPER, (uid, yrs_dev))
        cursor.close()
        g.conn.close()
        gc.collect()

        set_session_info(uid, name, 'dev')
        return redirect(url_for('index'))

    return render_template('register_dev.html')


@app.route('/filter/', methods=['GET', 'POST'])
def filter():
    """
    Filters the selection of games based on the options selected.
    :return:
    """
    if request.method == 'POST':
        os = request.form['os']
        gameplay = request.form['gameplay']
        genre = request.form['genre']

        filtered_os = []
        # filter OS:
        if os != "all":
            filtered_os = filter_game(queries.FILTER_OS, os)

        filtered_gameplay = []
        # filter gameplay:
        if gameplay != "all":
            filtered_gameplay = filter_game(queries.FILTER_GAMEPLAY, gameplay)

        filtered_genre = []
        # filter genre
        if genre != "all":
            filtered_genre = filter_game(queries.FILTER_GENRE, genre)

        return redirect(url_for('index', filtered_os=filtered_os, filtered_gameplay=filtered_gameplay, filtered_genre=filtered_genre))

    return redirect(url_for('index'))


def get_user_info():
    """
    retrieves user info for the current session
    :return:
    """
    user = None
    permissions = None
    uid = None
    if session.has_key('uid'):
        uid = session['uid']
        user = session['name']
        permissions = session['permissions']

    return uid, user, permissions

def set_session_info(uid, name, permissions):
    """
    sets session info
    :param uid: user id
    :param name: name
    :param permissions: gamer, dev, or admin
    :return:
    """
    session['logged_in'] = True
    session['uid'] = uid
    session['name'] = name
    session['permissions'] = permissions


def is_valid(id):
    """
    checks is ID entered is valid
    :param id: ID entered
    :return:
    """
    if int(id) <= 0 or int(id) >= sys.maxint / 100:
        return False

    return True

def is_unique(query, id):
    """
    Checks if the given id is unique
    :param query: db query
    :param id: id given
    :return:
    """
    cursor = g.conn.execute(query, (id))
    if cursor.rowcount > 0:
        cursor.close()
        return False

    return True

def filter_game(cmd, arg):
    """
    Retrieves all excluded games' gameid based on the query
    :param cmd: query
    :param arg: filter criteria (os, gameplay, genre)
    :return:
    """
    games = []
    cursor = g.conn.execute(cmd, (arg))
    for result in cursor:
        games.append(result['gameid'])

    cursor.close()
    return games