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
# from app.models import *
from dataclasses import dataclass, field

@dataclass
class Pokemon:
    name: str = ""
    moves: dict = field(default_factory=dict)
    wins: int = 0

@dataclass
class Player:
    name: str = ""
    # stores a dictionary containing a player's pokemon
    # We use the pokemon's nicknames (if they have them) as keys
    team: dict = field(default_factory=dict)
    # stores a list of pokemon names that are actually used
    picks: set = field(default_factory=set) 
    elo: list = field(default_factory=list)

class ReplayLogParser:
    def __init__(self, URL):
        self.players = {"p1": Player(), "p2": Player()}  
        self.winner = None # to be updated after win condition is satisfied
        # this stuff is handled once main loop terminates
        self.elo_data = {'p1': [0, 0], 'p2': [0, 0]}
        # stores the most recent attacker for each team
        # used to track which pokemon are responsible for fainting others
        self.last_attacker = ["", ""] 
        #TODO
        # handle terastallize
        self.terastallize = {'p1': False, 'p2': False}
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
        # stores active pokemon for each player, using their nicknames as keys

        # Initialize players before the game starts
        self.getPlayerData() # we are now at "|start|..."

        for line in self.log:
            line = line.split('|')
            if line[1] == 'win': break
            match line[1]: 
                case 'switch':
                    # For some god forsaken reason, the log refers to the pokemon 
                    # almost exclusively by their nickname. Despite this, the initial list
                    # of pokemon fails to include their nicknames. Terrific. 
                    # If you're curious, just add ".log" to the end of a replay, and look at all 
                    # the "poke" fields

                    # Converts "|switch|p1b: Calyrex|..." into [p1b, Calyrex]
                    active_p_num, nickname = line[2].split(": ")
                    pokemon_name = line[3].split(',')[0]
                    t = self.players[active_p_num[:2]].team # e.g. players["p1"].team
                    if nickname not in t and nickname != pokemon_name:
                        # Replace the key with the nickname instead
                        # The pokemon is already added to team in `getPlayerData`, so never fails
                        if pokemon_name not in t:
                            # we have an interesting case like Urshifu-Single-Strike vs Urshifu-Rapid-Strike
                            # or like deoxys
                            for p in t.keys():
                                if p.endswith("-*") and pokemon_name.startswith(p[:-2]): 
                                    pokemon_name = p
                                    break
                                    
                        temp = Pokemon()
                        temp.name = pokemon_name
                        temp.moves = t[pokemon_name].moves.copy()
                        temp.wins = t[pokemon_name].wins
                        t.pop(pokemon_name)
                        t[nickname] = temp
                    # adds the pokemon to the 'picks' set of e.g. players['p1']
                    self.players[active_p_num[:2]].picks.add(nickname)

                case 'move':
                    active_p_num, nickname = line[2].split(": ")
                    # active_p_num looks like `p1a`, p_num looks like "1"
                    p_num = int(active_p_num[1])
                    # updates the most recent attacking pokemon for the team
                    self.last_attacker[p_num - 1] = nickname # index starts at 0
                    move_name = line[3]
                    pokemon = self.players[f"p{p_num}"].team[nickname]
                    pokemon.moves[move_name] = pokemon.moves.get(move_name, 0) + 1

                case 'faint':
                    active_p_num, nickname = line[2].split(": ")
                    enemy_index = int(active_p_num[1]) % 2 # p1a -> 1, p2a -> 0
                    attacker_pokemon = self.last_attacker[enemy_index] 
                    self.players[f"p{enemy_index + 1}"].team[attacker_pokemon].wins += 1
                    

        if line[1] != "win":
            # We've run out of lines early. Dodgy log
            raise Exception("Replay terminates before win state is met. Please supply a valid replay.")
        else:
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
                    if pokemon_name:  # Ensure the name is not empty or None - no funny business
                        self.players[line[2]].team.setdefault(pokemon_name, Pokemon())

    def handleGameEnd(self):
        """Handles log content after the 'win' statement is encountered.
        Parses the log and locates the current and new ELO for each player, 
        and updates relevant `self.player.elo` field
        """
        i = 1
        for line in self.log:
            if line.startswith("|raw"): # so we don't look for " rating " a million times
                if " rating: " in line: # we have an elo updating line
                    line = line.split('|')
                    # finding and setting the current elo
                    temp = line[2].find(" rating: ") + 9 # index of the current elo
                    cur_elo_end_index = line[2].find(" ", temp)
                    cur_elo = line[2][temp:cur_elo_end_index]

                    temp = line[2].find("<strong>") + 8
                    new_elo_end_index = line[2].find("</strong>", temp)
                    new_elo = line[2][temp:new_elo_end_index]
                    self.players[f"p{i}"].elo = [cur_elo, new_elo]
                    i+=1

def save_parsed_log_to_db(parsed_log, db, s_username):
    players = parsed_log.players
    match = Match(
        user_id=s_username, # showdown name FK - links match to user
        # to store half as much data (when the opposing player submits their matches), have enemyname be another FK
        enemyname=players['p2'].name,
        teams=[]  # Teams will be added later
    )
    db.session.add(match)
    db.session.commit()

    # Add teams for the match
    for team_key in parsed_log.players.keys():
        team = Team(
            match_id=match.id,
            is_user_team=(team_key == 'p1')
        )
        db.session.add(team)
        db.session.commit()

        # Add Pokémon to the team
        for pokemon_name, pokemon_data in players[team_key].team.items():
            team_pokemon = TeamPokemon(
                team_id=team.id,
                pokemon_name=pokemon_name
            )
            db.session.add(team_pokemon)
            db.session.commit()

            # Add moves for the Pokémon
            for move_name, times_used in pokemon_data.moves.items():
                move_usage = MoveUsage(
                    team_pokemon_id=team_pokemon.id,
                    move_name=move_name,
                    times_used=times_used
                )
                db.session.add(move_usage)

    db.session.commit()

    # Update match winner and ELO data
    match.winner = parsed_log.winner
    for player_key, player in parsed_log.players.items():
        if player_key == "p1":
            match.p1_initial_elo = player.elo[0]
            match.p1_final_elo = player.elo[1]
        elif player_key == "p2":
            match.p2_initial_elo = player.elo[0]
            match.p2_final_elo = player.elo[1]
    db.session.commit()


# die 
# log = "https://replay.pokemonshowdown.com/oumonotype-82345404"
# temp = ReplayLogParser(log)
replay = ReplayLogParser('https://replay.pokemonshowdown.com/gen9vgc2025regi-2359297693-to7lmydgf9xotduir2oo3fxsls88fn5pw')

print("Player 1:", replay.players['p1'].name)
print("ELO:", replay.players['p1'].elo)
# prints each pokemon for player1's team, including moves, and defeated pokemon
print("Player 1 picks:", list(map(lambda x: (x, replay.players['p1'].team[x]), replay.players['p1'].picks)))
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