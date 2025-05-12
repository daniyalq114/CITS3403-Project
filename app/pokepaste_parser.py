import requests
import re

class PokePasteParser:
    def __init__(self):
        self.pokemon_data = []

    def parse_pokepaste(self, url):
        """Parse a PokéPaste URL and return formatted Pokemon data"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            content = response.text

            # Regular expression to match Pokemon sections
            pokemon_sections = re.split(r'\n\n+', content.strip())
            
            for section in pokemon_sections:
                if not section.strip():
                    continue
                
                lines = section.strip().split('\n')
                # First line contains Pokemon name
                pokemon_name = lines[0].split('@')[0].strip()
                moves = []
                
                # Look for moves (lines starting with '- ')
                for line in lines:
                    if line.strip().startswith('- '):
                        move = line.strip()[2:].strip()
                        moves.append([move])

                # Create Pokemon entry
                pokemon_entry = {
                    "name": pokemon_name,
                    "moves": moves,
                    "iconurl": ""  # Will be populated later with PokeAPI data
                }
                self.pokemon_data.append(pokemon_entry)

        except Exception as e:
            print(f"Error parsing PokéPaste: {str(e)}")
            return []

        return self.pokemon_data

    def populate_sprites(self):
        """Populate iconurl for each Pokemon using PokeAPI"""
        for pokemon in self.pokemon_data:
            try:
                url = f"https://pokeapi.co/api/v2/pokemon/{pokemon['name'].lower()}/"
                response = requests.get(url)
                if response.status_code == 200:
                    pokemon["iconurl"] = response.json()["sprites"]["front_default"]
                else:
                    pokemon["iconurl"] = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/0.png"
            except:
                pokemon["iconurl"] = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/0.png"