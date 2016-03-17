# "/" aka HOME/LOGIN SCREEN
# Textbox for uid, submit button

# Games is a masterlist of all possible Games regardless of evaluation status
SELECT * FROM Games;

# Admins can only see Games that have NOT been already evaluated
SELECT gameid, title, price FROM Games WHERE gameid NOT IN (SELECT gameid FROM Evaluate);

# Gamers can only see Games that have been evaluated
SELECT gameid, title, price FROM Games WHERE gameid IN (SELECT gameid FROM Evaluate);