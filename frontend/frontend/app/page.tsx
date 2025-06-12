"use client";

import { useState } from "react";

const mockPitchers = [
  {
    name: "Jacob deGrom",
    team: "Rangers",
    opponent: "Yankees",
    date: "2025-06-12",
    score: 2.3,
  },
  {
    name: "Shohei Ohtani",
    team: "Dodgers",
    opponent: "Giants",
    date: "2025-06-13",
    score: 1.9,
  },
  {
    name: "Spencer Strider",
    team: "Braves",
    opponent: "Mets",
    date: "2025-06-12",
    score: 3.1,
  },
  {
    name: "Gerrit Cole",
    team: "Yankees",
    opponent: "Rangers",
    date: "2025-06-12",
    score: 2.7,
  },
];

export default function Home() {
  const [teamFilter, setTeamFilter] = useState("");
  const [dateFilter, setDateFilter] = useState("");

  const filtered = mockPitchers.filter(
    (p) =>
      (!teamFilter ||
        p.team.toLowerCase().includes(teamFilter.toLowerCase())) &&
      (!dateFilter || p.date === dateFilter)
  );

  return (
    <main className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-4xl mx-auto bg-white shadow-xl rounded-xl p-6">
        <h1 className="text-3xl font-bold mb-6 text-center">
          Pitcher Projections
        </h1>

        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <input
            type="text"
            placeholder="Filter by team"
            className="border px-3 py-2 rounded w-full md:w-1/2"
            value={teamFilter}
            onChange={(e) => setTeamFilter(e.target.value)}
          />
          <input
            type="date"
            className="border px-3 py-2 rounded w-full md:w-1/2"
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
          />
        </div>

        <table className="w-full table-auto border-collapse">
          <thead>
            <tr className="bg-gray-200 text-left">
              <th className="p-2">Pitcher</th>
              <th className="p-2">Team</th>
              <th className="p-2">Opponent</th>
              <th className="p-2">Date</th>
              <th className="p-2">Projected Score</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((p, i) => (
              <tr key={i} className="border-t hover:bg-gray-50">
                <td className="p-2">{p.name}</td>
                <td className="p-2">{p.team}</td>
                <td className="p-2">{p.opponent}</td>
                <td className="p-2">{p.date}</td>
                <td className="p-2">{p.score.toFixed(1)}</td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={5} className="text-center p-4 text-gray-500">
                  No pitchers found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </main>
  );
}
