from pk import common

s1, s2, s3 = "a", "b", "ab"
prange = (8080, 9000)

def testMakeKnocks():
    ks = common._make_knocks(s1, prange) 
    ks2 = common._make_knocks(s2, prange) 
    assert all(prange[0] <= k and prange[1] >= k for k in ks)
    assert ks != ks2
