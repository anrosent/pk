from pk import common

s1, s2, s3 = "a", "b", "ab"

def testMakeKnocks():
    ks = common._make_knocks(s1) 
    ks2 = common._make_knocks(s2) 
    assert all(common.min_port <= k and common.max_port >= k for k in ks)
    assert ks != ks2
