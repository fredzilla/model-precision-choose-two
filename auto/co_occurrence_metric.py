from collections import Counter
import random
import sys
from math import log
import numpy as np
from helpers import *


def load_corpus(filename):
    docs = []
    wc = Counter()
    for line in open(filename):
        words = line.strip().split(" ")
        docs.append(words)
        wc.update(words)

    return docs, wc


def mimno_coherence(topic_words, corpus):
    nwords = len(topic_words)
    corpus = [frozenset(x) for x in corpus]
    p = 0.
    for iidx in range(1, nwords):
        for jidx in range(iidx):
            wordi = topic_words[iidx]
            wordj = topic_words[jidx]
            num = 0.
            den = 0.
            for file in corpus:
                num += int(wordi in file and wordj in file)
                den += int(wordj in file)
            if den == 0:
                print(wordi, wordj)
            p += log((num + 1) / den)
    return p


def mimno_coherence_ii(topic_words, iicorpus):
    nwords = len(topic_words)
    p = 0.
    for iidx in range(1, nwords):
        for jidx in range(iidx):
            wordi = topic_words[iidx]
            wordj = topic_words[jidx]
            num = len(iicorpus[wordi] & iicorpus[wordj])
            den = len(iicorpus[wordj])
            if den == 0:
                print(wordi, wordj)
            else:
                try:
                    p += log((num + 1.0) / den)
                except ValueError as e:
                    print("ERROR", num, den)
                    sys.exit(1)
    return p


def pnmi_ii(topic_words, iicorpus, ndocs=-1):
    nwords = len(topic_words)
    p = 0.
    if ndocs == -1:
        #figure out how many documents are in the corpus
        docs = set([])
        for v in iicorpus.values():
            docs |= set(v)
        ndocs = float(len(docs))  # a raw count of the number of documents
    for iidx in range(1, nwords):
        for jidx in range(iidx):
            wordi = topic_words[iidx]
            wordj = topic_words[jidx]
            numnum = len(iicorpus[wordi] & iicorpus[wordj]) + 1
            numnum /= ndocs
            numden = len(iicorpus[wordi]) * len(iicorpus[wordj])
            numden /= ndocs
            den = numnum

            try:
                p += log(float(numnum) / numden) / (-log(den))
            except ZeroDivisionError as zde:
                pass
    return p


def build_random_coherence(num_words, corpus, wcounts, iters=10):
    dist = []
    for i in range(iters):
        # select k words based on probability
        topic = make_random_topic(wcounts.items(), num_words)
        dist.append(mimno_coherence(topic, corpus))
        sys.stderr.write("Testing Topic %d. Value was %f.\n" % (i + 1, dist[-1]))

    return np.mean(dist), np.std(dist)


def test_individual_topic(topic_words, topic, corpus, iters=1000):
    #corpus should be an inverted index!!!
    baseline = mimno_coherence_ii(sanitize_topic_words(topic_words, corpus), corpus)

    distribution = []
    for i in range(iters):
        rtopic = make_random_topic(topic.items(), len(topic_words))
        rtopic = sanitize_topic_words(rtopic, corpus)
        distribution.append(mimno_coherence_ii(rtopic, corpus))
    return (baseline - np.mean(distribution)) / np.std(distribution)


def sanitize_topic_words(topic, iicorpus):
    words = frozenset(iicorpus.keys())
    topic = [w for w in topic if w in words]
    return topic


def make_random_topic(wcounts, num_words, uniform_distribution=False):
    mutate_uniform = lambda x: 1 if uniform_distribution else x
    # Make the probabilities add up to 1, preserving ratios
    s = sum([mutate_uniform(b) for (a, b) in wcounts])
    l2 = []
    for (a, b) in wcounts:
        l2.append((a, mutate_uniform(b)/s))

    topic = []
    for i in range(num_words):
        # build a fake topic
        r = random.random()
        for (a, b) in l2:
            if r < b:
                topic.append(a)
                break  # we've found the word, now get the next one.
            else:
                r -= b
    return topic
