# FantasyTeamBuilder
A tool for analyzing and visualizing team and player past and predicted performance, and developing an optimized starting roster for Yahoo Fantasy Hockey.

The Excel file contains data formatted in a specific schema, currently entered manually from the Yahoo Fantasy Hockey website. The data is fantasy points and games played overall, and in the last week, as well as upcoming number of games, for all players on a specific Fantasy Team.

The teamBuilder.py file contains two object classes, Team and Player. Player holds a single player and all their pertinent data, Team holds all the players on the Fantasy team. These classes have several functions to help initiate the objects as well as to perform calculations, predictions, and roster optimization, as examples. 

The module can be imported to use the objects and functions on their own. Running teamBuilder.py script will run a set of example functionality:
1) Instantiate a team and show its stats
2) Set optimized starting roster, show it and show predicted points
3) Pick a random player and show points, info, and trends

Lots of added functionality and features to come:
- Reformatting of Excel data to be more continuous
- Recalculation of data from raw "G, A, GP, S, BLK, +/-, GA, W, SO" data for players and goalies
  - Available from any sports stats site
  - Requires knowing the user's league's specific scoring schema (point multiplication factors)
- Automation of data entry via web scraping
- Migration of data to a database 
