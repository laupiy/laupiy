"""Pixel-style GitHub stats card (stats + top languages + streak) -> assets/garden-stats.svg

  python tools/make_stats.py            # pakai data tools/stats.json (atau data contoh kalau belum ada)
  python tools/make_stats.py --fetch    # ambil data terbaru dari GitHub (butuh env GITHUB_TOKEN)
"""
import json, os, sys, datetime as dt, urllib.request
from pixlib import *

USER = os.environ.get('GH_USER', 'laupiy')
DISPLAY = os.environ.get('GH_DISPLAY', 'Anoy')
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stats.json')

ROSE, PLUM, INK, TEAL, SOFT = '#e0678d', '#8b3d7c', '#4a2c58', '#3f8f9f', '#a08aa8'

SAMPLE = {
    'stars': 0, 'commits': 40, 'prs': 1, 'issues': 0, 'contributed': 2,
    'langs': [['JavaScript', 48.26, '#f1e05a'], ['TypeScript', 29.67, '#3178c6'], ['Python', 10.43, '#3572A5'],
              ['HTML', 6.35, '#e34c26'], ['CSS', 5.29, '#663399']],
    'total_contrib': 54, 'since': 'Oct 16, 2025',
    'cur_streak': 1, 'cur_date': 'Nov 23', 'best_streak': 1, 'best_date': 'Oct 16, 2025',
}


# ------------------------------------------------------------------ fetching
def gql(token, query, variables=None):
    req = urllib.request.Request('https://api.github.com/graphql',
                                 data=json.dumps({'query': query, 'variables': variables or {}}).encode(),
                                 headers={'Authorization': f'bearer {token}', 'Content-Type': 'application/json',
                                          'User-Agent': 'pixel-stats'})
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.load(r)
    if 'errors' in out:
        raise RuntimeError(out['errors'])
    return out['data']


Q = '''query($login:String!){user(login:$login){createdAt
 contributionsCollection{totalCommitContributions totalPullRequestContributions totalIssueContributions
  contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}
 repositoriesContributedTo(first:1,contributionTypes:[COMMIT,ISSUE,PULL_REQUEST,REPOSITORY]){totalCount}
 pullRequests{totalCount} issues{totalCount}
 repositories(first:100,ownerAffiliations:OWNER,isFork:false){nodes{stargazerCount
  languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name color}}}}}}}'''


def fmt(d):
    return d.strftime('%b ') + str(d.day)


def fetch(token):
    u = gql(token, Q, {'login': USER})['user']
    cc = u['contributionsCollection']
    langs = {}
    stars = 0
    for r in u['repositories']['nodes']:
        stars += r['stargazerCount']
        for e in r['languages']['edges']:
            n = e['node']
            cur = langs.setdefault(n['name'], [0, n['color'] or '#c7a6d9'])
            cur[0] += e['size']
    tot = sum(v[0] for v in langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:6]
    langs = [[k, v[0] * 100 / tot, v[1]] for k, v in top]
    days = [(dt.date.fromisoformat(d['date']), d['contributionCount'])
            for w in cc['contributionCalendar']['weeks'] for d in w['contributionDays']]
    today = dt.date.today()
    days = [x for x in days if x[0] <= today]
    best, run, best_end, start = 0, 0, None, None
    for d, c in days:
        if c > 0:
            run += 1
            if run > best:
                best, best_end = run, d
        else:
            run = 0
    cur, cur_end = 0, None
    seq = days[:]
    if seq and seq[-1][1] == 0:      # hari ini belum ada kontribusi -> streak masih hidup dari kemarin
        seq = seq[:-1]
    for d, c in reversed(seq):
        if c > 0:
            cur += 1
            cur_end = cur_end or d
        else:
            break
    return {
        'stars': stars, 'commits': cc['totalCommitContributions'], 'prs': u['pullRequests']['totalCount'],
        'issues': u['issues']['totalCount'], 'contributed': u['repositoriesContributedTo']['totalCount'],
        'langs': langs,
        'total_contrib': cc['contributionCalendar']['totalContributions'],
        'since': fmt(days[0][0]) + ', ' + str(days[0][0].year),
        'cur_streak': cur, 'cur_date': fmt(cur_end) if cur_end else '-',
        'best_streak': best, 'best_date': (fmt(best_end - dt.timedelta(days=best - 1)) if best_end else '-'),
    }


# -------------------------------------------------------------------- sprites
STAR = ['...X...', '..XXX..', 'XXXXXXX', '.XXXXX.', '..XXX..', '.XX.XX.', '.X...X.']
COMMIT = ['...X...', '...X...', '..XXX..', '.XX.XX.', '..XXX..', '...X...', '...X...']
PR = ['XX...X.', 'XX..XXX', '.X...X.', '.X...X.', '.X...X.', 'XX..XX.', 'XX..XX.']
ISSUE = ['.XXXXX.', 'X..X..X', 'X..X..X', 'X..X..X', 'X.....X', 'X..X..X', '.XXXXX.']
REPO = ['XXXXXX.', 'X....X.', 'X.XX.X.', 'X....X.', 'XXXXXX.', 'X....X.', 'XXXXXX.']
FLAME = ['....X....', '...XX....', '...XXX...', '..XXXXX..', '..XXXXXX.', '.XXXXXXX.', '.XXXYYXX.',
         '.XXYYYYX.', '.XXYYYYX.', '..XYYYY..', '...YYY...']


def rank(s):
    score = s['commits'] + s['prs'] * 3 + s['issues'] * 2 + s['stars'] * 4 + s['contributed'] * 3
    for lim, r in ((400, 'S'), (250, 'A+'), (150, 'A'), (100, 'B+'), (60, 'B')):
        if score >= lim:
            return r, min(1, score / 400)
    return 'C', min(1, score / 400)


def alloc(vals, n):
    tot = sum(vals) or 1
    raw = [v * n / tot for v in vals]
    out = [int(r) for r in raw]
    for i in sorted(range(len(vals)), key=lambda i: -(raw[i] - out[i]))[:n - sum(out)]:
        out[i] += 1
    return out


# ----------------------------------------------------------------------- card
def make(s):
    W, H = 860, 424
    d = Doc(W, H, title=f"{DISPLAY}'s GitHub stats: {s['commits']} commits, {s['prs']} PRs, "
                        f"streak {s['cur_streak']}, top language {s['langs'][0][0] if s['langs'] else '-'}")
    d.css.append('.fl{animation:fl .8s steps(1) infinite}@keyframes fl{0%{transform:translateY(0)}50%{transform:translateY(-3px)}}'
                 '.tw{animation:tw 2.4s steps(1) infinite}@keyframes tw{0%{opacity:1}50%{opacity:.25}}')
    CARD_BG = '#fff0f6'

    # ---------- card 1: stats
    d.add(px_frame(4, 4, 420, 244, 4, CARD_BG, ROSE, '#f3b8cc', 4))
    d.text(28, 42, f'{DISPLAY.lower()}’s stats', 'ps2p', 13, '#b93b74')
    d.text(28, 62, 'last 12 months', 'pix4', 14, SOFT)
    rows = [(STAR, '#f2b705', 'Stars earned', s['stars']), (COMMIT, ROSE, 'Commits', s['commits']),
            (PR, TEAL, 'Pull requests', s['prs']), (ISSUE, '#9c7ee0', 'Issues', s['issues']),
            (REPO, '#7fa83a', 'Contributed to', s['contributed'])]
    for i, (spr, col, lab, val) in enumerate(rows):
        y = 100 + i * 31
        d.add(f'<g transform="translate(28 {y - 17}) scale(3)">{sprite(spr, {"X": col}).svg()}</g>')
        d.text(62, y, lab, 'pix7', 18, INK)
        d.text(296, y, str(val), 'pix7', 18, '#b93b74', anchor='end')
    r, pct = rank(s)
    d.add(px_frame(322, 82, 84, 84, 4, '#ffffff', PLUM, '#f3b8cc', 4))
    d.text(364, 138, r, 'ps2p', 30 if len(r) == 1 else 22, '#b93b74', anchor='middle')
    d.text(364, 188, 'rank', 'pix7', 14, SOFT, anchor='middle')
    # pixel xp bar
    d.add(f'<rect x="322" y="198" width="84" height="12" fill="{PLUM}"/><rect x="324" y="200" width="80" height="8" fill="#ffe3ee"/>')
    d.add(f'<rect x="324" y="200" width="{max(4, int(80 * pct) // 4 * 4)}" height="8" fill="{ROSE}"/>')

    # ---------- card 2: languages
    d.add(px_frame(436, 4, 420, 244, 4, CARD_BG, ROSE, '#f3b8cc', 4))
    d.text(460, 42, 'top languages', 'ps2p', 13, '#b93b74')
    langs = s['langs'][:6]
    N = 30
    counts = alloc([l[1] for l in langs], N)
    d.add(f'<rect x="460" y="62" width="372" height="22" fill="{PLUM}"/><rect x="462" y="64" width="368" height="18" fill="#ffffff"/>')
    bx = 464
    for (nm, p, col), c in zip(langs, counts):
        for _ in range(c):
            d.add(f'<rect x="{bx}" y="66" width="10" height="10" fill="{col}"/>')
            bx += 12
    for i, (nm, p, col) in enumerate(langs):
        cx = 460 + (i % 2) * 190
        y = 126 + (i // 2) * 38
        d.add(px_frame(cx, y - 14, 16, 16, 2, col, PLUM))
        d.text(cx + 26, y, nm, 'pix7', 18, INK)
        d.text(cx + 26, y + 17, f'{p:.1f}%', 'pix4', 14, SOFT)

    # ---------- card 3: streak
    d.add(px_frame(4, 260, 852, 160, 4, CARD_BG, ROSE, '#f3b8cc', 4))
    cols = [(146, s['total_contrib'], 'Contributions', s['since'] + ' - now', False),
            (430, s['cur_streak'], 'Current streak', s['cur_date'], True),
            (714, s['best_streak'], 'Longest streak', s['best_date'], False)]
    for x in (288, 572):
        d.add(f'<rect x="{x}" y="284" width="4" height="116" fill="#ffd1e0"/>')
    for cx, num, lab, sub, hot in cols:
        n = str(num)
        if hot:
            d.add(px_frame(cx - 46, 302, 92, 54, 4, '#ffffff', ROSE, '#f3b8cc', 4))
            fl = sprite(FLAME, {'X': '#ff7fa6', 'Y': '#ffe27a'})
            d.add(f'<g transform="translate({cx - 14} 270) scale(3)"><g class="fl">{fl.svg()}</g></g>')
            d.text(cx, 337, n, 'ps2p', 24, '#b93b74', anchor='middle')
            d.text(cx, 381, lab, 'pix7', 18, '#e0527f', anchor='middle')
        else:
            d.text(cx, 336, n, 'ps2p', 30, INK, anchor='middle')
            d.text(cx, 372 + 10, lab, 'pix7', 18, TEAL, anchor='middle')
        d.text(cx, 406, sub, 'pix4', 14, SOFT, anchor='middle')
    d.save('assets/garden-stats.svg')


if __name__ == '__main__':
    data = dict(SAMPLE)
    if '--fetch' in sys.argv:
        data = fetch(os.environ['GITHUB_TOKEN'])
        json.dump(data, open(DATA, 'w'), indent=1)
    elif os.path.exists(DATA):
        data = json.load(open(DATA))
    print(make(data) or 'assets/garden-stats.svg ok')
