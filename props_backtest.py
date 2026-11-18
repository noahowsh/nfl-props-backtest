"""Backtest NFL player props against the closing line with EndzoneAPI.

    pip install -r requirements.txt
    export ENDZONEAPI_API_KEY=...     # free key: https://endzoneapi.com/signup

    # One player: every closing line since a date beside what he recorded.
    python props_backtest.py player "Travis Kelce" --market player_reception_yds --since 2025-09-01

    # One idea across the league: tight end receiving-yards overs for home underdogs.
    python props_backtest.py idea --market player_reception_yds --side over --position TE --home-away home --role underdog

Credits: search 2, each page of history 10 per 25 games, one backtest 25. All of
it fits in the free 500 credits a month.
"""
import argparse

import pandas as pd
from endzoneapi import Client


def implied(american):
    """American odds -> implied probability (with the book's margin in it)."""
    a = float(american)
    return 100 / (a + 100) if a > 0 else -a / (-a + 100)


def player_history(client, name, market, since):
    match = client.search_players(name, limit=1)["players"]
    if not match:
        raise SystemExit(f"No player found for {name!r}")
    player = match[0]
    rows, start = [], since
    while start:
        # client.call reaches any tool by name, so this works on every client version.
        page = client.call("get_prop_history", {"player_id": player["player_id"], "market": market, "from_date": start, "limit": 200})
        rows += page["games"]
        start = page.get("next_from_date") if page.get("truncated") else None
    return player, pd.DataFrame(rows)


def run_player(client, args):
    player, df = player_history(client, args.name, args.market, args.since)
    if df.empty:
        raise SystemExit("No graded lines in that range.")
    graded = df[df["result"].isin(["over", "under"])].copy()
    graded["over_implied"] = graded["over_odds"].map(implied)
    print(f"{player['name']} {args.market}, {len(graded)} graded games since {args.since}")
    print(f"  over rate {(graded['result'] == 'over').mean():.1%} vs {graded['over_implied'].mean():.1%} implied by the over price")
    print(f"  average line {graded['line'].mean():.1f}, average actual {graded['actual'].mean():.1f}, mean margin {graded['margin'].mean():+.1f}")
    moved = graded[graded["open_line"].notna() & (graded["open_line"] != graded["line"])]
    if len(moved):
        up = moved[moved["line"] > moved["open_line"]]
        print(f"  line moved open to close in {len(moved)} games; when it moved up the over hit {(up['result'] == 'over').mean():.1%} of {len(up)}")
    print(graded[["game_id", "open_line", "line", "actual", "result"]].tail(10).to_string(index=False))


def run_idea(client, args):
    params = {"market": args.market, "side": args.side, "position": args.position, "home_away": args.home_away,
              "team_role": args.role, "from_season": args.from_season}
    r = client.call("get_prop_backtest", {k: v for k, v in params.items() if v is not None})
    lo, hi = r["hit_rate_interval_95"]
    print(f"{r['label']} {r['side']}s, filters {r['filters']}")
    print(f"  {r['results']:,} results across {r['games']:,} games and {r['players']:,} players")
    print(f"  hit rate {r['hit_rate']:.1%} (95% interval {lo:.1%} to {hi:.1%})")
    print(f"  market implied {r['avg_implied_prob']:.1%}, fair (margin removed) {r['avg_fair_prob']:.1%}")
    print("  by season:")
    for s in r["by_season"]:
        print(f"    {s['season']}: {s['hit_rate']:.1%} of {s['results']:,} (fair {s['avg_fair_prob']:.1%})")
    print("  A past hit rate is a description of the sample, not a forecast.")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)
    p = sub.add_parser("player")
    p.add_argument("name")
    p.add_argument("--market", default="player_reception_yds")
    p.add_argument("--since", default="2025-09-01")
    i = sub.add_parser("idea")
    i.add_argument("--market", default="player_reception_yds")
    i.add_argument("--side", choices=["over", "under"], default="over")
    i.add_argument("--position", help="QB, RB, WR or TE")
    i.add_argument("--home-away", choices=["home", "away"])
    i.add_argument("--role", choices=["favorite", "underdog"])
    i.add_argument("--from-season", type=int, help="first season, e.g. 2024 (seasons are the year they start)")
    args = ap.parse_args()

    client = Client()
    run_player(client, args) if args.mode == "player" else run_idea(client, args)
    print("credits left:", client.last_credits_remaining)


if __name__ == "__main__":
    main()
