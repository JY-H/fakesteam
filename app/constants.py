class sql_queries:
    def __init__(self):
        # ACCESSORS
        self.SELECT_USER="SELECT * FROM users WHERE users.uid =%s"
        self.SELECT_GAMER="SELECT * FROM gamers WHERE gamers.uid=%s"
        self.SELECT_DEVELOPER="SELECT * FROM developers WHERE developers.uid=%s"
        self.SELECT_GAME="SELECT * FROM games WHERE games.gameid =%s"

        self.GET_USER_NAME="SELECT name FROM users WHERE users.uid=%s"
        self.GET_GAMER_USERNAME="SELECT * FROM gamers WHERE gamers.username=%s"
        self.FILTER_OS="SELECT evaluate.gameid FROM evaluate except (SELECT evaluate.gameid FROM evaluate, systemrequirements_has WHERE evaluate.gameid = systemrequirements_has.gameid AND systemrequirements_has.OS=%s)"
        self.FILTER_GAMEPLAY="SELECT games.gameid FROM games WHERE games.gameplay !=%s AND games.gameid IN (SELECT gameid FROM evaluate)"
        self.FILTER_GENRE="SELECT games.gameid FROM games WHERE games.genre !=%s AND games.gameid IN (SELECT gameid FROM evaluate)"

        self.DISPLAY_STORE="SELECT gameid, title, url FROM games WHERE gameid IN (SELECT gameid FROM evaluate)"
        self.GAMER_LIBRARY="SELECT contains.gameid, games.title, games.url FROM library_owned, contains, games WHERE library_owned.uid =%s AND library_owned.libraryid = contains.libraryid AND contains.gameid IN (SELECT gameid FROM evaluate) AND contains.gameid = games.gameid"

        # MUTATORS
        self.ADD_USER="INSERT INTO users VALUES(%s, %s)"
        self.ADD_GAMER="INSERT INTO gamers VALUES(%s, %s)"
        self.ADD_DEVELOPER="INSERT INTO developers VALUES(%s, %s)"
        self.ADD_LIBRARY="INSERT INTO library_owned VALUES(%s)"
        self.ADD_GAME="INSERT INTO games (gameid, title, description, genre, gameplay, price, url) VALUES(%s, %s, %s, %s, %s, %s, %s)"
        self.ADD_SYSREQS="INSERT INTO systemrequirements_has (gameid, os, processor, graphics) VALUES(%s, %s, %s, %s)"
        self.SUBMIT_GAME="INSERT INTO submit VALUES(%s, %s)"


class messages:
    def __init__(self):
        # ERRORS
        self.BAD_ID="The ID you entered is invalid! It's either too large or negative."
        self.REDUNDANT_ID="That ID is already taken! Choose another one."
        self.REDUNDANT_USERNAME="That username is already taken! Choose another one."
        self.INVALID_LOGIN="Invalid Login. Please try again."
        self.NEGATIVE_PRICE="Price cannot be negative."
        self.NEGATIVE_EXP="Your experience cannot be negative."

        # SUCCESS
        self.SUCCESSFUL_GAME_SUBMISSION="Success! Your game will be added to the store when approved."
