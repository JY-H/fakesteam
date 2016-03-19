# fakesteam
## TODO:
#### Login/Registration
* ~~Login Page~~
* ~~Registration for Gamers and Developers~~
* ~~Logout~~
* ~~Login button should change to a welcome message upon login.~~
* ~~Error handling for existing UID or username.~~
* ~~Create empty library upon gamer registration~~
* ~~Error handling for negative UID or years of experience.~~
* ~~Upon login, change nav bar to correspond to user permissions.~~
* Add password authentication (opt., not in part 1 description)

#### Library/Submit/Evaluate
* Based on the user's permissions, set up library/submission/evaluation pages. 
    * ~~gamers can view games owned.~~
    * ~~developers can submit new games, which cannot yet be viewed by gamers.~~
    * admins can evaluate games submitted by developers. 

#### Games
* ~~Store page; views all available games.~~
* ~~Filter function for the store page, allowing filter by OS, gameplay, and genre.~~
* Set up a single page for Games where all its information is displayed. Generate dynamically. 
* Purchase button that redirects to login if not currently logged in, and adds the game to the gamer's library otherwise. 
* Rate button that redirects to the community page (optional). 

#### Community
* ~~Set up a community page where gamers, admins, developers can post reviews for a specific game.~~ 

#### Misc
* Error handling. 

## DB CHANGE LOG:
* libraryid is now autoincrement
* developers no longer have platform as an attribute.
* games now have url as an attribute.
* games: title now has the UNIQUE constraint. 
