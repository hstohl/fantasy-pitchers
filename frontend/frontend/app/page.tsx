"use client";

import { useEffect, useState } from "react";

type Pitcher = {
  name: string;
  team: string;
  opponent: string;
  date: string;
  score: number;
  era: number;
  whip: number;
  strikeouts: number;
};

const mlbTeams = [
  "Arizona Diamondbacks",
  "Atlanta Braves",
  "Athletics",
  "Baltimore Orioles",
  "Boston Red Sox",
  "Cincinnati Reds",
  "Chicago Cubs",
  "Chicago White Sox",
  "Cleveland Guardians",
  "Colorado Rockies",
  "Detroit Tigers",
  "Houston Astros",
  "Kansas City Royals",
  "Los Angeles Angels",
  "Los Angeles Dodgers",
  "Miami Marlins",
  "Milwaukee Brewers",
  "Minnesota Twins",
  "New York Mets",
  "New York Yankees",
  "Philadelphia Phillies",
  "Pittsburgh Pirates",
  "San Diego Padres",
  "San Francisco Giants",
  "Seattle Mariners",
  "St. Louis Cardinals",
  "Tampa Bay Rays",
  "Texas Rangers",
  "Toronto Blue Jays",
  "Washington Nationals",
];

export default function Home() {
  const [teamFilter, setTeamFilter] = useState("");
  const [opponentFilter, setOpponentFilter] = useState("");
  const [dateFilter, setDateFilter] = useState("");
  const [pitchers, setPitchers] = useState<Pitcher[]>([]);
  const [selectedPitcher, setSelectedPitcher] = useState<Pitcher | null>(null);
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", isDarkMode);
  }, [isDarkMode]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (teamFilter) params.append("team", teamFilter);
    if (opponentFilter) params.append("opponent", opponentFilter);
    if (dateFilter) params.append("date", dateFilter);

    fetch(`/api/pitchers?${params.toString()}`)
      .then((res) => res.json())
      .then((data) => setPitchers(data));
  }, [teamFilter, opponentFilter, dateFilter]);

  return (
    <main className="min-h-screen bg-gray-100 dark:bg-gray-900 p-6 transition-colors duration-300">
      <div className="max-w-4xl mx-auto bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 shadow-xl rounded-xl p-6 relative">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-center w-full">
            Pitcher Projections
          </h1>
          <button
            onClick={() => setIsDarkMode(!isDarkMode)}
            className="absolute right-4 top-4 text-xl hover:scale-110 transition-transform"
            title="Toggle Dark Mode"
          >
            {isDarkMode ? "☀️" : "🌙"}
          </button>
        </div>

        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <select
            className="border px-3 py-2 rounded w-full md:w-1/2 dark:bg-gray-700 dark:border-gray-600"
            value={teamFilter}
            onChange={(e) => setTeamFilter(e.target.value)}
          >
            <option value="">All Teams</option>
            {mlbTeams.map((team) => (
              <option key={team} value={team}>
                {team}
              </option>
            ))}
          </select>

          <select
            className="border px-3 py-2 rounded w-full md:w-1/2 dark:bg-gray-700 dark:border-gray-600"
            value={opponentFilter}
            onChange={(e) => setOpponentFilter(e.target.value)}
          >
            <option value="">All Opponents</option>
            {mlbTeams.map((team) => (
              <option key={team} value={team}>
                {team}
              </option>
            ))}
          </select>

          <input
            type="date"
            className="border px-3 py-2 rounded w-full md:w-1/2 dark:bg-gray-700 dark:border-gray-600"
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
          />
        </div>

        <table className="w-full table-auto border-collapse">
          <thead>
            <tr className="bg-gray-200 dark:bg-gray-700 text-left">
              <th className="p-2">Pitcher</th>
              <th className="p-2">Team</th>
              <th className="p-2">Opponent</th>
              <th className="p-2">Date</th>
              <th className="p-2">Projected Score</th>
            </tr>
          </thead>
          <tbody>
            {pitchers.map((p, i) => (
              <tr
                key={i}
                onClick={() => setSelectedPitcher(p)}
                className="border-t cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                <td className="p-2">{p.name}</td>
                <td className="p-2">{p.team}</td>
                <td className="p-2">{p.opponent}</td>
                <td className="p-2">{p.date}</td>
                <td className="p-2">{p.score}</td>
              </tr>
            ))}
            {pitchers.length === 0 && (
              <tr>
                <td
                  colSpan={5}
                  className="text-center p-4 text-gray-500 dark:text-gray-400"
                >
                  No pitchers found.
                </td>
              </tr>
            )}
          </tbody>
        </table>

        {/* Modal */}
        {selectedPitcher && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 p-6 rounded-xl shadow-lg w-full max-w-md relative">
              <button
                onClick={() => setSelectedPitcher(null)}
                className="absolute top-3 right-4 text-xl font-bold hover:text-gray-500"
              >
                &times;
              </button>
              <h2 className="text-2xl font-semibold mb-4">
                {selectedPitcher.name} - {selectedPitcher.team}
              </h2>
              <ul className="space-y-2">
                <li>
                  <strong>Opponent:</strong> {selectedPitcher.opponent}
                </li>
                <li>
                  <strong>Date:</strong> {selectedPitcher.date}
                </li>
                <li>
                  <strong>Projected Score:</strong> {selectedPitcher.score}
                </li>
                <li>
                  <strong>ERA:</strong> {selectedPitcher.era}
                </li>
                <li>
                  <strong>WHIP:</strong> {selectedPitcher.whip}
                </li>
                <li>
                  <strong>Strikeouts:</strong> {selectedPitcher.strikeouts}
                </li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
