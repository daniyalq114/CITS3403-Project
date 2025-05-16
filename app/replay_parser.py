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
from app.models import *
from dataclasses import dataclass, field
from app.sprite_cache import sprite_cache
@dataclass
class Pokemon:
    name: str = ""
    moves: dict = field(default_factory=dict)
    wins: int = 0
    defeated:bool = False

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
        self.parsePlayerData() # we are now at "|start|..."

        for line in self.log:
            line = line.split('|')
            if len(line) < 2: continue
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
                        t[nickname].name = pokemon_name # the actual name of the pokemon
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
                    # set this pokemon's defeated field to True
                    self.players[active_p_num[:2]].team[nickname].defeated = True
                    enemy_index = int(active_p_num[1]) % 2 # p1a -> 1, p2a -> 0
                    attacker_pokemon = self.last_attacker[enemy_index] 
                    # increment the number of wins for the attacking pokemon
                    self.players[f"p{enemy_index + 1}"].team[attacker_pokemon].wins += 1
                    

        if line[1] != "win":
            # We've run out of lines early. Dodgy log
            raise Exception("Replay terminates before win state is met. Please supply a valid replay.")
        else:
            self.winner = line[2]
            self.handleGameEnd()
    
    def parsePlayerData(self):
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
                        self.players[line[2]].team[pokemon_name].name = pokemon_name

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

def save_parsed_log_to_db(parsed_log, db, username):
    players = parsed_log.players
    match = Match(
        user_id=username, # showdown name FK - links match to user
        # to store half as much data (when the opposing player submits their matches), have enemyname be another FK
        enemyname=players['p2'].name,
        teams=[],  # Teams will be added later
        winner=parsed_log.winner, 
        replay_url=parsed_log.replay_url
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
        for nickname, pokemon_data in players[team_key].team.items():
            team_pokemon = TeamPokemon(
                team_id=team.id,
                nickname=nickname, 
                pokemon_name=pokemon_data.name,
                ispick=True if nickname in players[team_key].picks else False,
                wins=pokemon_data.wins,
                defeated=pokemon_data.defeated
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
        if len(player.elo) == 2: # don't add elo to db if game is not competitive
            if player_key == "p1":
                match.p1_initial_elo = player.elo[0]
                match.p1_final_elo = player.elo[1]
            elif player_key == "p2":
                match.p2_initial_elo = player.elo[0]
                match.p2_final_elo = player.elo[1]
    db.session.commit()

def fetch_usr_matches_from_db(username):
    """Returns a list of dictionaries representing matches for a given user."""
    user = User.query.filter_by(username=username).first()
    if not user: 
        raise Exception("User doesn't exist!")

    match_list = []
    user_matches = sorted(user.matches, key=lambda m: m.id)
    for match_num, db_match in enumerate(user_matches, start=1):
        match_entry = {}
        match_entry["match_num"] = match_num
        match_entry["id"] = db_match.id
        match_entry["win"] = db_match.winner
        match_entry["enemyname"] = db_match.enemyname
        match_entry["replay_url"] = db_match.replay_url

        # Get user and enemy teams
        usr_team, enemy_team = db_match.teams

        # Get sprite URLs for all Pokémon, preserving nicknames
        match_entry["oppteam"] = [
            (sprite_cache.get_sprite_url(p.pokemon_name), p.nickname if p.nickname else p.pokemon_name)
            for p in enemy_team.pokemons
        ]
        match_entry["usr_picks"] = [
            (sprite_cache.get_sprite_url(p.pokemon_name), p.nickname if p.nickname else p.pokemon_name)
            for p in usr_team.pokemons if p.ispick
        ]
        match_entry["enemy_picks"] = [
            (sprite_cache.get_sprite_url(p.pokemon_name), p.nickname if p.nickname else p.pokemon_name)
            for p in enemy_team.pokemons if p.ispick
        ]

        # ELO data
        match_entry["elo"] = [
            db_match.p1_initial_elo, 
            db_match.p1_final_elo, 
            db_match.p2_initial_elo
        ]

        # Additional fields
        match_entry["terastallize"] = [False, False]  # Placeholder
        match_entry["OTS"] = False  # Placeholder

        match_list.append(match_entry)

    return match_list

def fetch_pokemon_data_for_usr(username, active_match_id):
    """
    Fetches information required for tables two and three. Including the 
    number of pokemon defeated by that pokemon, the number of matches won/lost, 
    and the number of times that pokemon used a particular move.
    -username: the username whos matches to search
    -active_match_id: the match whos pokemon you want information on 
    """
    target_match = Match.query.filter_by(id=active_match_id).first()
    if not target_match:
        raise Exception("Active match doesn't exist!")
    target_team = [t for t in target_match.teams if t.is_user_team][0]
    target_pokemon = {p.pokemon_name for p in target_team.pokemons}

    user = User.query.filter_by(username=username).first()
    if not user: 
        raise Exception("User doesn't exist!")
    
    poke_dict = dict()
    for db_match in user.matches:
        won = int(db_match.winner != db_match.enemyname)
        usr_team = [t for t in db_match.teams if t.is_user_team][0] 
        for pokemon in usr_team.pokemons:
            # we only care about pokemon in the active match
            if pokemon.pokemon_name not in target_pokemon: continue
            # construct dict if pokemon not already in poke_dict
            if pokemon.pokemon_name not in poke_dict:
                poke_dict[pokemon.pokemon_name] = {"moves":{}, "wins":0, "losses":0, "matches_won":0}
            # construct or increment values for the active pokemon
            cur_poke = poke_dict[pokemon.pokemon_name]
            for mu in pokemon.move_usages: # add moves or increment move counts on existing moves
                cur_poke["moves"][mu.move_name] = cur_poke["moves"].get(mu.move_name, 0) + mu.times_used
            cur_poke["wins"] += pokemon.wins
            cur_poke["losses"] += int(pokemon.defeated)
            cur_poke["matches_won"] += won
            cur_poke["truename"] =  pokemon.pokemon_name
    return poke_dict

def unpack_display_replay(replay):
    """For debugging - prints the information of a parsed log """
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
