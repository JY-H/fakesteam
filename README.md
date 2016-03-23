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
* ~~Based on the user's permissions, set up library/submission/evaluation pages.~~
    * ~~gamers can view games owned.~~
    * ~~developers can submit new games, which cannot yet be viewed by gamers.~~
    * ~~admins can view games submitted by developers.~~
* Filter games on the evaluation page according to the admin's assigned team. (opt.)

#### Games
* ~~Store page; views all available games.~~
* ~~Filter function for the store page, allowing filter by OS, gameplay, and genre.~~
* ~~Set up a single page for Games where all its information is displayed. Generate dynamically.~~ 
* ~~Purchase button that redirects to login if not currently logged in, and adds the game to the gamer's library otherwise.~~
    * ~~Purchase should only be allowed for gamers and for games that have been approved.~~
* ~~Approve, reject buttons that add game to the store / delete game if the user permission is admin.~~

#### Community
* ~~Set up a community page where gamers, admins, developers can post reviews for a specific game.~~ 

#### Misc
* Error handling. 
    * Should users be allowed to review games that they do not own? (Dropdown menu for game titles on the reviews page, and only display review page for gamers?)
    * check stars less than 5.
    * parse review commentary such that new line renders.

## DB CHANGE LOG:
* libraryid is now autoincrement
* developers no longer have platform as an attribute.
* games now have url as an attribute.
* games: title now has the UNIQUE constraint. 
