from bs4 import BeautifulSoup
import requests
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
from game import Game
import json
import os
import psycopg2
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

date = datetime.now()
start_date = date.strftime("%Y-%m-%d")
date = date + timedelta(days=4)
end_date = date.strftime("%Y-%m-%d")

print(f"Fetching data for dates: {start_date} to {end_date}")

url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&sportId=51&sportId=21&startDate={start_date}&endDate={end_date}&timeZone=America/New_York&gameType=E&&gameType=S&&gameType=R&&gameType=F&&gameType=D&&gameType=L&&gameType=W&&gameType=A&language=en&leagueId=104&&leagueId=103&&leagueId=160&&leagueId=590&&leagueId=&&leagueId=&&leagueId=426&&leagueId=427&&leagueId=428&&leagueId=429&&leagueId=430&&leagueId=431&&leagueId=432&sortBy=gameDate,gameType&hydrate=team,probablePitcher,stats"

print(f"Fetching data from URL: {url}")

matchup_response = requests.get(url)
if matchup_response.status_code == 200:
    matchup_json = matchup_response.json()
    print("Supposedly successfully retrieved the page.")
else:
    print("Failed to retrieve the page:", matchup_response.status_code)

# print(matchup_json)
matchup_results = []

for date_entry in matchup_json['dates']:
    date = date_entry['date']
    for game in date_entry['games']:
        game_info = {
            'date': date,
            'away_team': None,
            'home_team': None,
            'away_pitcher': None,
            'home_pitcher': None,
        }

        for side in ['away', 'home']:
            team = game['teams'][side]['team']['name']
            game_info[f'{side}_team'] = team

            pitcher = game['teams'][side].get('probablePitcher')
            if pitcher:
                # Find the pitching season stats
                pitching_stats = next(
                    (s['stats'] for s in pitcher.get('stats', [])
                     if s['type']['displayName'] == 'statsSingleSeason'
                     and s['group']['displayName'] == 'pitching'),
                    {}
                )
                # innings_pitched = pitching_stats.get('inningsPitched')
                # full_innings, outs = innings_pitched.split('.')
                # innings_pitched = int(full_innings) + (int(outs) / 3 if outs else 0)
                # avg_innings_pitched = innings_pitched / pitching_stats.get('gamesStarted') if pitching_stats.get('gamesStarted') else 0
                # # print("We are here!!", avg_innings_pitched)

                # avg_innings_pitched = float(avg_innings_pitched)

                era = pitching_stats.get('era', 0)
                if '-' not in era:
                    era = float(era)
                else:
                    era = 4.0  # Default ERA if not available
                k_per_9 = pitching_stats.get('strikeoutsPer9Inn', 0)
                if '-' not in k_per_9:
                    k_per_9 = float(k_per_9)
                else:
                    k_per_9 = 8.0 # Default K/9 if not available
                whip = pitching_stats.get('whip', 0)
                if '-' not in whip:
                    whip = float(whip)
                else:
                    whip = 1.3 # Default WHIP if not available
                game_info[f'{side}_pitcher'] = {
                    'name': pitcher['fullName'],
                    'era_per_inning': era / 9 if era else 0,
                    'whip': whip,
                    'k_per_inning': k_per_9 / 9 if k_per_9 else 0,
                }

        matchup_results.append(game_info)

# Print the results
# print(matchup_results)
for game in matchup_results:
    print(f"Date: {game['date']}")
    print(f"{game['away_team']} (P: {game['away_pitcher']}) vs {game['home_team']} (P: {game['home_pitcher']})")
    print()


try:
    connection = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
    )
    print("Connection successful!")
    
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            game_id SERIAL PRIMARY KEY,
            game_date DATE NOT NULL,
            away_team TEXT NOT NULL,
            home_team TEXT NOT NULL,
            away_pitcher_id INT,
            home_pitcher_id INT
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pitchers (
            pitcher_id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            era_per_inning NUMERIC(8, 6),
            whip NUMERIC(8, 6),
            k_per_inning NUMERIC(8, 6)
        );
    """)

    def get_pitcher_id(pitcher):
        if pitcher is None:
            return None

        # Check if pitcher already exists
        cursor.execute("SELECT pitcher_id FROM pitchers WHERE name = %s", (pitcher['name'],))
        result = cursor.fetchone()
        if result:
            return result[0]
        
        # Insert new pitcher
        cursor.execute("""
            INSERT INTO pitchers (name, era_per_inning, whip, k_per_inning)
            VALUES (%s, %s, %s, %s)
            RETURNING pitcher_id;
        """, (
            pitcher['name'],
            pitcher['era_per_inning'],
            pitcher['whip'],
            pitcher['k_per_inning']
        ))
        return cursor.fetchone()[0]


    for game in matchup_results:
        game_date = game["date"]
        away_team = game["away_team"]
        home_team = game["home_team"]
        away_pitcher = game.get("away_pitcher")
        home_pitcher = game.get("home_pitcher")

        away_pitcher_id = get_pitcher_id(away_pitcher)
        home_pitcher_id = get_pitcher_id(home_pitcher)

        # Check if game already exists
        cursor.execute("""
            SELECT game_id, away_pitcher_id, home_pitcher_id FROM games
            WHERE game_date = %s AND away_team = %s AND home_team = %s;
        """, (game_date, away_team, home_team))

        existing_game = cursor.fetchone()

        if existing_game:
            game_id, existing_away_id, existing_home_id = existing_game
            # Update any missing pitcher slots
            if away_pitcher_id and not existing_away_id:
                cursor.execute("""
                    UPDATE games SET away_pitcher_id = %s WHERE game_id = %s;
                """, (away_pitcher_id, game_id))

            if home_pitcher_id and not existing_home_id:
                cursor.execute("""
                    UPDATE games SET home_pitcher_id = %s WHERE game_id = %s;
                """, (home_pitcher_id, game_id))
        else:
            # Insert new game
            cursor.execute("""
                INSERT INTO games (game_date, away_team, home_team, away_pitcher_id, home_pitcher_id)
                VALUES (%s, %s, %s, %s, %s);
            """, (
                game_date, away_team, home_team,
                away_pitcher_id, home_pitcher_id
            ))

    connection.commit()
    # Close the cursor and connection
    cursor.close()
    connection.close()
    print("Connection closed.")

except Exception as e:
    print(f"Failed to connect: {e}")