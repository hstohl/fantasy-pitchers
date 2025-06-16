import { createClient } from "@supabase/supabase-js";
import type { NextApiRequest, NextApiResponse } from "next";

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!
);

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const { team, opponent, date } = req.query;

  const { data: games, error } = await supabase.rpc("get_pitcher_projections");

  if (error) return res.status(500).json({ error: error.message });

  const results = [];

  for (const game of games || []) {
    const {
      game_date,
      away_team,
      home_team,
      away_pitcher,
      away_era_per_inning,
      away_whip,
      away_k_per_inning,
      home_pitcher,
      home_era_per_inning,
      home_whip,
      home_k_per_inning,
      away_runs_per_inning,
      away_hits_walks_per_inning,
      away_strikeouts_per_inning,
      home_runs_per_inning,
      home_hits_walks_per_inning,
      home_strikeouts_per_inning,
    } = game;

    const away_team_score =
      ((away_runs_per_inning ?? 0) * -2 +
        (away_hits_walks_per_inning ?? 0) * -1 +
        (away_strikeouts_per_inning ?? 0)) *
      6;

    const home_team_score =
      ((home_runs_per_inning ?? 0) * -2 +
        (home_hits_walks_per_inning ?? 0) * -1 +
        (home_strikeouts_per_inning ?? 0)) *
      6;

    let away_pitcher_score = away_team_score;
    let home_pitcher_score = home_team_score;

    if (away_pitcher) {
      const era =
        (away_era_per_inning ?? 0) * 0.35 + (home_runs_per_inning ?? 0) * 0.65;
      const whip =
        (away_whip ?? 0) * 0.35 + (home_hits_walks_per_inning ?? 0) * 0.65;
      const k =
        (away_k_per_inning ?? 0) * 0.35 +
        (home_strikeouts_per_inning ?? 0) * 0.65;

      away_pitcher_score = (era * -2 + whip * -1 + k) * 6;

      results.push({
        name: away_pitcher,
        team: away_team,
        opponent: home_team,
        date: game_date,
        score: Number(away_pitcher_score.toFixed(2)),
        era: away_era_per_inning,
        whip: away_whip,
        strikeouts: away_k_per_inning,
        innings: 6,
      });
    }

    if (home_pitcher) {
      const era =
        (home_era_per_inning ?? 0) * 0.35 + (away_runs_per_inning ?? 0) * 0.65;
      const whip =
        (home_whip ?? 0) * 0.35 + (away_hits_walks_per_inning ?? 0) * 0.65;
      const k =
        (home_k_per_inning ?? 0) * 0.35 +
        (away_strikeouts_per_inning ?? 0) * 0.65;

      home_pitcher_score = (era * -2 + whip * -1 + k) * 6;

      results.push({
        name: home_pitcher,
        team: home_team,
        opponent: away_team,
        date: game_date,
        score: Number(home_pitcher_score.toFixed(2)),
        era: home_era_per_inning,
        whip: home_whip,
        strikeouts: home_k_per_inning,
        innings: 6,
      });
    }
  }

  results.sort((a, b) => {
    const dateA = new Date(a.date);
    const dateB = new Date(b.date);

    if (dateA.getTime() !== dateB.getTime()) {
      return dateA.getTime() - dateB.getTime(); // Ascending by date
    }

    return b.score - a.score; // Descending by score
  });

  const filtered = results.filter(
    (p) =>
      (!team || p.team === team) &&
      (!opponent || p.opponent === opponent) &&
      (!date || p.date === date)
  );

  res.status(200).json(filtered);
}
