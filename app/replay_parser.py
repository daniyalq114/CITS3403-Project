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

from html.parser import HTMLParser

class Player:
    def __init__(self, name="", team=None):
        self.name = name
        self.team = team if team else []

class Turn:
    def __init__(self, number):
        self.number = number
        self.actions = []

class ReplayData:
    def __init__(self):
        self.title = ""
        self.player1 = Player()
        self.player2 = Player()
        self.turns = []
        self.winner = ""
        self.raw_log = []

class ReplayHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.recording_title = False
        self.in_script_tag = False
        self.replay = ReplayData()
        self.log_buffer = []
        self.move_usage = {}
        self.team1 = []
        self.team2 = []
        self.picked_pokemon = {'p1': [], 'p2': []}
        self.elo_data = {'p1': [0, 0, 0], 'p2': [0, 0, 0]}
        self.terastallize = {'p1': False, 'p2': False}

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.recording_title = True
        if tag == "script":
            for name, value in attrs:
                if name == "class" and "battle-log-data" in value:
                    self.in_script_tag = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.recording_title = False
        if tag == "script" and self.in_script_tag:
            self.in_script_tag = False
            self._parse_script_data("\n".join(self.log_buffer))
            self.log_buffer.clear()

    def handle_data(self, data):
        if self.recording_title:
            self.replay.title = data.strip()
        if self.in_script_tag:
            self.log_buffer.append(data)

    def _parse_script_data(self, script_data):
        current_turn = None
        for line in script_data.strip().splitlines():
            self.replay.raw_log.append(line.strip())
            parts = line.split('|')
            
            # Track teams and picks
            if line.startswith('|poke|p1|'):
                pokemon = parts[3].split(',')[0].strip()
                if pokemon not in self.team1:
                    self.team1.append(pokemon)
                    self.replay.player1.team.append(pokemon)
            elif line.startswith('|poke|p2|'):
                pokemon = parts[3].split(',')[0].strip()
                if pokemon not in self.team2:
                    self.team2.append(pokemon)
                    self.replay.player2.team.append(pokemon)
            elif line.startswith('|switch|') or line.startswith('|drag|'):
                side = 'p1' if 'p1a:' in parts[2] else 'p2'
                pokemon = parts[3].split(',')[0].strip()
                if pokemon not in self.picked_pokemon[side]:
                    self.picked_pokemon[side].append(pokemon)

            # Track moves
            elif line.startswith('|move|'):
                pokemon = parts[2].split(':')[1].strip()
                move = parts[3].strip()
                if pokemon not in self.move_usage:
                    self.move_usage[pokemon] = {}
                if move not in self.move_usage[pokemon]:
                    self.move_usage[pokemon][move] = 0
                self.move_usage[pokemon][move] += 1

            # Track winner
            elif line.startswith('|win|'):
                self.replay.winner = parts[2]

            # Player names
            elif line.startswith("|player|p1|"):
                self.replay.player1.name = parts[3]
            elif line.startswith("|player|p2|"):
                self.replay.player2.name = parts[3]

            # Turns and actions
            elif line.startswith("|turn|"):
                turn_num = int(parts[2])
                current_turn = Turn(turn_num)
                self.replay.turns.append(current_turn)
            elif line.startswith("|") and current_turn:
                current_turn.actions.append(line)

    def get_formatted_data(self, username):
        """Return formatted game data for the given username"""
        is_player1 = self.replay.player1.name.lower() == username.lower()
        
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

def parse_replay_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    parser = ReplayHTMLParser()
    parser.feed(content)
    return parser.replay
