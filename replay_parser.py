"""
Replay Parser Module for Pokémon Showdown HTML Replays

Usage Example:

    from replay_parser import parse_replay_file

    replay = parse_replay_file("OUMonotype-2014-01-29-kdarewolf-onox.html")

    print("Title:", replay.title)
    print("Player 1:", replay.player1.name, "| Team:", replay.player1.team)
    print("Player 2:", replay.player2.name, "| Team:", replay.player2.team)
    print("Winner:", replay.winner)
    print("First 3 turns:")
    for turn in replay.turns[:3]:
        print(f"Turn {turn.number}:")
        for action in turn.actions:
            print("  ", action)
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
    team: dict = field(default_factory=dict)

class ReplayLogParser:
    def __init__(self, URL):
        self.players = {"p1": Player(), "p2": Player()}  
        self.winner = None # to be updated after win condition is satisfied
        #TODO
        # mostly to be returned to intermediary database-communicating class
        self.replay_url = URL
        # this stuff is handled once main loop terminates
        self.elo_data = {'p1': [0, 0, 0], 'p2': [0, 0, 0]}
        self.terastallize = {'p1': False, 'p2': False}

        response = requests.get(f"{URL}.log")
        response.raise_for_status()
        # perhaps stupid. Sorry.
        log = (line.decode('utf-8') for line in response.iter_lines()) 
        self.parse_loop(log)
    
    def parse_loop(self, log):
        # log = (line.decode('utf-8') for line in log)  # Decode all lines at once
        active_pokemon = [None, None]  # p1, p2

        # Initialize players before the game starts
        self.getPlayerData(log)

        line = next(log, None)
        if line:
            line = line.strip('|').split('|')  # First 'turn' has just been encountered

        # Main loop
        while line and line[0] != 'win':
            match line[0]: # logic for each case could probably move into different funcs
                case 'switch': 
                    player = line[1][1]  # Extract player number (e.g., 'p1' -> '1')
                    pokemon_name = line[2].split(',')[0].strip()  # Extract and clean Pokémon name
                    if pokemon_name:  # Ensure the name is valid
                        self.players[f'p{player}'].team.setdefault(pokemon_name, Pokemon()).active = True
                        active_pokemon[int(player) - 1] = pokemon_name  # Update active Pokémon

                case 'move':
                    player = line[1][1]
                    pokemon_name = active_pokemon[int(player) - 1]
                    if pokemon_name:  # Ensure the active Pokémon is valid
                        move_name = line[2]
                        pokemon = self.players[f'p{player}'].team.setdefault(pokemon_name, Pokemon())
                        pokemon.moves[move_name] = pokemon.moves.get(move_name, 0) + 1

                case 'faint':
                    fainted_player = line[1][1]
                    fainted_pokemon = line[1][line[1].find(": "):] #deals with formatting
                    if fainted_pokemon:
                        attacker_player = 1 if fainted_player == '2' else 2
                        attacker_pokemon = active_pokemon[attacker_player - 1]
                        if attacker_pokemon:  # Ensure the attacker Pokémon is valid
                            self.players[f'p{attacker_player}'].team[attacker_pokemon].wins += 1
            # Read the next line
            line = next(log, None)
            if line:
                line = line.strip('|').split('|')
    
    def getPlayerData(self, log):
        """Retrieves initial pokemon data from `log`"""
        line = next(log).strip('|').split('|')
        while line[0] != 'start':
            if line[0] == 'player':
                self.players[line[1]].name = line[2]

            elif line[0] == 'poke':
                pokemon_name = line[2].split(',')[0].strip()  # Extract and clean Pokémon name
                if pokemon_name:  # Ensure the name is not empty or None
                    self.players[line[1]].team.setdefault(pokemon_name, Pokemon())

            line = next(log).strip('|').split('|')
    
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

replay = ReplayLogParser('https://replay.pokemonshowdown.com/oumonotype-82345404')
# import parser in other python file responsible for 
# writing to database
print("Player 1:", replay.players['p1'].name)
for pokemon in replay.players['p1'].team:
    print(f"{pokemon}, {replay.players['p1'].team[pokemon]}")
print()
print("Player 2:", replay.players['p2'].name)
for pokemon in replay.players['p2'].team:
    print(f"{pokemon}, {replay.players['p2'].team[pokemon]}")
print()
print("Winner:", replay.winner)