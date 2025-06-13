// frontend/pages/api/pitchers.ts
import type { NextApiRequest, NextApiResponse } from "next";
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!
);

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const { team, opponent, date } = req.query;

  let query = supabase.from("pitchers").select("*");

  if (team) query = query.eq("team", team);
  if (opponent) query = query.eq("opponent", opponent);
  if (date) query = query.eq("game_date", date);

  const { data, error } = await query;

  if (error) return res.status(500).json({ error: error.message });

  const scored = data.map((p: any) => ({
    ...p,
    score: (p.era / 9 + p.whip / 2).toFixed(2),
  }));

  res.status(200).json(scored);
}
