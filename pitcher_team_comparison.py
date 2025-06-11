import os
import psycopg2
from dotenv import load_dotenv
from supabase import create_client, Client
from decimal import Decimal

load_dotenv()

USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

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
            SELECT game_id, game_date, away_team, home_team, 
                   away_pitcher.name AS away_pitcher, away_pitcher.era_per_inning, away_pitcher.whip AS away_whip, away_pitcher.k_per_inning AS away_k_per_inning, 
                   home_pitcher.name AS home_pitcher, home_pitcher.era_per_inning, home_pitcher.whip AS home_whip, home_pitcher.k_per_inning AS home_k_per_inning,
                   away_team_stats.runs_per_inning AS away_runs_per_inning, away_team_stats.hits_walks_per_inning AS away_hits_walks_per_inning, away_team_stats.strikeouts_per_inning AS away_strikeouts_per_inning,
                     home_team_stats.runs_per_inning AS home_runs_per_inning, home_team_stats.hits_walks_per_inning AS home_hits_walks_per_inning, home_team_stats.strikeouts_per_inning AS home_strikeouts_per_inning
            FROM games
            LEFT JOIN pitchers AS away_pitcher ON games.away_pitcher_id = away_pitcher.pitcher_id
            LEFT JOIN pitchers AS home_pitcher ON games.home_pitcher_id = home_pitcher.pitcher_id
            JOIN mlb_team_stats AS away_team_stats ON games.away_team = away_team_stats.team_name
            JOIN mlb_team_stats AS home_team_stats ON games.home_team = home_team_stats.team_name
        """)
    games = cursor.fetchall()
    print(games)
    for game in games:
        game_id, game_date, away_team, home_team, away_pitcher, away_era, away_whip, away_k, home_pitcher, home_era, home_whip, home_k, away_runs_per_inning, away_hits_walks_per_inning, away_strikeouts_per_inning, home_runs_per_inning, home_hits_walks_per_inning, home_strikeouts_per_inning = game
        # print(f"Game ID: {game_id}, Date: {game_date}, Away Team: {away_team}, Home Team: {home_team}, Away Pitcher: {away_pitcher}, Home Pitcher: {home_pitcher}")
        # print(f"Away Pitcher ERA: {away_era}, WHIP: {away_whip}, K/INN: {away_k}")
        # print(f"Home Pitcher ERA: {home_era}, WHIP: {home_whip}, K/INN: {home_k}")
        # print(f"Away Team Runs/INN: {away_runs_per_inning}, Hits/Walks/INN: {away_hits_walks_per_inning}, Strikeouts/INN: {away_strikeouts_per_inning}")
        # print(f"Home Team Runs/INN: {home_runs_per_inning}, Hits/Walks/INN: {home_hits_walks_per_inning}, Strikeouts/INN: {home_strikeouts_per_inning}")

        away_team_score = ((away_runs_per_inning * -2) + (away_hits_walks_per_inning * -1) + (away_strikeouts_per_inning)) * 6
        home_team_score = ((home_runs_per_inning * -2) + (home_hits_walks_per_inning * -1) + (home_strikeouts_per_inning)) * 6

        if away_pitcher is not None:
            # away_pitcher_calc_era = (away_era + home_runs_per_inning) / 2
            # away_pitcher_calc_whip = (away_whip + home_hits_walks_per_inning) / 2
            # away_pitcher_calc_k_per_inning = (away_k + home_strikeouts_per_inning) / 2

            away_pitcher_calc_era = (away_era * Decimal(str(0.35)) + home_runs_per_inning * Decimal(str(0.65)))
            away_pitcher_calc_whip = (away_whip * Decimal(str(0.35)) + home_hits_walks_per_inning * Decimal(str(0.65)))
            away_pitcher_calc_k_per_inning = (away_k * Decimal(str(0.35)) + home_strikeouts_per_inning * Decimal(str(0.65)))

            away_pitcher_score = ((away_pitcher_calc_era * -2) + (away_pitcher_calc_whip * -1) + (away_pitcher_calc_k_per_inning)) * 6
        else:
            away_pitcher_score = home_team_score

        if home_pitcher is not None:
            # home_pitcher_calc_era = (home_era + away_runs_per_inning) / 2
            # home_pitcher_calc_whip = (home_whip + away_hits_walks_per_inning) / 2
            # home_pitcher_calc_k_per_inning = (home_k + away_strikeouts_per_inning) / 2

            home_pitcher_calc_era = (home_era * Decimal(str(0.35)) + away_runs_per_inning * Decimal(str(0.65)))
            home_pitcher_calc_whip = (home_whip * Decimal(str(0.35)) + away_hits_walks_per_inning * Decimal(str(0.65)))
            home_pitcher_calc_k_per_inning = (home_k * Decimal(str(0.35)) + away_strikeouts_per_inning * Decimal(str(0.65)))

            home_pitcher_score = ((home_pitcher_calc_era * -2) + (home_pitcher_calc_whip * -1) + (home_pitcher_calc_k_per_inning)) * 6
        else:
            home_pitcher_score = away_team_score


        print(f"{away_pitcher} vs {home_team} Score: {round(away_pitcher_score, 2)}")
        print(f"{home_pitcher} vs {away_team} Score: {round(home_pitcher_score, 2)}")

    connection.commit()
    # Close the cursor and connection
    cursor.close()
    connection.close()
    print("Connection closed.")

except Exception as e:
    print(f"Failed to connect: {e}")