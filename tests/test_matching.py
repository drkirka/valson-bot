from bot.matching import height_score,score,pair
def test_height_score_close():
    assert height_score(170,175)==25
def test_height_score_medium():
    assert height_score(170,188)==15
def test_height_score_far():
    assert height_score(170,220)==0
def test_pair_order():
    assert pair(10,2)==(2,10)
def test_score():
    me={'gender':'girl','class_name':'L','height':170}
    other={'gender':'boy','class_name':'l','height':178,'description':'hello','contact':'@test'}
    assert score(me,other)==100
