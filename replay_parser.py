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

            # Player names
            if line.startswith("|player|p1|"):
                self.replay.player1.name = line.split("|")[3]
            elif line.startswith("|player|p2|"):
                self.replay.player2.name = line.split("|")[3]

            # Pokémon teams
            elif line.startswith("|poke|p1|"):
                name = line.split("|")[3].split(",")[0].strip()
                self.replay.player1.team.append(name)
            elif line.startswith("|poke|p2|"):
                name = line.split("|")[3].split(",")[0].strip()
                self.replay.player2.team.append(name)

            # Winner
            elif line.startswith("|win|"):
                self.replay.winner = line.split("|")[2]

            # Turns and actions
            elif line.startswith("|turn|"):
                turn_num = int(line.split("|")[2])
                current_turn = Turn(turn_num)
                self.replay.turns.append(current_turn)
            elif line.startswith("|") and current_turn:
                current_turn.actions.append(line)

def parse_replay_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    parser = ReplayHTMLParser()
    parser.feed(content)
    return parser.replay
