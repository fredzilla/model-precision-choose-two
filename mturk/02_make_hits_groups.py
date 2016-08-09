import sys
from math import ceil
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import *
from boto.mturk.price import Price
from boto.mturk.qualification import *
from datetime import timedelta
from collections import defaultdict
from random import shuffle, sample
import csv

# ------------- Some Boilerplate
DESC = """You will be shown six words. 
Four of these words belong together, and two of them do not.
<h2>Check two words that do <u>NOT</u> belong in the group.</h2>"""

# form overview boilerplate
overview = Overview()
overview.append_field('Title', 'Word Intrusion')
overview.append(FormattedContent(DESC))

# ------------- Log In to MTurk -------------
ACCESS_ID = ''
SECRET_KEY = ''
HOST = 'mechanicalturk.amazonaws.com'
 
mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                      aws_secret_access_key=SECRET_KEY,
                      host=HOST)

try:
    done_ids = frozenset(open("already_tested_ids.txt").read().split("\n"))
except IOError:
    done_ids = set()

# build the qualification
all_questions = []

#open the topic file
fin = csv.DictReader(open("out.aux.csv", 'rU'))
bins = defaultdict(list)
for row in fin:
    tid = row["ID"]
    if tid in done_ids:
        continue
    words = [row["Word %d" % (i + 1)] for i in range(6)]
    words = ", ".join(words)
    answer_arry = [(row["Word %d" % (i + 1)], "Word %d" % (i + 1)) for i in range(6)]
    topicanswers = SelectionAnswer(selections=answer_arry, 
        min=2, 
        max=2,
        style='checkbox')
    aspec = AnswerSpecification(topicanswers)

    qual_ques1 = QuestionContent()
    # qual_ques1.append(FormattedContent("<p>Choose words that <u>do not belong</u>.</p>"))
    qual_ques1.append(FormattedContent("<h3>%s</h3>" % words))
    q = Question(identifier=tid, content=qual_ques1, answer_spec=aspec, is_required=True)
    all_questions.append(q)

shuffle(all_questions)
print(len(all_questions))

num_posted = 0
for i in range(int(ceil(len(all_questions) / 10.0))):
    form = QuestionForm()
    form.append(overview)
    qs = all_questions[i*10: (i+1) * 10]
    form += qs

    c = mtc.create_hit(questions=form, max_assignments=10, # qualifications=qualifications,
                       reward=Price(amount=0.20, currency_code='USD'), duration=timedelta(7),
                       keywords=['word', 'topic', 'text', 'choice', 'group'],
                       title="Word Intrusion", description=DESC)
    print(c[0].HITId)
    num_posted += 1
