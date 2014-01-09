# !/usr/bin/python
# -*- coding: utf-8 -*-

import math

def prf(tlist, plist, n):
    '''
    cal the (precision, recall, f-score)

    rlist:real values list
    plist:predicted values list
    n:compare first n values
    '''

    if not (tlist and plist):
        return .0, .0, .0

    tset = set(tlist)
    pset = set(plist[:n])

    m = float(len(pset.intersection(tset)))

    precision = m/len(pset)
    recall = m/len(tset)
    fscore = 2*precision*recall/(precision+recall+0.1)

    return precision, recall, fscore

def ap(tlist, plist, n):
    '''
    cal the average precision

    rlist:real values list
    plist:predicted values list
    n:compare first n values
    '''
    if not (tlist and plist):
        return .0, .0, .0

    apval = .0
    last_recall = .0
    for i in range(n+1)[1:]:
        if i>len(plist):
            break
        precision, recall, _ = prf(tlist, plist, i)
        apval += precision*(recall-last_recall)
        last_recall = recall

    return apval

def ndcg(tlist, plist, n):
    '''
    cal the ndcg value

    rlist:real values list
    plist:predicted values list
    n:compare first n values
    '''
    if not (tlist and plist):
        return .0, .0, .0

    wdict = {}
    for i in range(len(tlist)):
        wdict[tlist[i]] = 1.0/(i+1.0)
    ndcg = .0; ndcgopt = .0
    for i in range(len(plist[:n])):
        if plist[i] in wdict:
            w = wdict[plist[i]]
        else:
            w = 1.0/len(tlist)

        ndcg += (pow(2, w)-1)/math.log(i+2, 2)
        ndcgopt += (pow(2, 1.0/(i+1.0))-1)/math.log(i+2, 2)

    return ndcg / ndcgopt




if __name__ == '__main__':
    tlist = [1,2,3,4, 5]
    plist = [4,1, 2,5,3]

    for n in [1,2,3,4, 5]:
        print '\n', n
        print prf(tlist, plist, n)
        print ap(tlist, plist, n)
        print ndcg(tlist, plist, n)
