from pk import common

s1, s2, s3 = "a", "b", "ab"
nknocks = 5
prange = (8080, 9000)

def testMakeKnocks():
    ks = common._make_knocks(s1, nknocks, prange) 
    ks2 = common._make_knocks(s2, nknocks, prange) 
    assert all(prange[0] <= k and prange[1] >= k for k in ks)
    assert ks != ks2
