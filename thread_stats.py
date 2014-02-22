# Some mailers obviously do not respect in-reply-to or references headers!
# Or, the NANOG archive is just screwed up. Either way, have to compensate,
# need to use subject for matching threads instead of refs.

import sys
import math
from stats_common import *

con = db_connection()
curs = con.cursor()

# Threads by number of messages
sys.stderr.write("Finding threads by message count...")
thread_size = {}
curs.execute("select subject, count(*) as a from mail group by subject order by a")
rows = curs.fetchall()
for row in rows:
	subject, count = row
	subject = subject.replace("[", " ").replace("]", " ")
	subject = subject.replace("re:", " ").replace("RE:", " ").replace("Re:", " ")
	subject = subject.strip()
	
	if subject not in thread_size:
		thread_size[subject] = 0
	thread_size[subject] = thread_size[subject] + count

sorted_thread_size = sorted(thread_size.iteritems(), key=lambda t: t[1])

msgs_by_size = {}
top_msg_data = []
for d in sorted_thread_size:
	print "[%s]	%s" % d
	
	if d[1] not in msgs_by_size:
		msgs_by_size[d[1]] = 0
	msgs_by_size[d[1]] += 1
	
	if d[1] >= 100:
		curs.execute("""select subject, fromcname, min(sent) from mail
						where subject=%s""", d[0])
		r = curs.fetchone()
		top_msg_data.append([r[0], r[1], r[2], d[1]])

print
print
print "------------ Top Message Info -------------"
for d in top_msg_data:
	print d[0]
	print "	%d	%s		%s" % (d[3], d[1], d[2])

print
print
print "---------------- Messages by size ---------------"
print "Replies	Message Count"
print "-------	-------------"

s_msgs_by_size = sorted(msgs_by_size.iteritems())
for d in s_msgs_by_size:
	print "%s	%s" % d
generate_chart([(math.log10(r[0]), math.log10(r[1])) for r in s_msgs_by_size], "Msgs_By_Thread_Size")
		

# Threads by number of participants
sys.stderr.write("Finding threads by participants...")
thread_users = {}
curs.execute("select subject, fromcname from mail group by subject, fromcname")
rows = curs.fetchall()
for row in rows:
	subject, user = row
	subject = subject.replace("[", " ").replace("]", " ")
	subject = subject.replace("re:", " ").replace("RE:", " ").replace("Re:", " ")
	subject = subject.strip()
	
	if subject not in thread_users:
		thread_users[subject] = set()
	thread_users[subject].add(user)

sorted_thread_users = sorted(thread_users.iteritems(), key=lambda t: len(t[1]))

print
print

msgs_by_users = {}
for d in sorted_thread_users:
	user_count = len(d[1])
	print "[%s]	%s" % (d[0], user_count)
	
	if user_count not in msgs_by_users:
		msgs_by_users[user_count] = 0
	msgs_by_users[user_count] += 1

print
print
print "---------------- Messages by size ---------------"
print "Participants	Message Count"
print "------------	-------------"

s_msgs_by_users = sorted(msgs_by_users.iteritems())
for d in s_msgs_by_users:
	print "%s	%s" % d
generate_chart([(math.log10(r[0]), math.log10(r[1])) for r in s_msgs_by_users], "Msgs_By_Thread_Users")

curs.close()
con.close()
