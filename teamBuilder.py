'''
  Fantasy Team Builder.
  1) Parses data from Excel doc. 
  2) Computation for past data:
    a) Compute usable parameters for each player based on parsed data. X
    b) Visualize trends in each player's performance. X
    c) Find the best optimization of forwards based on past data.
  2) Projected data:
    a) Predict next week's performance for each player.
    b) Visualize the projections.
    c) Find the best optimization of forwards based on projected data.

Functionality to add:
  - Eventually change this all to do it by scraping the website for the point data.
  - Provide a plot of a specific player's trends, player entered by user
  - Provide data for a specific player, entered by user
  - Turn players into objects
  - Put code into functions
'''
import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np 



class Player(object):

  def __init__(self, d):
    self.name = d['name']
    self.position = [d['position_1'], d['position_2']]
    self.ppg, self.ptotal, self.ppweek = self.calculate_player_stats(d) 


  def get_name(self):
    return self.name

  def get_position(self):
    return self.position

  def get_stats(self):
    return self.ppg, self.ptotal, self.ppweek

  
  def calculate_player_stats(self, player):
    '''
      input: none
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
      print("[name, ppg 1, ppg 2, ppg 3, ptot 1, ptot 2, ptot 3, ppweek 1, ppweek 2, ppweek 3]")
    print(self.name, self.ppg, self.ptotal, self.ppweek)

  def plot_player_stats(self):
    weeks = [-1, -2, -3]
    plt.plot(weeks, self.ppg, 'r', weeks, self.ppweek, 'b', weeks, self.ptotal, 'g')
    plt.title(self.name)
    plt.xlabel('Weeks ago')
    plt.ylabel('Value')
    plt.show()

  def predict_next_player_points(self):
    pass




class Team(object):
  '''
    player_list: a list of all Player objects on the team
    starting_roster: a list of all Player objects set to play in a corresponding position
  '''
  def __init__(self, path):

    self.player_list = self.create_roster(path) 
    self.starting_roster = [
                              ['C', 'L', 'R', 'D', 'G'],
                              [ [], [], [], [], []]
                           ] #list of 5 objects, each object's 2nd element is a list of players

  def create_roster(self, path):
    '''
      input: string, path to excel file with data of proper form
      return: list, with each element being a complete Player object
    '''
    df = pd.read_excel(path)
    df_as_dict = df.to_dict('records')
    players = []
    for i in range(len(df_as_dict)):
      players.append(Player(df_as_dict[i]))

    return players 


  def print_player_list(self, just_roster=False, sub_list = None):
    if sub_list is not None:
        for p in sub_list:
            print(p.get_name())
    elif just_roster:
      for j in range(0,len(self.starting_roster[0])):
        print("\n" + self.starting_roster[0][j] + ":")
        for i in range(0,len(self.starting_roster[1][j])):
          p = self.starting_roster[1][j][i]
          print(p.get_name())
    else:
      for p in self.player_list:
        print(p.get_name())


  def print_team_stats(self, just_roster=False):
    print("[name, ppg 1, ppg 2, ppg 3, ptot 1, ptot 2, ptot 3, ppweek 1, ppweek 2, ppweek 3]")
    if just_roster:
      for name in self.starting_roster():
        p_ = self.find_player_by_name(name)
        p_.print_player_stats(info_bar=False)
    else:
      for p in self.player_list:
        p.print_player_stats(info_bar=False)



  def get_player_by_name(self, name):
    '''
      input: a string, a player name
      output: a Player object with the designated name, or 'null' if none found for a name
    '''
    for p in self.player_list: # <- can turn to lambda expression??
      assert type(name) is 'string' 
      if name == p.name: 
        return p
    
    return None


  def get_player_by_index(self, i):
    '''
      input: int, index of player in player_list
      output: a Player object corresponding to index given
    '''
    if i >= 0 and i < len(self.player_list): 
      return  self.player_list[i]

    return None 


  def get_players_by_position(self, position):
    '''
      input: string, either 'C', 'L', 'R', 'G', or 'D'
      return: list of all Player objects that play that position, or 'null' if none found
    '''
    result = []
    for p in self.player_list: # <- can turn to lambda expression??
      if position in p.position: 
        result.append(p)
    
    return result



  def set_optimal_starting_roster(self):
    '''
      input: none
      do: find the optimal combination of 2 C, 2 LW, and 2 RW from the team list and update roster 
          with this info 
    '''
    pass

  def predict_team_next_points(self, just_roster=False):
    '''
      input: none
      return: total number of points that the team (or just starting roster) is expected to get
    '''
    pass

  def set_random_starting_roster(self):
    '''
      input: none
      do: update roster attribute with a random but legal combination
    '''
    
    # Set right wingers
    RW = self.get_players_by_position('R')
    self.starting_roster[1][2] = RW[0:2]
    
    # Set left wingers
    LW = self.get_players_by_position('L')
    self.starting_roster[1][1] = LW[0:2]
    
    # Set centres
    C = self.get_players_by_position('C')
    self.starting_roster[1][0] = C[0:2]
    
    
    # Set defense
    defense = self.get_players_by_position('D')
    self.starting_roster[1][3] = defense[0:4]
    
    # Set goalies
    goalies = self.get_players_by_position('G')
    self.starting_roster[1][4] = goalies[0:2]
    
    # start with shortest list
    if len(RW) <= len(C) and len(RW) <= len(LW):
        # pick two from RW because it is the shortest
        RW_to_play = RW[0:2]
        #RW_remaining = RW[2:]
        if len(C) <= len(LW):
            C_remaining = C[:]
            C_to_play = []
            for i in range(0, len(C)):
                if C[i] in RW_to_play:
                    C_remaining.remove(C[i])
            C_to_play = C_remaining[0:2]
            C_remaining = C_remaining[2:]
        else: #LW < C
            LW_remaining = LW[:]
            LW_to_play = []
            for i in range(0, len(LW)):
                if LW[i] in RW_to_play:
                    LW_remaining.remove(LW[i])
            for i in range(0, len(LW)):
                if LW[i] in C_to_play:
                    LW_remaining.remove(LW[i])
            LW_to_play = LW_remaining[0:2]
            LW_remaining = LW_remaining[2:]
        self.starting_roster[1][2] = RW_to_play
        self.starting_roster[1][1] = LW_to_play
        self.starting_roster[1][0] = C_to_play
    elif len(LW) <= len(C) and len(LW) <= len(RW):
        LW_to_play = LW[0:2]
        #LW_remaining = LW[2:]
        self.starting_roster[1][1] = LW_to_play
        print("LW is smallest")
    
    elif len(C) <= len(RW) and len(C) <= len(LW):
        C_to_play = C[0:2]
        #C_remaining = C[2:]
        self.starting_roster[1][0] = C_to_play
    
    
        
    



'''
if __name__ == '__main__':
    roster = set_roster('FantasyTeamPoints.xlsx')

'''


