import requests
from functools import lru_cache

class SpriteCache:
    _instance = None
    _cache = {}
    _default_sprite = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/0.png"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpriteCache, cls).__new__(cls)
        return cls._instance

    @lru_cache(maxsize=1000)
    def get_sprite_url(self, pokemon_name: str) -> str:
        """
        Get the sprite URL for a Pokémon, using cache if available.
        Returns the default sprite if the Pokémon can't be found.
        """
        # Check if we already have this Pokémon cached
        if pokemon_name in self._cache:
            return self._cache[pokemon_name]

        try:
            # Clean the name for the API (handle special cases)
            clean_name = pokemon_name.lower()
            print(f"Original name: {pokemon_name}, Cleaned name: {clean_name}")  # Debug log

            # Handle special cases like "Nidoran♀" or "Nidoran♂"
            if "♀" in clean_name:
                clean_name = "nidoran-f"
            elif "♂" in clean_name:
                clean_name = "nidoran-m"

            print(f"Final cleaned name: {clean_name}")  # Debug log

            url = f"https://pokeapi.co/api/v2/pokemon/{clean_name}/"
            print(f"Requesting URL: {url}")  # Debug log
            response = requests.get(url)
            response.raise_for_status()
            jsondata = response.json()
            
            # Get the sprite URL from the response
            if 'sprites' in jsondata and 'front_default' in jsondata['sprites']:
                sprite_url = jsondata['sprites']['front_default']
                if sprite_url:  # Make sure we got a valid URL
                    print(f"Found sprite URL: {sprite_url}")  # Debug log
                    # Cache the result
                    self._cache[pokemon_name] = sprite_url
                    return sprite_url
            
            # If we get here, either sprites or front_default was missing
            print(f"Warning: No sprite found for {pokemon_name} (cleaned as {clean_name})")
            self._cache[pokemon_name] = self._default_sprite
            return self._default_sprite
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching sprite for {pokemon_name}: {str(e)}")
            self._cache[pokemon_name] = self._default_sprite
            return self._default_sprite
        except Exception as e:
            print(f"Unexpected error for {pokemon_name}: {str(e)}")
            self._cache[pokemon_name] = self._default_sprite
            return self._default_sprite

    def get_sprites_for_pokemon_list(self, pokemon_list: list) -> list:
        """
        Get sprite URLs for a list of Pokémon names.
        Returns a list of dictionaries with 'sprite_url' and 'pokemon_name' keys
        """
        return [{'sprite_url': self.get_sprite_url(name), 'pokemon_name': name} for name in pokemon_list]

# Create a global instance
sprite_cache = SpriteCache() 