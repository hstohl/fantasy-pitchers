class Game:
    def __init__(self, date, team1, team2, pitcher1, stats_link1, pitcher2, stats_link2):
        self.date = date
        self.team1 = team1
        self.team2 = team2
        self.pitcher1 = pitcher1
        self.pitcher1_stats = stats_link1
        self.pitcher2 = pitcher2
        self.pitcher2_stats = stats_link2

    def display(self):
        print(f"{self.team1} vs {self.team2} on {self.date}")
        print(f"Pitchers: {self.pitcher1} vs {self.pitcher2}")
        print(f"Pitcher stats links: {self.pitcher1_stats}, {self.pitcher2_stats}")