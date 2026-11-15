"""Fetch live GitHub data for the Solar System README and write scripts/data.json.
Runs inside GitHub Actions (uses the built-in GITHUB_TOKEN). Zero dependencies.
If anything fails, the previous data.json is kept, so the README never breaks."""
import base64, html, json, os, re, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, 'data.json')
LOGIN = os.environ.get('GH_LOGIN') or 'Build-With-MTT'
TOKEN = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN') or ''

QUERY = '''
query($login: String!) {
  user(login: $login) {
    avatarUrl(size: 240)
    followers { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      totalCount
      nodes {
        name description stargazerCount forkCount
        primaryLanguage { name }
        languages(first: 8, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}'''


def http(url, data=None, headers=None, timeout=30):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.headers.get('content-type', '')


def graphql():
    body = json.dumps({'query': QUERY, 'variables': {'login': LOGIN}}).encode()
    raw, _ = http('https://api.github.com/graphql', body, {
        'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json', 'User-Agent': 'solar-system-readme'})
    j = json.loads(raw)
    if j.get('errors'):
        raise RuntimeError(j['errors'])
    return j['data']['user']


def contributions_from_html():
    """Fallback: public contribution calendar page (no token needed)."""
    raw, _ = http(f'https://github.com/users/{LOGIN}/contributions', headers={'User-Agent': 'solar-system-readme'})
    h = raw.decode('utf-8', 'ignore')
    cells = re.findall(r'<td[^>]*data-date="(\d{4}-\d{2}-\d{2})"[^>]*id="([^"]+)"', h)
    tips = dict(re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]+)</tool-tip>', h))
    days = []
    for date, cid in cells:
        m = re.match(r'(\d+) contribution', html.unescape(tips.get(cid, '')))
        days.append({'date': date, 'count': int(m.group(1)) if m else 0})
    days.sort(key=lambda d: d['date'])
    return days


def build(user, old):
    """Turn the GraphQL user object into the data.json structure."""
    out = dict(old)
    repos_all = user['repositories']['nodes']
    repos = [r for r in repos_all if r['name'].lower() != LOGIN.lower()]  # skip the profile repo itself
    out['followers'] = user['followers']['totalCount']
    out['repo_count'] = len(repos)
    out['stars'] = sum(r['stargazerCount'] for r in repos)
    # language share by bytes across public repos
    tot = {}
    for r in repos:
        for e in r['languages']['edges']:
            tot[e['node']['name']] = tot.get(e['node']['name'], 0) + e['size']
    s = sum(tot.values()) or 1
    top = sorted(tot.items(), key=lambda kv: -kv[1])[:5]
    out['languages'] = [[n, max(1, round(100 * b / s))] for n, b in top]
    out['comets'] = [r['name'] for r in repos[:3]]  # most recently pushed
    out['repos'] = {r['name']: {'stars': r['stargazerCount'], 'forks': r['forkCount'],
                                'language': (r['primaryLanguage'] or {}).get('name') or '',
                                'description': r['description'] or ''} for r in repos}
    cal = user['contributionsCollection']['contributionCalendar']
    out['total_contributions'] = cal['totalContributions']
    out['days'] = [{'date': d['date'], 'count': d['contributionCount']} for w in cal['weeks'] for d in w['contributionDays']]
    return out


def main():
    old = json.load(open(PATH, encoding='utf-8')) if os.path.exists(PATH) else {}
    data = dict(old)
    data['login'] = LOGIN
    try:
        user = graphql()
        data = build(user, data)
        try:  # keep the sun's photo in sync with the GitHub avatar
            img, ctype = http(user['avatarUrl'])
            data['avatar_b64'] = base64.b64encode(img).decode()
            data['avatar_mime'] = ctype.split(';')[0] or 'image/jpeg'
        except Exception as e:
            print('avatar skipped:', e)
        print('GraphQL ok')
    except Exception as e:
        print('GraphQL failed, trying public calendar only:', e)
        try:
            days = contributions_from_html()
            if days:
                data['days'] = days
                data['total_contributions'] = sum(d['count'] for d in days[-365:])
                print('calendar fallback ok')
        except Exception as e2:
            print('fallback failed, keeping previous data:', e2)
    new = json.dumps(data, ensure_ascii=False, indent=0, sort_keys=True)
    if not os.path.exists(PATH) or open(PATH, encoding='utf-8').read() != new:
        open(PATH, 'w', encoding='utf-8').write(new)
        print('data.json updated')
    else:
        print('no change')


if __name__ == '__main__':
    main()
