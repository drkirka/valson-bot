def norm(v):
    return ' '.join((v or '').split()).lower()
def height_score(a,b):
    if not a or not b:
        return 0
    d=abs(int(a)-int(b))
    if d<=10:
        return 25
    if d<=20:
        return 15
    if d<=30:
        return 5
    return 0
def score(me,other):
    s=0
    if norm(me.get('class_name'))==norm(other.get('class_name')):
        s+=40
    if me.get('gender') and other.get('gender') and me.get('gender')!=other.get('gender'):
        s+=20
    s+=height_score(me.get('height'),other.get('height'))
    if other.get('description'):
        s+=10
    if other.get('contact'):
        s+=5
    return min(s,100)
def pair(a,b):
    a=int(a)
    b=int(b)
    return (a,b) if a<b else (b,a)
