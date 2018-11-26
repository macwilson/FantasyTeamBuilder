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
      - columns "total_games, total_pts, last_wk_games, last_wk_pts, games_this_wk"
'''

import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np 
from itertools import combinations


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
          stats: a nested dictionary of points per game (ppg), total points 
                 (pts), and number of games (games), separated by time period 
                 (last week [last_week], next week [predicted], or overall)
          
          
      FUNCTIONS:
          __init__
          get_name
          get_position
          get_stats
          get_prediction
          calculate_player_stats
          print_player_stats
          plot_player_stats
          print_player_info
          predict_player_next_points
    '''

    def __init__(self, d):
        # Identity info
        self.name = d['name']
        self.position = [d['position_1'], d['position_2']]
        self.stats = {'predicted': {'pts': 0, 'games': 0, 'ppg': 0},
                      'last_week': {'pts': 0, 'games': 0, 'ppg': 0},
                      'total': {'pts': 0, 'games': 0, 'ppg': 0}
                      }
        self.calculate_player_stats(d) #Fill in the stats dictionary
        

    def get_name(self):
        '''
            Access and return the player's name as string.
        '''
        return self.name

    def get_position(self):
        '''
            Access and return the player's positions as list of strings
        '''
        
        return [x for x in self.position if str(x) != 'nan']
    
    def get_prediction(self):
        return self.stats['predicted']['pts']
    
    def get_stats(self, time=None, stat=None): 
        '''
           Access specified time period data, type of data, specific data cell, 
           or all data if none specified.
           
           @param: time, a string referring to a time period in stats dict
                   stat, a string referring to a type of stat in stats dict
                   Both can also be "None" (default)
           @return: A float (specific stat), a dict (period/type of stat), or
                    a nested dict (all stats)
        '''

        if time is not None:
            pass
            if stat is not None:
                # Return a single stat type for 1 time point
                return self.stats[time][stat] #float
            
            else:
                # Return range of stats for certain time
                return self.stats[time] #dict
            
        elif stat is not None: 
            # Return a range of stats of the same type
            return {'predicted': self.stats['predicted'][stat], 
                      'last_week': self.stats['last_week'][stat],
                      'total': self.stats['total'][stat]
                    }
        
        # ELSE: Return the whole dict, stat==None & time ==None
        return self.stats #nested dict
                
    
    def calculate_player_stats(self, player_data):
        '''
            Get points per game, total points, and number of games for time 
            periods of the total season up until now, the previous week, as
            well as the upcoming week. This includes making a call to the 
            prediction function that will predict how many points the player
            is expected to score in the upcoming week. Set all these to the
            self.stats nested dictionary attribute. 
            
            @param: player_data, a dictionary representing one row of data from
                    the Excel file containing all player data
            @return: none
        '''
        # Last week stats
        points_last_week = player_data['points_7']
        games_last_week = player_data['games_7']
        self.stats['last_week']['pts'] = points_last_week
        self.stats['last_week']['games'] = games_last_week
        self.stats['last_week']['ppg'] = round(points_last_week/games_last_week,2)
        
        # Overall stats
        games_total = player_data['games_total'] #Eventually change this to total
        points_total = player_data['points_total'] #Eventually change to points_total
        self.stats['total']['pts'] = points_total
        self.stats['total']['games'] = games_total
        self.stats['total']['ppg'] = round(points_total/games_total, 2) 
        
        # Predicted stats -> Call to predict_player_next_points()
        games_this_week = player_data['games_this_week']
        self.stats['predicted']['games'] = games_this_week
        points_this_week = self.predict_player_next_points()
        self.stats['predicted']['pts'] = points_this_week
        self.stats['predicted']['ppg'] = round(points_this_week/games_this_week, 2)
        
       
    
    def print_player_stats(self): 
        '''
           Print player stats in a nice pretty table.
        '''
        
        # table heading
        print('{:8} {:8} {:10} {:10}'.format("stat", "total", "last_wk", "next_wk_predict"))
        for stat in list(self.stats['total'].keys()):
            print('{:8} {:<8} {:<10} {:<10}'.format(
                    stat, #stat name
                    self.stats['total'][stat],
                    self.stats['last_week'][stat],
                    self.stats['predicted'][stat]
                    ))
        
    
    def print_player_info(self):
        '''
           Print player name, position, and stats. 
        '''
        print("\nPlayer: "+ self.get_name())
        print("Position: ", self.get_position())
        print("Stats: ")
        self.print_player_stats()
        
    
    def plot_player_stats(self): # DEPRECATED -> CHANGE
        '''
           Plot the progression of points per game, and total points, over time
           and predicted. Data points should be:
               1. Total before last week
               2. Total including last week
               3. Predicted after this week
        '''
        # Set the variables to plot
        time = ['before', 'last week', 'upcoming week']
        x = [0,1,2]
        pts_before = self.get_stats('total', 'pts') - self.get_stats('last_week', 'pts')
        ppg_before = pts_before / (self.get_stats('total', 'games') - self.get_stats('last_week', 'games'))
        pts_array = [pts_before, self.get_stats('total', 'pts'), self.get_stats('total','pts') + self.get_stats('predicted', 'pts')]
        ppg_array = [ppg_before, self.get_stats('last_week', 'ppg'), self.get_stats('predicted', 'ppg')]
        
        # Create the figure
        fig = plt.figure(1)
        fig.suptitle(self.get_name(), fontsize=16)
        
        # Subplot 1, total points
        plt.subplot(211)
        plt.xticks(x, time)
        plt.plot(x, pts_array, 'r', label='total points')
        plt.xlabel('Time Period')
        plt.ylabel('Total Points')
        plt.ylim(bottom=0, top=(max(pts_array) + 0.25*max(pts_array)))
        
        # Subplot 2, points per game
        plt.subplot(212)
        plt.xticks(x, time)
        plt.plot(x, ppg_array, 'b', label='points per game')
        plt.xlabel('Time Period')
        plt.ylabel('Points Per Game')
        plt.ylim(bottom=0, top=(max(ppg_array) + 0.25*max(ppg_array)))
        
        plt.show()
        
        
    
    def predict_player_next_points(self):
        '''
            Return the predicted points for the player for next week.
            This depends on the ppg metric we decide to use, and the number
            of games to play next week.
            For now the ppg metric is an overall average ppg, weighted x2 for
            the week immediately previous. 
            
            @return: float
        '''
        return round( ((self.stats['total']['ppg'] + 
                         self.stats['last_week']['ppg'] )/2 ) 
                         * self.stats['predicted']['games'], 2
                      )
 


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
        get_players_by_position
        set_optimal_starting_roster
        set_random_starting_roster
        predict_team_next_points
        predict_starting_roster_next_points
  '''
  
  def __init__(self, path):
    '''
      Instantiate a Team object. Player list gets imported, but starting 
      roster starts as unset - needs to be manually set later. 
      
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
    
    df = pd.read_excel(path, sheetname='Nov26Data') # Newer version is sheet_name
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
      Print all Player statistics for the whole Team (or a sub list)
      
      @param: none, or a sub_list list of Player objects
      @return: none
    '''
    list_to_use = sub_list
    if sub_list is None:
        list_to_use = self.player_list
        
    print("\nTeam Stats:")
    print('{:12} {:12} {:10} {:12} {:12} {:10}'.format("name", 
                                                 "position", 
                                                 "total_pts", 
                                                 "overall_ppg", 
                                                 "last_wk_ppg", 
                                                 "next_wk_ppg"))
    for p in list_to_use:
        print('{:12} {:12} {:<10} {:<12} {:<12} {:<10}'.format(
                                                     p.get_name(),
                                                     str(p.get_position()),
                                                     p.get_stats('total', 'pts'),
                                                     p.get_stats('total', 'ppg'),
                                                     p.get_stats('last_week', 'ppg'),
                                                     p.get_stats('predicted', 'ppg')
                                                    ))
                  
            
    
  def print_starting_roster_stats(self):
      '''
        Print all statistics for players on the stating roster
        
        @param: none
        @return: none
      '''
      
      print("\nStarting Roster Stats:")
      print('{:12} {:10} {:12} {:12} {:10}'.format("name", "total_pts", "overall_ppg", "last_wk_ppg", "next_wk_predict"))
      for position in self.starting_roster.keys():
          for p in self.starting_roster[position]:
              print('{:12} {:10} {:12} {:12} {:10}'.format(
                                          p.get_name(),
                                          p.get_stats('total', 'pts'),
                                          p.get_stats('total', 'ppg'),
                                          p.get_stats('last_week', 'ppg'),
                                          p.get_stats('predicted', 'pts')
                                                    ))


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


  def get_players_by_position(self, position):
    '''
      Return a list of all Player objects that play that position.
      
      @param: string, either 'C', 'L', 'R', 'G', or 'D'
      @return: list of Player objects 
    '''
    result = []
    for p in self.player_list: 
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
    #   Find all possible combinations
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
    defense.sort(key=lambda x: x.get_prediction(), reverse=True)
    self.starting_roster['D'] = defense[0:4]
    
    #GOALIES:
    # Just sort by descending points and take top 2
    goalies = self.get_players_by_position('G')
    goalies.sort(key=lambda x: x.get_prediction(), reverse=True)
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
    SHOW BASIC FUNCTIONALITY:
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
    print("\nStarting Roster:")
    testteam.print_starting_roster()
    print("\nPredicted Roster Points: ", testteam.predict_starting_roster_next_points())
    
    
    p = testteam.get_player_by_name('Hellebuyck')
    p.print_player_info()
    p.plot_player_stats()
    


    
    




