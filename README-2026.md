# 🏈 Big Sarge NFL Tracker — 2026

The complete **2026 NFL regular season**: all 18 weeks, all 272 games, with live scores,
standings and a playoff picture. One self-contained HTML file, no build step, no dependencies.

**Live:** https://wayneaince-sys.github.io/big-sarge-nfl/

## Files

| File | What it is |
|---|---|
| `index.html` | The page GitHub Pages serves. **Generated — don't hand-edit.** |
| `commentary.json` | Your per-game takes. **Edit this.** |
| `tools/build_2026.py` | Regenerates `index.html` from the schedule + your commentary |
| `tools/template.html` | The page shell (styling, layout, behavior) |

## Writing your commentary

Open `commentary.json` and fill in a game. The key is the game id — `season_week_AWAY_HOME`:

```json
{
  "2026_03_ATL_GB": "Falcons are 0-2 and the wheels are coming off. Packers at Lambeau on a Thursday? Take the home team and don't overthink it."
}
```

Week 3's sixteen games are already listed as empty slots. Add any other game by following
the same pattern — no lookup needed. An empty value renders nothing, so unfinished entries
just stay invisible.

Takes appear on the game card under a gold **BIG SARGE'S TAKE** heading, in the same place
the old tracker put its predictions.

## Updating scores

```bash
curl -o games.csv https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv
python3 tools/build_2026.py games.csv index.html
```

Python 3 only, nothing to install. **Rebuilding never touches your writing** — commentary
lives in `commentary.json`, not in the generated page. The build warns you if a commentary
key doesn't match a real game, so a typo can't silently vanish.

Records, standings and playoff seeding all compute themselves from the results in the data,
so they stay correct without you editing anything.

## Accuracy notes

- **Week 18 shows TBD times.** The matchups are locked and all 16 are division games, but the
  NFL assigns days and kickoff times only after Week 17. Expect a Saturday, January 9 split.
- **Times flex from Week 5 on.** Sunday windows can move late in the season.
- **The playoff picture is approximate.** It sorts on win percentage, then division record,
  then point differential. The NFL's real head-to-head and common-games tiebreakers are not
  applied, so close seeds can flip. Entertainment only — and the page says so.

## Data source

[nflverse/nfldata](https://github.com/nflverse/nfldata). Cross-checked against the NFL's own
2026 schedule release: 272 games, the Week 5–14 bye window, and the all-division Week 18
slate all match.

---

Team names and logos are property of the National Football League.
