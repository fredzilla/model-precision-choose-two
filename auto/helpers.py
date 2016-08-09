from collections import defaultdict
from scipy.stats import kendalltau
from math import log
from itertools import combinations
from nltk.corpus import wordnet as wn
from nltk.corpus import genesis


def inverted_index(corpus):
    iindex = defaultdict(set)
    for idoc, doc in enumerate(corpus):
        for word in doc:
            iindex[word].add(idoc)
    return iindex


def make_kendalls_tau(ids1, ids2):
    gold_standard = {y: x + 1 for x, y in enumerate(ids1)}
    worst_score = len(ids1) + 1

    second_set = []
    for i in ids2:
        score = gold_standard.get(i, worst_score)
        second_set.append(score)

    return kendalltau(range(1, worst_score), second_set)


def spearmans_rank(ids1, ids2):
    second_set = {y: x + 1 for x, y in enumerate(ids2)}
    worst_score = len(ids1)
    n = len(ids1)

    error = 0.
    for rank, id in enumerate(ids1, start=1):
        srank = second_set.get(id, worst_score)
        error += (srank - rank) ** 2

    rho = 1 - 6 * error / (n * (n**2 - 1))
    return rho


def compute_hhi(distribution):
    sy = sum([y for x, y in distribution])
    hhi = sum([(y/sy)**2 for x, y in distribution])
    n = len(distribution)
    nhhi = (hhi - 1 / n) / (1 - 1 / n)
    return nhhi


### Wordnet-based measures
def no_senses(topic, k=5):
    words = [i for i, j in topic.most_common(k)]
    s = sum([len(wn.synsets(w)) for w in words])
    return s

genesis_ic = wn.ic(genesis, False, 0.0)
def jiang_conrath_ds(topic, k=5, tisw=False):
    if not tisw:
        words = [i for i, j in topic.most_common(k)]
    else:
        words = topic
    s = []
    for wi, wj in combinations(words, 2):
        wis = wn.synsets(wi)
        wjs = wn.synsets(wj)
        for i in wis:
            for j in wjs:
                if i.pos() != j.pos() or i.pos() == 's':
                    continue
                s.append(i.jcn_similarity(j, genesis_ic))
    return sum(s) * 1.0 / len(s)

def intruded_jiang_conrath(words, intruded, aggFn=None):
    s = []
    wi = intruded
    wis = wn.synsets(wi)
    for wj in words:
        wjs = wn.synsets(wj)
        for i in wis:
            for j in wjs:
                if i.pos != j.pos or i.pos == 's':
                    continue
                s.append(i.jcn_similarity(j, genesis_ic))
    if len(s) == 0:
        return 1
    else:
        if aggFn is None:
            return sum(s) * 1.0 / len(s)
        else:
            return aggFn(s)


