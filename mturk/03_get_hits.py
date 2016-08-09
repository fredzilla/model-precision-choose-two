from boto.mturk.connection import MTurkConnection
import csv

# ------------- Log In to MTurk -------------
ACCESS_ID = ''
SECRET_KEY = ''
HOST = 'mechanicalturk.amazonaws.com'

# ------------- Establish a Connection -------------
mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                      aws_secret_access_key=SECRET_KEY,
                      host=HOST)

# get the list of all available IDs
id_file = open("hit_ids_aux.txt").read().split("\n")
id_file = frozenset(id_file)

# build the header for the CSV
header = ['HIT ID', 'Worker ID', 'Status', 'Response Time', 'Approval Time', 'Question ID', 'Answer']

outfile = csv.writer(open("mturk_answers_aux.csv", 'w'), quoting=csv.QUOTE_ALL)
outfile.writerow(header)

hits = mtc.get_all_hits()
hits = [h for h in hits if h.HITId in id_file]
for h in hits:
    responses = mtc.get_assignments(h.HITId)
    for response in responses:
        try:
            at = response.ApprovalTime
        except:
            at = "N/A"
        if response.AssignmentStatus == 'Approved':
            for answer in response.answers[0]:
                # row += [answer.qid, answer.fields[0] if len(answer.fields) > 0 else "NO ANSWER"]
                row = [response.HITId, response.WorkerId, response.AssignmentStatus, response.SubmitTime, at]
                row += [answer.qid, ",".join(answer.fields) if len(answer.fields) > 0 else "NO ANSWER"]
                outfile.writerow(row)

