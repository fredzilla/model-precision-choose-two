from glob import glob
from collections import defaultdict, Counter
from gzip import GzipFile

# files = glob("../topics/NYT_topics/*.state.gz")
files = glob("../news_corpus/mallet_out/*.state.gz")


def read_in_topics(all_files=files):
    topic_word_distributions = {}

    for file in all_files:
        topic_type = "NYT" if file.find("NYT_topics") != -1 else "real"
        reader = GzipFile(file, "r")

        pdists = defaultdict(lambda: Counter())

        line = "firstgo"
        while len(line) > 0:
            line = reader.readline()
            line = line.decode('utf-8')
            # print(file, line, len(line))
            if len(line) == 0 or line[0] == "#":
                continue
            parts = line.strip().split(" ")
            topic = int(parts[-1]) + 1  # The raw files save as 0-based, we want 1-based.
            wtype = parts[-2]
            pdists[topic][wtype] += 1

        num_topics = len(pdists.keys())

        for topic, dist in pdists.items():
            key = "%s_%d_of_%d" % (topic_type, topic, num_topics)
            topic_word_distributions[key] = dist

    return topic_word_distributions