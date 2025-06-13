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

  const { data: games, error } = await supabase.from("games").select(`
      game_id, game_date, away_team, home_team,
      away_pitcher:away_pitcher_id ( name, era_per_inning, whip, k_per_inning ),
      home_pitcher:home_pitcher_id ( name, era_per_inning, whip, k_per_inning ),
      away_team_stats:away_team ( runs_per_inning, hits_walks_per_inning, strikeouts_per_inning ),
      home_team_stats:home_team ( runs_per_inning, hits_walks_per_inning, strikeouts_per_inning )
    `);

  if (error) return res.status(500).json({ error: error.message });

  const results = [];

  for (const game of games || []) {
    const {
      game_date,
      away_team,
      home_team,
      away_pitcher,
      home_pitcher,
      away_team_stats,
      home_team_stats,
    } = game;

    const awayStats = away_team_stats?.[0] || {};
    const homeStats = home_team_stats?.[0] || {};
    const awayPitcher = away_pitcher?.[0] || null;
    const homePitcher = home_pitcher?.[0] || null;

    const away_team_score =
      ((awayStats.runs_per_inning ?? 0) * -2 +
        (awayStats.hits_walks_per_inning ?? 0) * -1 +
        (awayStats.strikeouts_per_inning ?? 0)) *
      6;

    const home_team_score =
      ((homeStats.runs_per_inning ?? 0) * -2 +
        (homeStats.hits_walks_per_inning ?? 0) * -1 +
        (homeStats.strikeouts_per_inning ?? 0)) *
      6;

    let away_pitcher_score = away_team_score;
    let home_pitcher_score = home_team_score;

    if (awayPitcher) {
      const era =
        (awayPitcher.era_per_inning ?? 0) * 0.35 +
        (homeStats.runs_per_inning ?? 0) * 0.65;
      const whip =
        (awayPitcher.whip ?? 0) * 0.35 +
        (homeStats.hits_walks_per_inning ?? 0) * 0.65;
      const k =
        (awayPitcher.k_per_inning ?? 0) * 0.35 +
        (homeStats.strikeouts_per_inning ?? 0) * 0.65;

      away_pitcher_score = (era * -2 + whip * -1 + k) * 6;
    }

    if (homePitcher) {
      const era =
        (homePitcher.era_per_inning ?? 0) * 0.35 +
        (awayStats.runs_per_inning ?? 0) * 0.65;
      const whip =
        (homePitcher.whip ?? 0) * 0.35 +
        (awayStats.hits_walks_per_inning ?? 0) * 0.65;
      const k =
        (homePitcher.k_per_inning ?? 0) * 0.35 +
        (awayStats.strikeouts_per_inning ?? 0) * 0.65;

      home_pitcher_score = (era * -2 + whip * -1 + k) * 6;
    }

    if (awayPitcher) {
      results.push({
        name: awayPitcher.name,
        team: away_team,
        opponent: home_team,
        date: game_date,
        score: Number(away_pitcher_score.toFixed(2)),
        era: awayPitcher.era_per_inning,
        whip: awayPitcher.whip,
        strikeouts: awayPitcher.k_per_inning,
      });
    }

    if (homePitcher) {
      results.push({
        name: homePitcher.name,
        team: home_team,
        opponent: away_team,
        date: game_date,
        score: Number(home_pitcher_score.toFixed(2)),
        era: homePitcher.era_per_inning,
        whip: homePitcher.whip,
        strikeouts: homePitcher.k_per_inning,
      });
    }
  }

  //   const filtered = results.filter(
  //     (p) =>
  //       (!team || p.team === team) &&
  //       (!opponent || p.opponent === opponent) &&
  //       (!date || p.date === date)
  //   );

  const filtered = results;

  res.status(200).json(filtered);
}
