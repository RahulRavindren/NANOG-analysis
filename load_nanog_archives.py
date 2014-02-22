import MySQLdb
import datetime
import re
import sys

import warnings
warnings.simplefilter("error")

con=MySQLdb.connect(host='127.0.0.1', port=3306,
                    user='root', passwd='dballz',
                    use_unicode=1, charset='utf8', db='nanogmail')
curs=con.cursor()
curs.execute("set names utf8")

# Precompile regex to match label opening message headers
# From kch670 at eecs.northwestern.edu  Wed Apr  1 08:30:31 2009
label_re = re.compile("^From [^ ]* at [^ ]*  (Mon|Tue|Wed|Thu|Fri|Sat|Sun) " \
				+ "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) " \
				+ "[ 0123][0-9] [0-2][0-9]:[0-5][0-9]:[0-5][0-9] " \
				+ "2[0-9][0-9][0-9]\n$")

for year in range(2009, 2012+1):
	for month in ("January", "February", "March", "April", "May", "June",
			"July", "August", "September", "October", "November", "December"):
		msg_data_file = "current-data/%s-%s.txt" % (year, month)
		try:
			print "* Parsing file: %s" % msg_data_file
			msg_data = open(msg_data_file)
		except:
			print "--- No file found: %s" % msg_data_file
			continue

		# Message headers start with a labeling line, followed by
		# a series of headers, which always end with a Message-ID header.
		# Here's an example:
		# From kch670 at eecs.northwestern.edu  Wed Apr  1 08:30:31 2009
		# From: kch670 at eecs.northwestern.edu (Kai Chen)
		# Date: Wed, 1 Apr 2009 08:30:31 -0500
		# Subject: Can you see these AS links:)
		# In-Reply-To: <E51CFA60-C0B1-4C43-932E-BF8DEF74F788@cs.ucla.edu>
		# References: <e81393830903311956j16861409n90bbeb78249946e7@mail.gmail.com>
		# 	<E51CFA60-C0B1-4C43-932E-BF8DEF74F788@cs.ucla.edu>
		# Message-ID: <e81393830904010630q34853c0el5c4cc5090c9df815@mail.gmail.com>

		# Assume we're starting with a label + headers,
		line = msg_data.readline() # Clear past the label

		while line:
			# Read From header
			from_data = msg_data.readline()[6:]
			from_data_elements = from_data.split(" ", 3)
			msg_from_email = "%s@%s" % (from_data_elements[0],
										from_data_elements[2])
			msg_from_name = from_data_elements[3][1:-2] # Strip brackets

			# Read Date header
			date_str = msg_data.readline()[6:] # Strip header
			if date_str.find(", ") != -1: # Strip day name if present
				date_str = date_str[5:]
			date_str = date_str[:date_str.rfind(":")+3] # Strip timezone
			msg_date = datetime.datetime.strptime(date_str,"%d %b %Y %H:%M:%S")

			# Read Subject header, may span multiple lines
			msg_subject = msg_data.readline()[9:-1]
			line = msg_data.readline()
			while not line.startswith("In-Reply-To:") \
				and not line.startswith("References:") \
				and not line.startswith("Message-ID:"):
				msg_subject += line[:-1]
				line = msg_data.readline()

			# Try to read In-Reply-To and References headers if present, and then
			# the Message-ID header which is always present

			# Some In-Reply-To headers are corrupted with additional
			# text and extra lines
			msg_in_reply_to = None
			if line.startswith("In-Reply-To:"):
				msg_in_reply_to = line[14:line.rfind(">")]
				line = msg_data.readline()
			# Bypass extra junk lines, if any
			while not line.startswith("References:") \
				and not line.startswith("Message-ID:"):
				line = msg_data.readline()

			# References may span multiple lines,
			# may have multiple references per line.
			msg_ref_ids = []
			if line.startswith("References:"):
				line = line[12:]
				ref_ids = line
				line = msg_data.readline()
				while not line.startswith("Message-ID:"):
					ref_ids += line
					line = msg_data.readline()
				msg_ref_ids = ref_ids.replace("<", " ").replace(">", " ").split()

			# If msg_in_reply_to is not in msg_ref_ids, push it in
			# Also, in case msg_in_reply_to is None, populate it with
			# the last of the msg_ref_ids.
			if msg_in_reply_to:
				if msg_in_reply_to not in msg_ref_ids:
					msg_ref_ids.append(msg_in_reply_to)
			elif len(msg_ref_ids):
				msg_in_reply_to = msg_ref_ids[-1]

			# Now get the Message-ID
			# Bypass extra junk lines, if any
			while not line.startswith("Message-ID:"):
				line = msg_data.readline()
			msg_id = line[12:][1:-2]

			# And finally, the message body text.
			# Use regex to match a label line to detect body end.
			# Body end may also occur at EOF
			msg_text = ""
			line = msg_data.readline() # Move past Message-ID
			while line and not label_re.match(line):
				msg_text += line
				line = msg_data.readline()

			"""
			print "Subject: %s" % msg_subject
			print "ID: %s" % msg_id
			print "In_reply_to: %s" % msg_in_reply_to
			print "Ref: %s" % msg_ref_ids
			print "From_email: %s" % msg_from_email
			print "From_name: %s" % msg_from_name
			print "Date: %s" % msg_date.isoformat()
			print
			print msg_text
			print
			"""

			# Now insert into db, assume msg_ref_ids[0] is message being
			# responded to. Have to make this assumption, since there is no
			# in-reply-to header; but there's typically only one reference, so
			# this shouldn't be a big deal.
			curs.execute("""insert into mail
				(fromemail, fromname, fromcname, sent, messageid, subject, inreplyto, body, legacy)
				values (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
				(msg_from_email, msg_from_name, msg_from_name,
				msg_date.strftime("%Y-%m-%d %H:%M:%S"),
				msg_id,	msg_subject, msg_in_reply_to, msg_text, False))
			for msg_ref_id in msg_ref_ids:
				curs.execute("""insert into refs values (%s, %s, %s)""",
					(msg_id, msg_ref_id, False))

			con.commit()
