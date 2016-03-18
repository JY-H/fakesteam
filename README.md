# fakesteam
## TODO:
#### Login/Registration
* Create empty library for gamer registration
* Upon login, change nav bar to correspond to user permissions

#### Library/Submit/Evaluate
* Based on the user's permissions, set up library/submission/evaluation pages. 
    * gamers can view games owned 
    * developers can submit new games, which cannot yet be viewed by gamers
    * admins can evaluate games submitted by developers. 
* Should be a single page, dynamically generated based on permissions. 

#### Games
* Set up a single page for Games where all its information is displayed. Generate dynamically. 
* Purchase button that redirects to login if not currently logged in, and adds the game to the gamer's library otherwise. 
* Rate button that redirects to the community page (optional). 

#### Community
* Set up a community page where gamers, admins, developers can post reviews for a specific game. 

#### Misc
* Error handling. 
