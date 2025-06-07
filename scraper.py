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

response = requests.get(url)
if response.status_code == 200:
    everything_json = response.json()
    print("Supposedly successfully retrieved the page.")
else:
    print("Failed to retrieve the page:", response.status_code)

results = []

for date_entry in everything_json['dates']:
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

                game_info[f'{side}_pitcher'] = {
                    'name': pitcher['fullName'],
                    'era': pitching_stats.get('era'),
                    'whip': pitching_stats.get('whip'),
                    'k_per_9': pitching_stats.get('strikeoutsPer9Inn')
                }

        results.append(game_info)

# Print the results
for game in results:
    print(f"Date: {game['date']}")
    print(f"{game['away_team']} (P: {game['away_pitcher']}) vs {game['home_team']} (P: {game['home_pitcher']})")
    print()