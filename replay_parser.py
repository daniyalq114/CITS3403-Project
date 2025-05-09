"""
Replay Parser Module for Pokémon Showdown Replays

Usage Example:

    replay = ReplayLogParser('https://replay.pokemonshowdown.com/oumonotype-82345404')

    print("Player 1:", replay.players['p1'].name)
    print("ELO:", replay.players['p1'].elo)
    # prints each pokemon for player1's team, including moves, and defeated pokemon
    print("Player 1 picks:", replay.players['p1'].picks)
    for pokemon in replay.players['p1'].team:
        print(f"{pokemon}, {replay.players['p1'].team[pokemon]}")
    print()

    # same for player 2, 3, {...} , n, etc
    print("Player 2:", replay.players['p2'].name)
    print("ELO:", replay.players['p2'].elo)
    print("Player 2 picks:", replay.players['p2'].picks)
    for pokemon in replay.players['p2'].team:
        print(f"{pokemon}, {replay.players['p2'].team[pokemon]}")
    print()

    # return the winning team
    print("Winner:", replay.winner)

This assumes pokemon will not have empty names or names containing the char '|'.
"""
import requests
from dataclasses import dataclass, field

@dataclass
class Pokemon:
    moves: dict = field(default_factory=dict)
    wins: int = 0

@dataclass
class Player:
    name: str = ""
    # associates moves with the pokemon that performed the move
    team: dict = field(default_factory=dict)
    # stores a list of pokemon names that are actually used
    picks: set = field(default_factory=set) 
    elo: list = field(default_factory=list)

class ReplayLogParser:
    def __init__(self, URL):
        self.players = {"p1": Player(), "p2": Player()}  
        self.winner = None # to be updated after win condition is satisfied
        # this stuff is handled once main loop terminates
        self.elo_data = {'p1': [0, 0, 0], 'p2': [0, 0, 0]}
        self.terastallize = {'p1': False, 'p2': False}

        #TODO
        # mostly to be returned to intermediary database-communicating class
        self.replay_url = URL

        response = requests.get(f"{URL}.log")
        response.raise_for_status()
        
        # constructs an iterator, so we can divide the loop into several 
        # functions that operate over specific areas, without having to keep track
        # of where we're up 
        self.log = (line.decode('utf-8') for line in response.iter_lines()) 

        # Populates instance variables by operating over the log file
        # by dividing states of the game into different helper functions.
        self.parse_loop()

    def parse_loop(self):
        """ Main parsing loop. 
        Counts the number of moves made and pokemon defeated by each pokemon, 
        the names and ELO of each player, and the winner of the match, 
        and stores this data in relevant fields such as `self.players`, 
        `self.winner` etc. 
        """
        # stores active pokemon for each player
        # active_pokemon[0] is player 1's active pokemon
        # updated every time "switch" is encountered
        active_pokemon = [None, None]  

        # Initialize players before the game starts
        self.getPlayerData() # we are now at "|start|..."

        for line in self.log:
            line = line.split('|')
            if line[1] == 'win': break
            # I think the reason it has "p1a", "p2a" is to differentiate between members of a team?
            # need to double check, but i think p1a p1b are two players in the same team
            match line[1]: 
                case 'switch':
                    # this has to be done within each switch statement, as other lines that don't start
                    # with these specific fields do not follow the same format
                    p_num = line[2][1] 
                    pokemon_name = line[3].split(',')[0].strip()  # Extract and clean Pokémon name
                    self.players[f'p{p_num}'].picks.add(pokemon_name)
                    self.players[f'p{p_num}'].team.setdefault(pokemon_name, Pokemon()).active = True
                    active_pokemon[int(p_num) - 1] = pokemon_name  # Update active Pokémon

                case 'move':
                    p_num = line[2][1]
                    pokemon_name = active_pokemon[int(p_num) - 1]
                    move_name = line[3]
                    pokemon = self.players[f'p{p_num}'].team.setdefault(pokemon_name, Pokemon())
                    pokemon.moves[move_name] = pokemon.moves.get(move_name, 0) + 1

                case 'faint':
                    p_num = line[2][1]
                    attacker_player = 1 if p_num == '2' else 2
                    attacker_pokemon = active_pokemon[attacker_player - 1]
                    self.players[f'p{attacker_player}'].team[attacker_pokemon].wins += 1
                    
        if next(self.log).split('|')[1] != 'raw': 
            # we've run out of lines early - no winner...
            raise Exception("Replay terminates before win state is met. Please supply a valid replay.")
        self.winner = line[2]
        self.handleGameEnd()
    
    def getPlayerData(self):
        """Retrieves initial pokemon data from `log`.
        Fetches the username of the players and the team of each player, 
        and initialises `self.players['pn'].name` and `self.players['pn'].team`
        """
        for line in self.log:
            line = line.split('|') 
            match line[1]:
                case 'start':
                    break
                case 'player':
                    # e.g. players['p2'].name = "ash ketchup"
                    self.players[line[2]].name = line[3]
                case 'poke':
                    # ignores irrelevant details about pokemon's name
                    # e.g. "Pikachu, F, shiny" - we only want "Pikachu"
                    pokemon_name = line[3].split(',')[0].strip()  
                    if pokemon_name:  # Ensure the name is not empty or None
                        self.players[line[2]].team.setdefault(pokemon_name, Pokemon())

    def handleGameEnd(self):
        """Handles log content after the 'win' statement is encountered.
        Parses the log and locates the current and new ELO for each player, 
        and updates relevant `self.player.elo` field
        """
        i = 1
        for line in self.log:
            line = line.split('|')
            if line[1] == 'raw': # '|raw| Ladder updating...' is handled by parse loop
                # finding and setting the current elo
                temp = line[2].find(" rating: ") + 9 # index of the current elo
                cur_elo_end_index = line[2].find(" ", temp)
                cur_elo = line[2][temp:cur_elo_end_index]

                temp = line[2].find("<strong>") + 8
                new_elo_end_index = line[2].find("</strong>", temp)
                new_elo = line[2][temp:new_elo_end_index]
                self.players[f"p{i}"].elo = [cur_elo, new_elo]
                i+=1
    
    def get_formatted_data(self, username):
        """Return formatted game data for the given username"""
        is_player1 = self.players['p1'].name.lower() == username.lower()
        
        return {
            "win": self.replay.winner.lower() == username.lower(),
            "enemyusr": {
                "name": self.replay.player2.name if is_player1 else self.replay.player1.name,
                "search_request": ""  # Add actual search request if available
            },
            "replay": {
                "name": self.replay.title,
                "search_request": ""  # Add actual replay URL if available
            },
            "oppteam": self.team2 if is_player1 else self.team1,
            "usrpicks": self.picked_pokemon['p1'] if is_player1 else self.picked_pokemon['p2'],
            "opppicks": self.picked_pokemon['p2'] if is_player1 else self.picked_pokemon['p1'],
            "Terastallize": [
                self.terastallize['p1'] if is_player1 else self.terastallize['p2'],
                self.terastallize['p2'] if is_player1 else self.terastallize['p1']
            ],
            "ELO": self.elo_data['p1'] if is_player1 else self.elo_data['p2'],
            "OTS": True  # Add logic to determine OTS if available
        }