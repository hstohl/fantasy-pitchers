from bs4 import BeautifulSoup
import requests
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
from game import Game
import json

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
                avg_innings_pitched = float(pitching_stats.get('inningsPitched')) / pitching_stats.get('gamesStarted') if pitching_stats.get('gamesStarted') else 0
                print("We are here!!", avg_innings_pitched)

                avg_innings_pitched = float(avg_innings_pitched)

                game_info[f'{side}_pitcher'] = {
                    'name': pitcher['fullName'],
                    'era_per_start': (float(pitching_stats.get('era')) / 9) * avg_innings_pitched if avg_innings_pitched != 0 else float('inf'),
                    'whis': float(pitching_stats.get('whip')) * avg_innings_pitched if avg_innings_pitched != 0 else float('inf'),
                    'k_per_start': (float(pitching_stats.get('strikeoutsPer9Inn')) / 9) * avg_innings_pitched if avg_innings_pitched != 0 else 0,
                }

        matchup_results.append(game_info)

# Print the results
for game in matchup_results:
    print(f"Date: {game['date']}")
    print(f"{game['away_team']} (P: {game['away_pitcher']}) vs {game['home_team']} (P: {game['home_pitcher']})")
    print()

url2 = "https://bdfed.stitch.mlbinfra.com/bdfed/stats/team?&env=prod&sportId=1&gameType=R&group=hitting&order=desc&sortStat=homeRuns&stats=season&season=2025&limit=30&offset=0"

team_stats_response = requests.get(url2)
if team_stats_response.status_code == 200:
    team_stats_json = team_stats_response.json()
    print("Supposedly successfully retrieved the page for team stats.")
else:
    print("Failed to retrieve the page:", team_stats_response.status_code)

team_stats_results = []
for team in team_stats_json['stats']:
    team_stats_results.append({
        'teamName': team.get('teamName'),
        'gamesPlayed': team.get('gamesPlayed'),
        'runs': team.get('runs'),
        'hits': team.get('hits'),
        'baseOnBalls': team.get('baseOnBalls'),
        'strikeOuts': team.get('strikeOuts')
    })

# Print the results
for team in team_stats_results:
    print(team)