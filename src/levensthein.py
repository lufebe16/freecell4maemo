
def levensthein(s1,s2,maxcnt=52):
    l1 = len(s1)
    if (l1>maxcnt): l1 = maxcnt
    l2 = len(s2)
    if (l2>maxcnt): l2 = maxcnt

    m = [[0 for k in range(0,l2+1) ] for i in range(0,l1+1) ]
    m[0][0] = 0
    for i in range(1,l1+1): m[i][0] = i
    for k in range(1,l2+1): m[0][k] = k

    for i in range (1,l1+1):
        for k in range (1,l2+1):
            if s1[i-1] == s2[k-1]:
                m[i][k] = m[i-1][k-1]
            else:
                d = m[i-1][k-1] + 1
                b = m[i][k-1] + 1
                if (b<d): d = b
                c = m[i-1][k] + 1
                if (c<d): d = c
                m[i][k] = d

    return m[l1][l2]
