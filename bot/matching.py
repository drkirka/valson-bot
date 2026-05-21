def norm_class(value):
    return ' '.join((value or '').split()).lower()

def height_points(a,b):
    if not a or not b:
        return 0
    diff=abs(int(a)-int(b))
    if diff<=10:
        return 25
    if diff<=20:
        return 15
    if diff<=30:
        return 5
    return 0

def compatibility_score(viewer,target):
    score=0
    if norm_class(viewer.get('class_name'))==norm_class(target.get('class_name')):
        score+=40
    if viewer.get('gender') and target.get('gender') and viewer.get('gender')!=target.get('gender'):
        score+=20
    score+=height_points(viewer.get('height'),target.get('height'))
    if target.get('description'):
        score+=10
    if target.get('contact'):
        score+=5
    return min(score,100)

def match_pair(a,b):
    a=int(a)
    b=int(b)
    return (a,b) if a<b else (b,a)
