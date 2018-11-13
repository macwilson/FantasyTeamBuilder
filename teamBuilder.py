'''
FANTASY TEAM BUILDER
by @macwilson on github
https://github.com/macwilson/FantasyTeamBuilder 
Created October 2018

Main Functionality:
  1) Parses data from Excel doc. 
  2) Computation and visualization for past data.
  3) Predicts next week's fantasy points.
  4) Find best optimization of a roster for next week. 

Functionality to add:
  - Eventually change this all to do it by scraping the website for the point data.
  - Migrate data to a database?
  - Merge all datasheets into one continuous set + add object functionality for this
'''

import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np 
from itertools import combinations
from statistics import mean


# ----------------------- PLAYER OBJECT -------------------------
class Player(object):
    '''
      DESCRIPTION:
          A Player object contains all pertinent data for a single player.
          
      ATTRIBUTES:
          name: string identifier of player
          position: list of up to two strings of type 'C' for centre, 'L' for 
                    left wing, 'R' for right wing, 'D' for defense, 'G' for 
                    goalie (only forwards C/L/R will have more than 1)
          ppg: list of floats indicating points per game [1wkago, 2wksago, 3wksago]
          ptotal: list of floats indicating total points [1wkago, 2wksago, 3wksago]
          ppweek: list of floats indicating weekly total points [1wago, 2wago, 3wago]
          next_week_games: integer, number of games in next week
          next_week_points: float, predicted total points for the next week
          
      FUNCTIONS:
          __init__
          get_name
          get_position
          get_stats
          get_prediction
          calculate_player_stats
          print_player_stats
          plot_player_stats
          predict_player_next_points
    '''

    def __init__(self, d):
        self.name = d['name']
        self.position = [d['position_1'], d['position_2']]
        self.ppg, self.ptotal, self.ppweek = self.calculate_player_stats(d) 
        self.next_week_games = d['games_this_week']
        self.next_week_points = self.predict_player_next_points()


    def get_name(self):
        return self.name

    def get_position(self):
        return self.position

    def get_stats(self):
        return self.ppg, self.ptotal, self.ppweek
    
    def get_prediction(self):
        return self.next_week_points

  
    def calculate_player_stats(self, player):
        '''
          @param: none
          return: three lists of data for [last 7 days, 7 days before that, 16 days before that]
        '''
        ppweek1 = 0
        ppweek2 = 0 
        ppweek3 = 0
        ppg_wk1 = 0
        ppg_wk2 = 0
        ppg_before = 0
        ptot_wk1 = round(player['points_30'], 2) #all the points until now, 16 + 7 + 7 days
        ptot_before = round((player['points_30']-player['points_14']), 2) # earliest 16 days of data
    
        # Find ppg for the most recent week
        if player['games_7'] is not 0:  # If 0 games played, leave ppg and points as 0.
            ppweek1 = round(player['points_7'] , 2)
            ppg_wk1 = round(ppweek1/player['games_7'], 2)
    
        ptot_wk2 = round(ptot_wk1 - ppweek1, 2) # earliest 16 + 7 days
        if player['games_14'] is not 0: 
            ppweek2 = round(player['points_14']-player['points_7'], 2)
            ppg_wk2 = round(ppweek2/(player['games_14']-player['games_7']), 2)
    
        
        # This one is tricky since it is not previous + 7 days, it is previous + 16 days.
        # Points per week will be normalized to 7 days. Points per game is as usual.
        ppweek3 = round(ptot_before*(7/16), 2)
        games_wk3 = player['games_30']-player['games_14']
        if games_wk3 is not 0: 
            ppg_before = round(ptot_before/games_wk3, 2)
    
        return [ppg_wk1, ppg_wk2, ppg_before], [ptot_wk1, ptot_wk2, ptot_before], [ppweek1, ppweek2, ppweek3]
    
    
    def print_player_stats(self, info_bar=True):
        if info_bar:
            print("[name, ppg average, total points, next week predicted points]")
        print(self.name, round(mean(self.ppg), 2), self.ptotal[0], self.next_week_points)
    
    def plot_player_stats(self):
        weeks = [-1, -2, -3]
        p1, = plt.plot(weeks, self.ppg, 'r', label='ppg')
        p2, = plt.plot(weeks, self.ppweek, 'b', label='ppweek')
        p3, = plt.plot(weeks, self.ptotal, 'g', label='ptotal')
        plt.title(self.name)
        plt.xlabel('Weeks ago')
        plt.ylabel('Value')
        plt.legend()
        plt.show()
    
    def predict_player_next_points(self):
        return round((self.ppg[0]+self.ppg[1]+self.ppg[2])*self.next_week_games /3, 2)
        





# ---------------------- TEAM OBJECT ----------------------
class Team(object):
  '''
    DESCRIPTION:
        A Team object is a specified collection of Player objects.
  
    ATTRIBUTES:
        player_list: a list of all Player objects on the team.
        starting_roster: a dict of all positions and the Player objects set to 
                        play that position.
                    
    FUNCTIONS:
        __init__
        create_team
        print_player_list
        print_starting_roster
        print_team_stats
        print_starting_roster_stats
        get_player_by_name
        get_player_by_index
        get_players_by_position
        set_optimal_starting_roster
        set_random_starting_roster
        predict_team_next_points
        predict_starting_roster_next_points
  '''
  
  def __init__(self, path):
    '''
      Instantiate a Team object.
      
      @param: path, a string indicating the path to the Excel sheet data
      @return: none
    '''
    self.player_list = self.create_team(path) 
    self.starting_roster = {'C': [], 'L': [], 'R': [], 'D': [], 'G': []}


  def create_team(self, path):
    '''
      For each player in the data file, make a player object.  
      
      @param: string, path to excel file 
      @return: players, list of Player objects
    '''
    
    df = pd.read_excel(path, sheetname='Nov12Data') # Newer version is sheet_name
    df_as_dict = df.to_dict('records')
    players = []
    for i in range(len(df_as_dict)):
      players.append(Player(df_as_dict[i])) 

    return players 


  def print_player_list(self, sub_list = None):
    '''
      Print names of all Players in Team, or within a Player list.
      
      @param: none, or a sub-list of Player objects 
      @return: none
    '''
    list_to_use = sub_list
    if sub_list is  None:
        list_to_use = self.player_list
    for p in list_to_use:
        print(p.get_name())
        
        
  def print_starting_roster(self):
    '''
      Print positions and names of all Players on the Team starting roster.
      
      @param: none
      @return: none
    '''
    for position in self.starting_roster.keys():
      print("\n" + position + ":")
      for i in range( len(self.starting_roster[position]) ):
        player = self.starting_roster[position][i]
        print(player.get_name())


  def print_team_stats(self,  sub_list=None):
    '''
      Print all Player statistics for the whole Team (or just the roster)
      
      @param: none, or binary "just_roster" value
      @return: none
    '''
    list_to_use = sub_list
    if sub_list is None:
        list_to_use = self.player_list
        
    print("\nTeam Stats:")
    print("[name, ppg average, total points, next week predicted points]")
    for p in list_to_use:
      p.print_player_stats(info_bar=False)
            
    
  def print_starting_roster_stats(self):
      '''
        Print all statistics for players on the stating roster
        
        @param: none
        @return: none
      '''
      
      print("\nStarting Roster Stats:")
      print("[name, ppg 1, ppg 2, ppg 3, ptot 1, ptot 2, ptot 3, ppweek 1, ppweek 2, ppweek 3]")
      for position in self.starting_roster.keys():
          for player in self.starting_roster[position]:
              player.print_player_stats(info_bar=False)


  def get_player_by_name(self, name):
    '''
      Given a player name, get the corresponding Player object. 
      
      @param: a string, a player name
      @return: a Player object with the designated name, or 'None" if none found
    '''
    for p in self.player_list:
      assert type(name) is str 
      if name == p.name: 
        return p
    
    return None


  def get_player_by_index(self, i):
    '''
      Return the player in the player list at a certain index.
      
      @param: int, index of player in player_list
      @return: a Player object corresponding to index given
    '''
    if i >= 0 and i < len(self.player_list): 
      return  self.player_list[i]

    return None 


  def get_players_by_position(self, position):
    '''
      Return a list of all Player objects that play that position.
      
      @param: string, either 'C', 'L', 'R', 'G', or 'D'
      @return: list of Player objects 
    '''
    result = []
    for p in self.player_list: # <- can turn to lambda expression??
      if position in p.position: 
        result.append(p)
    
    return result


  def predict_team_next_points(self, sub_list=None):
    '''
      Sum the predicted points of the whole Team, or a provided sub_list.
      
      @param: none, or sub_list of Players
      @return: total_points, float
    '''
    list_to_use = sub_list
    if sub_list is None:
        list_to_use = self.player_list
    total_points = 0
    for p in list_to_use:
        total_points = total_points + p.get_prediction()
        
    return round(total_points, 2)

  def predict_starting_roster_next_points(self):
    '''
      Sum the predicted points of the starting roster.
      
      @param: noneaallaa
      @return: total_points, float
    '''
    total_points = 0

    for position in self.starting_roster.keys():
        for player in self.starting_roster[position]:
            total_points = total_points + player.get_prediction()
    
    return round(total_points, 2)


  def set_optimal_starting_roster(self):
    '''
      Determine the combination of players that leads to the highest team score,
      based on predicted next week values. Set this combination to the roster. 
      This means finding 2C, 2L, and 2R that do not overlap. 
      
      @param: none
      @return: none
    '''    
    
    # FORWARDS:
    # Method:
    #   Enumerate all possible combinations
    #   Check if combination produces a maximum predicted sum
    
    RW = self.get_players_by_position('R')
    LW = self.get_players_by_position('L')
    C = self.get_players_by_position('C')
    
    max_fwd_sum = 0
    combo_sum = 0
    max_fwd_lineup = {'C': [], 'R': [], 'L': []}
    
    for Rpair in combinations(RW, 2):
        for Lpair in combinations(LW, 2):
            for Cpair in combinations(C, 2):
                
                concat_list = list(Rpair+Lpair+Cpair)
                concat_list_names = []
                for player in concat_list: concat_list_names.append(player.get_name())
                
                # If no elements are repeated, then the list is good 
                if (len(np.unique(concat_list_names)) == len(concat_list_names)):
                    
                    # At this point, we know we have a unique combination
                    # of 2C, 2LW, and 2RW.
                    # Calculate predicted sum and store if max.
                    combo_sum = self.predict_team_next_points(sub_list=concat_list)
                    
                    if combo_sum > max_fwd_sum:
                        max_fwd_sum = combo_sum
                        max_fwd_lineup['C'] = Cpair
                        max_fwd_lineup['R'] = Rpair
                        max_fwd_lineup['L'] = Lpair
    
    # Set the remaining maximum combo to the Team object's starting roster            
    self.starting_roster['C'] = max_fwd_lineup['C']
    self.starting_roster['R'] = max_fwd_lineup['R']
    self.starting_roster['L'] = max_fwd_lineup['L']
    
    
    # DEFENSE: 
    # Just sort by descending points and take top 4
    defense = self.get_players_by_position('D')
    defense.sort(key=lambda x: x.next_week_points, reverse=True)
    self.starting_roster['D'] = defense[0:4]
    
    #GOALIES:
    # Just sort by descending points and take top 2
    goalies = self.get_players_by_position('G')
    goalies.sort(key=lambda x: x.next_week_points, reverse=True)
    self.starting_roster['G'] = goalies[0:2]



  def set_random_starting_roster(self):
    '''
      Determine the first legal combination of 2R, 2C, 2L, 4D and 2G. 
      Set this to the starting roster. 
      
      @param: none
      @return: none
    '''
    # DEFENSE - take first 4
    defense = self.get_players_by_position('D')
    self.starting_roster['D'] = defense[0:4]
    
    # GOALIES - take first 2
    goalies = self.get_players_by_position('G')
    self.starting_roster['G'] = goalies[0:2]
    
    # FOR FORWARDS 
    # Get all possible players
    RW = self.get_players_by_position('R')
    LW = self.get_players_by_position('L')
    C = self.get_players_by_position('C')

    for Rpair in combinations(RW, 2):
        for Lpair in combinations(LW, 2):
            for Cpair in combinations(C, 2):
                
                concat_list = list(Rpair+Lpair+Cpair)
                concat_list_names = []
                for player in concat_list: concat_list_names.append(player.get_name())
                
                # If no elements are repeated, then the list is good 
                if (len(np.unique(concat_list_names)) == len(concat_list_names)):
    
                        # SET THESE FORWARDS TO THE ROSTER
                        self.starting_roster['R'] = Rpair
                        self.starting_roster['L'] = Lpair
                        self.starting_roster['C'] = Cpair
                        
                        #exit because we just need any working combo
                        return 
        
    

# --------------- MAIN FUNCTION ------------------
if __name__ == '__main__':
    '''
        1) Instantiate a team
        2) Print team stats
        3) Print OPTIMAL starting roster
        4) Print predicted roster points
        5) Pick a player by name
        6) Print player stats
        7) Plot player stats 
    '''
    testteam = Team('FantasyTeamPoints.xlsx')
    testteam.print_team_stats()
    testteam.set_optimal_starting_roster()
    print("")
    testteam.print_starting_roster()
    print("\nRoster Next Points:")
    print(testteam.predict_starting_roster_next_points())
    print("")
    p = testteam.get_player_by_name('Hall')
    p.print_player_stats()
    p.plot_player_stats()


    
    




