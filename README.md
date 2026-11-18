# nfl-props-backtest

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/noahowsh/nfl-props-backtest/blob/main/props_backtest.ipynb)

Check NFL player props against the closing line, using real sportsbook history since 2023. Two modes, one script:

- **player:** every closing line for one player and market beside what he actually recorded, his over rate against the price, and what happened when the line moved.
- **idea:** test a league-wide angle ("tight end receiving-yards overs for home underdogs") in one call, with the sample size, a 95% interval, and the market's implied and margin-free probability.

```bash
pip install -r requirements.txt
export ENDZONEAPI_API_KEY=your_key      # free: https://endzoneapi.com/signup (500 credits a month)

python props_backtest.py player "Travis Kelce" --market player_reception_yds --since 2025-09-01
python props_backtest.py idea --market player_reception_yds --side over --position TE --home-away home --role underdog
```

Example output (Nov 2026):

```
receiving yards overs, filters {'position': 'TE', 'home_away': 'home', 'team_role': 'underdog'}
  561 results across 390 games and 96 players
  hit rate 50.6% (95% interval 46.5% to 54.7%)
  market implied 53.3%, fair (margin removed) 50.1%
  by season:
    2023: 56.5% of 131 (fair 50.0%)
    2024: 53.8% of 145 (fair 50.1%)
    2025: 45.9% of 194 (fair 50.2%)
    2026: 47.3% of 91 (fair 49.9%)
```

A sample that beat the market one season and lost the next is what most angles look like. That is the point of checking by season.

## Markets

`player_pass_yds`, `player_pass_tds`, `player_pass_completions`, `player_pass_attempts`, `player_pass_interceptions`, `player_rush_yds`, `player_rush_attempts`, `player_receptions`, `player_reception_yds`, `player_anytime_td`, and the longest-play markets.

## The data

[EndzoneAPI](https://endzoneapi.com/data/player-props?utm_source=github&utm_medium=readme&utm_campaign=nfl-props-backtest) holds NFL prop lines by sportsbook, with the closing line and the opening line where held. `get_prop_history` grades each closing line against the box score; `get_prop_backtest` runs the aggregate with filters for position, home or away, favorite or underdog, week and line range.

Credits: a player search costs 2, history 10 for every 25 games a call covers, and a backtest 25.

## Ideas to extend it

- Loop over a depth chart (`get_depth_chart`) and rank receivers by margin against the closing line.
- Join to `get_snap_counts` and `get_advanced_stats` for target share, and model the line yourself.
- Compare the opening and closing line to see which moves held up.

This is a research tool. A past hit rate describes a sample; it is not a pick.

Uses the [endzoneapi](https://pypi.org/project/endzoneapi/) Python client (no dependencies). EndzoneAPI is also a hosted MCP server for Claude, ChatGPT and Cursor: https://endzoneapi.com/mcp?utm_source=github&utm_medium=readme&utm_campaign=nfl-props-backtest

MIT licensed.
