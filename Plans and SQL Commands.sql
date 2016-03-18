# "/" aka HOME/LOGIN SCREEN
# Textbox for uid, submit button

# Games is a masterlist of all possible Games regardless of evaluation status
SELECT * FROM Games;

# Admins can only see Games that have NOT been already evaluated
SELECT gameid, title, price FROM Games WHERE gameid NOT IN (SELECT gameid FROM Evaluate);

# Gamers/"store" can only see Games that have been evaluated; filter and sort as needed
SELECT gameid, title, price FROM Games WHERE gameid IN (SELECT gameid FROM Evaluate);

# Gamers/Library can only see what the Gamer owns
SELECT contains.gameid, games.title, games.url FROM library_owned, contains, games WHERE library_owned.uid =%s  AND library_owned.libraryid = contains.libraryid AND contains.gameid IN (SELECT gameid FROM evaluate) AND contains.gameid = games.gameid;

# Filtering by OS
SELECT evaluate.gameid FROM evaluate except (SELECT evaluate.gameid FROM evaluate, systemrequirements_has WHERE evaluate.gameid = systemrequirements_has.gameid AND systemrequirements_has.OS=%s);

# Filtering by gameplay
SELECT games.gameid FROM games WHERE games.gameplay !=%s AND games.gameid IN (SELECT gameid FROM evaluate);

# Filtering by genre
SELECT games.gameid FROM games WHERE games.genre !=%s AND games.gameid IN (SELECT gameid FROM evaluate);



