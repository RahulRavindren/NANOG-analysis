import pycha.line
import cairo
import math
from stats_common import *

con = db_connection()
curs = con.cursor()
curs.execute("set names utf8")

def process_freq_posters(rows, name):
	data = []
	idx = 0
	print
	print name
	print "------------------------"
	for row in rows:
		data.append((idx, math.log10(row[1])))
		idx += 1
		print "%s		%s" % row
	generate_chart(data, name)

# Most frequent posters
curs.execute("select fromcname, count(*) as a from mail group by fromcname order by a desc")
process_freq_posters(curs.fetchall(), "Freq_Posters")

# Most frequent posters of new messages
curs.execute("select fromcname, count(*) as a from mail where inreplyto is null group by fromcname order by a desc")
process_freq_posters(curs.fetchall(), "Freq_Posters_New")

# Most frequent posters of replies
curs.execute("select fromcname, count(*) as a from mail where inreplyto is not null group by fromcname order by a desc")
process_freq_posters(curs.fetchall(), "Freq_Posters_Reply")

def process_msg_month(rows, name):
	data = []	
	for i in range(0, len(rows)):
		#label = int("%d%02d" % (row[0], row[1]))
		data.append((i, rows[i][2]))
	generate_chart(data, name)
	
# Messages per month
curs.execute("select year(sent) as y, month(sent) as m, count(*) from mail group by y, m")
process_msg_month(curs.fetchall(), "Msg_Month")

# New posts per month
curs.execute("select year(sent) as y, month(sent) as m, count(*) from mail where inreplyto is null group by y, m")
new_posts = curs.fetchall()
process_msg_month(new_posts, "Msg_Month_New")

# Replies per month
curs.execute("select year(sent) as y, month(sent) as m, count(*) from mail where inreplyto is not null group by y, m")
reply_posts = curs.fetchall()
process_msg_month(reply_posts, "Msg_Month_Reply")

# Replies to new posts ratio
rows = []
for i in range(0, len(new_posts)):
	rows.append([new_posts[i][0], new_posts[i][1], reply_posts[i][2]/new_posts[i][2]])
process_msg_month(rows, "Msg_Month_Ratio")

curs.close()
con.close()
