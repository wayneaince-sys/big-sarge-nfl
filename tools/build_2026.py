#!/usr/bin/env python3
"""
Build the Big Sarge NFL Tracker page for the 2026 season.

    python3 tools/build_2026.py games.csv index.html

Reads the nflverse schedule (games.csv), merges in commentary.json, and writes
a single self-contained index.html. Commentary lives in its own file, so
rebuilding for fresh scores never touches anything you wrote.
"""
import csv, json, datetime, sys, pathlib

SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'games.csv')
OUT = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else 'index.html')
COMMENTARY = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else OUT.parent / 'commentary.json'
SEASON = '2026'

TEAMS = {
 'BUF':('Buffalo Bills','Bills','AFC','East'),      'MIA':('Miami Dolphins','Dolphins','AFC','East'),
 'NE':('New England Patriots','Patriots','AFC','East'), 'NYJ':('New York Jets','Jets','AFC','East'),
 'BAL':('Baltimore Ravens','Ravens','AFC','North'),  'CIN':('Cincinnati Bengals','Bengals','AFC','North'),
 'CLE':('Cleveland Browns','Browns','AFC','North'),  'PIT':('Pittsburgh Steelers','Steelers','AFC','North'),
 'HOU':('Houston Texans','Texans','AFC','South'),    'IND':('Indianapolis Colts','Colts','AFC','South'),
 'JAX':('Jacksonville Jaguars','Jaguars','AFC','South'), 'TEN':('Tennessee Titans','Titans','AFC','South'),
 'DEN':('Denver Broncos','Broncos','AFC','West'),    'KC':('Kansas City Chiefs','Chiefs','AFC','West'),
 'LV':('Las Vegas Raiders','Raiders','AFC','West'),  'LAC':('Los Angeles Chargers','Chargers','AFC','West'),
 'DAL':('Dallas Cowboys','Cowboys','NFC','East'),    'NYG':('New York Giants','Giants','NFC','East'),
 'PHI':('Philadelphia Eagles','Eagles','NFC','East'),'WAS':('Washington Commanders','Commanders','NFC','East'),
 'CHI':('Chicago Bears','Bears','NFC','North'),      'DET':('Detroit Lions','Lions','NFC','North'),
 'GB':('Green Bay Packers','Packers','NFC','North'), 'MIN':('Minnesota Vikings','Vikings','NFC','North'),
 'ATL':('Atlanta Falcons','Falcons','NFC','South'),  'CAR':('Carolina Panthers','Panthers','NFC','South'),
 'NO':('New Orleans Saints','Saints','NFC','South'), 'TB':('Tampa Bay Buccaneers','Buccaneers','NFC','South'),
 'ARI':('Arizona Cardinals','Cardinals','NFC','West'),'LAR':('Los Angeles Rams','Rams','NFC','West'),
 'SF':('San Francisco 49ers','49ers','NFC','West'),  'SEA':('Seattle Seahawks','Seahawks','NFC','West'),
}
SLUG = {
 'BUF':'buffalo-bills','MIA':'miami-dolphins','NE':'new-england-patriots','NYJ':'new-york-jets',
 'BAL':'baltimore-ravens','CIN':'cincinnati-bengals','CLE':'cleveland-browns','PIT':'pittsburgh-steelers',
 'HOU':'houston-texans','IND':'indianapolis-colts','JAX':'jacksonville-jaguars','TEN':'tennessee-titans',
 'DEN':'denver-broncos','KC':'kansas-city-chiefs','LV':'las-vegas-raiders','LAC':'los-angeles-chargers',
 'DAL':'dallas-cowboys','NYG':'new-york-giants','PHI':'philadelphia-eagles','WAS':'washington-commanders',
 'CHI':'chicago-bears','DET':'detroit-lions','GB':'green-bay-packers','MIN':'minnesota-vikings',
 'ATL':'atlanta-falcons','CAR':'carolina-panthers','NO':'new-orleans-saints','TB':'tampa-bay-buccaneers',
 'ARI':'arizona-cardinals','LAR':'los-angeles-rams','SF':'san-francisco-49ers','SEA':'seattle-seahawks',
}
ALIAS = {'LA': 'LAR'}
VENUE_CITY = {
 'Melbourne Cricket Ground':'Melbourne, Australia','Maracana Stadium':'Rio de Janeiro, Brazil',
 'Tottenham Hotspur Stadium':'London, England','Wembley Stadium':'London, England',
 'Stade de France':'Paris, France','Bernabeu':'Madrid, Spain',
 'FC Bayern Munich Stadium':'Munich, Germany','Estadio Banorte':'Mexico City, Mexico',
}

def fmt_time(t):
    if not t:
        return 'TBD'
    h, m = int(t[:2]), t[3:5]
    return '%d:%s %s' % (h % 12 or 12, m, 'AM' if h < 12 else 'PM')

games, weeks = [], {}
for r in csv.DictReader(SRC.open()):
    if r['season'] != SEASON or r['game_type'] != 'REG':
        continue
    wk = int(r['week'])
    away = ALIAS.get(r['away_team'], r['away_team'])
    home = ALIAS.get(r['home_team'], r['home_team'])
    neutral = r['location'] != 'Home'
    g = {'id': '%s_%02d_%s_%s' % (SEASON, wk, away, home),
         'wk': wk, 'date': r['gameday'], 'day': r['weekday'],
         'time': fmt_time(r['gametime']), 'away': away, 'home': home,
         'div': r['div_game'] == '1'}
    sp = r.get('spread_line', '')
    if sp not in ('', 'NA'):
        try:
            g['sp'] = float(sp)
        except ValueError:
            pass
    if r['away_score'] and r['home_score']:
        g['as'], g['hs'] = int(r['away_score']), int(r['home_score'])
    if neutral:
        g['kind'], g['at'] = 'intl', VENUE_CITY.get(r['stadium'], r['stadium'])
    elif r['weekday'] in ('Thursday', 'Monday', 'Saturday'):
        g['kind'] = {'Thursday': 'tnf', 'Monday': 'mnf', 'Saturday': 'sat'}[r['weekday']]
    # The NFL sets Week 18 days and times only after Week 17; the feed's
    # uniform Sunday 1:00 entry is a placeholder, not a real kickoff.
    if wk == 18 and 'hs' not in g:
        g['time'], g['tbd'] = 'TBD', True
    games.append(g)
    weeks.setdefault(wk, []).append(g)

games.sort(key=lambda g: (g['wk'], g['date'], g['time']))

byes = {}
for wk in sorted(weeks):
    playing = {t for g in weeks[wk] for t in (g['home'], g['away'])}
    off = sorted(set(TEAMS) - playing, key=lambda t: TEAMS[t][0])
    if off:
        byes[wk] = off

ranges = {}
for wk in sorted(weeks):
    ds = sorted({g['date'] for g in weeks[wk]})
    a, b = (datetime.date.fromisoformat(ds[0]), datetime.date.fromisoformat(ds[-1]))
    ranges[wk] = ('%s %d' % (a.strftime('%b'), a.day) if a == b else
                  ('%s %d–%d' % (a.strftime('%b'), a.day, b.day) if a.month == b.month
                   else '%s %d – %s %d' % (a.strftime('%b'), a.day, b.strftime('%b'), b.day)))

picks = {}
PICKS = pathlib.Path(sys.argv[5]) if len(sys.argv) > 5 else OUT.parent / 'picks.json'
if PICKS.exists():
    picks = {k: v for k, v in json.loads(PICKS.read_text()).items()
             if not k.startswith('_') and v}

for g in games:
    if g['id'] in picks:
        g['pk'] = picks[g['id']]

miami = {}
MIAMI = pathlib.Path(sys.argv[4]) if len(sys.argv) > 4 else OUT.parent / 'miami_weekly.json'
if MIAMI.exists():
    mj = json.loads(MIAMI.read_text())
    if mj.get('body') and any(p.strip() for p in mj['body']):
        miami = {k: v for k, v in mj.items() if not k.startswith('_')}

commentary = {}
if COMMENTARY.exists():
    raw = json.loads(COMMENTARY.read_text())
    commentary = {k: v for k, v in raw.items()
                  if not k.startswith('_') and isinstance(v, str) and v.strip()}

known = {g['id'] for g in games}
for key in commentary:
    if key not in known:
        print('  warning: commentary key not in schedule: %s' % key, file=sys.stderr)

played = [g for g in games if 'hs' in g]
last = max((g['wk'] for g in played), default=0)
current = 1 if not last else (last if len([g for g in played if g['wk'] == last]) < len(weeks[last])
                              else min(last + 1, 18))

data = {'season': SEASON, 'games': games, 'byes': byes, 'ranges': ranges,
        'currentWeek': current, 'played': len(played), 'commentary': commentary, 'miami': miami,
        'teams': {k: {'n': v[0], 'short': v[1], 'c': v[2], 'd': v[3],
                      'u': 'https://www.nfl.com/teams/%s/' % SLUG[k]}
                  for k, v in TEAMS.items()},
        'notes': {'18': ('Week 18 matchups are locked — all 16 are division games — but the '
                         'NFL sets days and kickoff times only after Week 17. Times show TBD until '
                         'then, and expect a Saturday, January 9 split.')}}

TPL = pathlib.Path(__file__).with_name('template.html').read_text()
OUT.write_text(TPL.replace('/*__DATA__*/null',
                           json.dumps(data, separators=(',', ':')))
                  .replace('__UPDATED__', datetime.date.today().strftime('%B %d, %Y').replace(' 0', ' ')))

print('wrote %s (%d bytes)' % (OUT, OUT.stat().st_size))
print('games=%d weeks=%d played=%d current=W%d commentary=%d'
      % (len(games), len(weeks), len(played), current, len(commentary)))
