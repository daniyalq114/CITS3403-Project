# CITS3403-Project


| UWA ID   | Name                  | GitHub Username |
|----------|-----------------------|-----------------|
| 23976415 | Daniyal Qureshi       | daniyalq114     |
| 23904324 | Adam Ahmadavi         | aradavi63       |
| 23360799 | Sam Jackson           | samjjacko       |
| 21480994 | Cam Luketina-Clarke   | Drummonddo      |

## LugiAnalytics - a Pokémon Battle Analysis Tool
LugiAnalytics is a web-based tool designed specifically for competitive Pokémon players. The site allows users to:

Input their Showdown username, their team (via a Pokepaste link), and links to battle replays.
Automatically extract key data from battle replays—including win/loss results, opponent team details, ELO changes, move usage, and overall team performance.
Visualise performance metrics using interactive charts and summaries, helping players review their match history and optimize team strategies.

### Features
**User Input:**
Enter your Showdown username.
Provide battle replay links for analysis.

**Sharing:**
Share your data with other users.

**Data Extraction:**
A HTML parser processes the replay data to extract game results and performance metrics.

**Visual Analysis:**
Charts and summaries display win/loss ratios, ELO fluctuations, move usage statistics, and more.

**Technologies Used:**
Frontend: HTML, CSS, Bootstrap, JavaScript 
Backend: Flask (for routing and processing)
Database: SQLite (via SQLAlchemy)
APIs and Parsing: Custom HTML parser for battle replay data
Version Control: Git and GitHub for collaborative development

### Running the test site
1. Navigate to the directory you'd like to store LugiAnalytics, for instance:
```shell
cd Desktop/dev/
```
2. Clone the repository:
```shell
git clone https://github.com/daniyalq114/CITS3403-Project.git
```
3. Navigate to the project directory:
```shell
cd CITS3403-Project/
```
4. Construct a virtual environment:
```shell
python3 -m venv lugi-venv
```
5. Activate the environment: 
    | Platform | Shell      | Command                                 |
    |----------|------------|-----------------------------------------|
    | POSIX    | bash/zsh   | `source lugi-venv/bin/activate`         |
    |          | fish       | `source lugi-venv/bin/activate.fish`    |
    |          | csh/tcsh   | `source lugi-venv/bin/activate.csh`     |
    |          | pwsh       | `source lugi-venv/bin/Activate.ps1`     |
    | Windows  | cmd.exe    | `source lugi-venv\Scripts\activate.bat` |
    |          | Powershell | `source lugi-venv\Scripts\Activate.ps1` |

6. Install dependencies
```shell
pip install -r requirements.txt
```
7. Set up the database
```shell
mkdir -p instance # create instance folder if required
flask db init # initialise database
flask db migrate # set up the database to follow schema in models.py
flask db upgrade # apply the migration to the database
```
8. Set the Flask application environment variable:

    | Platform | Shell      | Command                     |
    | -------- | ---------- | --------------------------- |
    | POSIX    | bash/zsh   | `export FLASK_APP=app.py`   |
    | Windows  | Powershell | `$env:FLASK_APP = "app.py"` |

9. Set the Flask secret key (replace 'your-very-secret-key' with a real random string when deploying):

    | Platform | Shell      | Command                                    |
    | -------- | ---------- | ------------------------------------------ |
    | POSIX    | bash/zsh   | `export SECRET_KEY='your-very-secret-key'` |
    | Windows  | Powershell | `$env:SECRET_KEY = "your-very-secret-key"` |

10. Run LugiAnalytics
```shell
flask run
```
11. Open the returned url, e.g. for `* Running on http://127.0.0.1:5000` open `http://127.0.0.1:5000` in your browser. 

When you're done, exit the virtual environment with `deactivate`


## Credits

**AI Assistance**  
Portions of this project were developed with the assistance of AI tools for code suggestions, debugging, and documentation refinement:
- [OpenAI's ChatGPT](https://openai.com/chatgpt)
- [Anthropic's Claude](https://www.anthropic.com/claude)
- [GitHub Copilot](https://github.com/features/copilot)

**Images**  
Pokémon images are sourced from [Bulbapedia Archives](https://archives.bulbagarden.net/wiki/Main_Page).  
© Game Freak / The Pokémon Company. Usage under [Bulbagarden Archives License](https://bulbapedia.bulbagarden.net/wiki/Bulbapedia:Copyrights).

**Libraries and Tools**  
- [Google Material Design Icons (MDI)](https://fonts.google.com/icons) – [License](https://github.com/google/material-design-icons/blob/master/LICENSE)
- [Google Fonts](https://fonts.google.com/) – [License](https://fonts.google.com/attribution)
- [Google Charts JS](https://developers.google.com/chart) – [License](https://github.com/GoogleWebComponents/google-chart/blob/main/LICENSE)
- [GLSL Canvas JS](https://github.com/patriciogonzalezvivo/glslCanvas) – [License](https://github.com/patriciogonzalezvivo/glslCanvas/blob/master/LICENSE)
- [Bootstrap CSS & JS](https://getbootstrap.com/) – [License](https://github.com/twbs/bootstrap/blob/main/LICENSE)
