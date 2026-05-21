def vals(v):
    if not v:
        return set()
    return {x.strip().lower() for x in v.replace(';', ',').split(',') if x.strip()}

def norm(v):
    return (v or '').strip().lower()

def roles_ok(role, pref):
    role = norm(role)
    pref = norm(pref)
    if not role or not pref:
        return False
    if role == 'both' or pref == 'both':
        return True
    return role != pref

def height_ok(height, min_h, max_h):
    if height is None:
        return False
    return min_h <= height <= max_h

def calculate_match_score(a, b):
    score = 0
    why = []
    if norm(a.get('preferred_class')) == norm(b.get('class_name')):
        score += 25
        why.append('class')
    if roles_ok(b.get('role'), a.get('preferred_role')):
        score += 20
        why.append('role')
    if height_ok(b.get('height'), a.get('min_height'), a.get('max_height')):
        score += 15
        why.append('height')
    if norm(a.get('experience')) == norm(b.get('experience')):
        score += 15
        why.append('experience')
    if vals(a.get('availability')) & vals(b.get('availability')):
        score += 15
        why.append('availability')
    if norm(a.get('tempo')) and norm(a.get('tempo')) == norm(b.get('tempo')):
        score += 5
        why.append('tempo')
    if vals(a.get('goals')) & vals(b.get('goals')):
        score += 5
        why.append('goals')
    return min(score, 100), why

def rank_matches(me, candidates):
    res = []
    for p in candidates:
        if p['user_id'] == me['user_id']:
            continue
        score, why = calculate_match_score(me, p)
        if score:
            p = dict(p)
            p['match_score'] = score
            p['match_reasons'] = why
            res.append(p)
    return sorted(res, key=lambda p: p['match_score'], reverse=True)
