import pandas as pd
import numpy as np
import re
import co_occurrence_metric as ccmetrics
from scipy.stats import spearmanr
from read_topics import read_in_topics
from helpers import *

# read in the precomputed topic scores
ground_truth = pd.read_csv("mturk_questions.csv")

# load in the corpus
corpus, wcounts = ccmetrics.load_corpus("<<<CORPUS>>>")
iicorpus = inverted_index(corpus)

# we only want to look at the ERC topics
z = ground_truth["Topic ID"]
z = [True if x.find("real") != -1 else False for x in z]
ground_truth = ground_truth.loc[z, :]

topic_dists = read_in_topics()

scores = []
pnmi_scores = []
total = len(ground_truth["Topic ID"])
for i in ground_truth["Topic ID"]:
    # get the topic words with that name
    twords = ground_truth.loc[ground_truth["Topic ID"] == i, "Top 20 Words"]
    twords = twords.values[0].split(", ")
    v = ccmetrics.test_individual_topic(twords, topic_dists[i], iicorpus)
    scores.append(v)
    v = ccmetrics.pnmi_ii(twords, iicorpus)
    pnmi_scores.append(v)
    # 
    # if len(scores) % 10 == 0:
    print("Processed %d/%d" % (len(scores), total))

ground_truth["Wallach_zscores"] = pd.Series(scores)
ground_truth["PNMI_Scores"] = pd.Series(pnmi_scores)

# now calculate the HHI based on the words
z = ground_truth["Topic ID"]
hhis = [compute_hhi(topic_dists[x].items()) for x in z]
ground_truth["Topic HHI"] = pd.Series(hhis)


# now we make a new Topic Size metric
z = ground_truth["Topic ID"]
sizes = [sum([y for (x, y) in topic_dists[i].items()]) for i in z]
ground_truth["Topic Size"] = sizes

print("No senses...")
# calculate the no. senses
z = ground_truth["Topic ID"]
no_senses = [no_senses(topic_dists[x]) for x in z]
ground_truth["No Senses"] = pd.Series(no_senses)

print("Avg JC")
# calculate the no. senses
z = ground_truth["Topic ID"]
ajc = [jiang_conrath_ds(topic_dists[x]) for x in z]
ajc = pd.Series(ajc)
ajc[ajc > 1.0] = 1
ground_truth["Avg Jiang Conrath"] = ajc

ground_truth.to_csv(open("output.csv", "w"))

