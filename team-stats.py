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


url2 = "https://bdfed.stitch.mlbinfra.com/bdfed/stats/team?&env=prod&sportId=1&gameType=R&group=hitting&order=desc&sortStat=homeRuns&stats=season&season=2025&limit=30&offset=0"

team_stats_response = requests.get(url2)
if team_stats_response.status_code == 200:
    team_stats_json = team_stats_response.json()
    print("Supposedly successfully retrieved the page for team stats.")
else:
    print("Failed to retrieve the page:", team_stats_response.status_code)

team_stats_results = []
for team in team_stats_json['stats']:
    gamesPlayed = team.get('gamesPlayed')
    runs_per_inning = team.get('runs') / (gamesPlayed * 9) if gamesPlayed else 0
    hits_walks_per_inning = (team.get('hits') + team.get('baseOnBalls')) / (gamesPlayed * 9) if gamesPlayed else 0
    strikeouts_per_inning = team.get('strikeOuts') / (gamesPlayed * 9) if gamesPlayed else 0
    team_stats_results.append({
        'teamName': team.get('teamName'),
        'runs_per_inning': runs_per_inning,
        'hits_walks_per_inning': hits_walks_per_inning,
        'strikeouts_per_inning': strikeouts_per_inning
    })

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
            DROP TABLE IF EXISTS mlb_team_stats;
            CREATE TABLE mlb_team_stats (
                team_name TEXT PRIMARY KEY,
                runs_per_inning NUMERIC(8, 7),
                hits_walks_per_inning NUMERIC(8, 7),
                strikeouts_per_inning NUMERIC(8, 7)
            );
        """)
    
    for row in team_stats_results:
            cursor.execute("""
                INSERT INTO mlb_team_stats (team_name, runs_per_inning, hits_walks_per_inning, strikeouts_per_inning)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (team_name) DO UPDATE SET
                    runs_per_inning = EXCLUDED.runs_per_inning,
                    hits_walks_per_inning = EXCLUDED.hits_walks_per_inning,
                    strikeouts_per_inning = EXCLUDED.strikeouts_per_inning   
            """, (
                row['teamName'],
                row['runs_per_inning'],
                row['hits_walks_per_inning'],
                row['strikeouts_per_inning']
            ))

    connection.commit()
    # Close the cursor and connection
    cursor.close()
    connection.close()
    print("Connection closed.")

except Exception as e:
    print(f"Failed to connect: {e}")

# Print the results
print(team_stats_results)