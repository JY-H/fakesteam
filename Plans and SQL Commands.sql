# "/" aka HOME/LOGIN SCREEN
# Textbox for uid, submit button

# Games is a masterlist of all possible Games regardless of evaluation status
SELECT * FROM Games;

# Admins can only see Games that have NOT been already evaluated
SELECT gameid, title, price FROM Games WHERE gameid NOT IN (SELECT gameid FROM Evaluate);

# Gamers/"store" can only see Games that have been evaluated; filter and sort as needed
SELECT gameid, title, price FROM Games WHERE gameid IN (SELECT gameid FROM Evaluate) [AND os = "<input>"...etc][ORDER BY "<attr>" ASC/DESC];

# Gamers/Library can only see what the Gamer owns
SELECT gameid, title, genre, gameplay FROM Games, Library_Owned, Contains WHERE Games.gameid = Library_Owned.gameid
AND Library_Owned.libraryid = Contains.libraryid AND gameid IN (SELECT gameid FROM Evaluate);