# CITS3403-Project


| UWA ID   | Name                  | GitHub Username |
|----------|-----------------------|-----------------|
| 23976415 | Daniyal Qureshi       | daniyalq114     |
| 23904324 | Adam Ahmadavi         | aradavi63       |
| 23360799 | Sam Jackson           | samjjacko       |
| 21480994 | Cam Luketina-Clarke   | Drummonddo      |



Bootstrap: https://getbootstrap.com/docs/5.0/components/dropdowns/

https://themewagon.com/themes/free-bootstrap-5-admin-dashboard-template-darkpan/

## LugiAnalytics - a Pokémon Battle Analysis Tool
LugiAnalytics is a web-based tool designed specifically for competitive Pokémon players. The site allows users to:

Input their Showdown username, their team (via a Pokepaste link), and links to battle replays.
Automatically extract key data from battle replays—including win/loss results, opponent team details, ELO changes, move usage, and overall team performance.
Visualise performance metrics using interactive charts and summaries, helping players review their match history and optimize team strategies.

### Features
**User Input:**
Enter your Showdown username.
Submit your team via a Pokepaste link.
Provide battle replay links for analysis.

**Data Extraction:**
An HTML parser processes the replay data to extract game results and performance metrics.

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
flask db init # initialise database
flask db migrate # set up the database to follow schema in models.py
flask db upgrade # apply the migration to the database
```
8. Run LugiAnalytics
`pip install -r requirements.txt`

7. Set the Flask application environment variable:

    | Platform | Shell      | Command                     |
    | -------- | ---------- | --------------------------- |
    | POSIX    | bash/zsh   | `export FLASK_APP=app.py`   |
    | Windows  | Powershell | `$env:FLASK_APP = "app.py"` |

8. Set the Flask secret key (replace 'your-very-secret-key' with a real random string when deploying):

    | Platform | Shell      | Command                                    |
    | -------- | ---------- | ------------------------------------------ |
    | POSIX    | bash/zsh   | `export SECRET_KEY='your-very-secret-key'` |
    | Windows  | Powershell | `$env:SECRET_KEY = "your-very-secret-key"` |

9. Creates /instance/app.db and applies migrations:
`flask db upgrade`

10. NOT IMPLEMENTED (Optional) Add test users and matches: 
`python seed.py`

11. Run LugiAnalytics
`flask run`

12. Open the returned url, e.g. for `* Running on http://127.0.0.1:5000` open `http://127.0.0.1:5000` in your browser. 

When you're done, exit the virtual environment with `deactivate`