# Parses and saves individual messages from NANOG legacy archives
import MySQLdb
import datetime

_con = None
_curs = None
_debug = False
_insert = True

# Setup database connectivity
def process_msg_setup():
	global _con, _curs
	_con = MySQLdb.connect(host='127.0.0.1', port=3306,
                    user='root', passwd='dballz',
                    use_unicode=1, charset='utf8', db='nanogmail')
	_curs = _con.cursor()
	_curs.execute("set names utf8")
# Close database connection
def process_msg_teardown():
	global _con, _curs
	_curs.close()
	_con.close()

def set_debug(s_debug):
	global _debug
	_debug = s_debug

def set_insert(s_insert):
	global _insert
	_insert = s_insert

# For each message, first extract data from the header, which
# provides subject, date, message id and
# reference id (in-reply-to). Header is of the form, with
# potentially multiple references.
# <!-- MHonArc v2.5.11 -->
# <!--X-Subject: Re: SYN spoofing -->
# <!--X-From-R13: "oelna f. oynax" <oelnaNfhcrearg.arg> -->
# <!--X-Date: Wed, 28 Jul 1999 14:06:37 &#45;0400 (EDT) -->
# <!--X-Message-Id: 199907281554.LAA15425@supernet.net -->
# <!--X-Content-Type: text/plain -->
# <!--X-Reference: 379F1FFF.7229F1DE@senie.com -->
# <!--X-Head-End-->

def process_msg(msg_html, msg_seq=-1):
	msg_html.readline() # MHonArc

	line = msg_html.readline() # X-Subject
	msg_subject = line[15:-4]
	msg_html.readline() # X-From-R13
	msg_html.readline() # X-Date

	line = msg_html.readline() # X-Message-Id
	msg_id = line[18:-5]

	# Find references, which may be multiple
	msg_ref_ids = []
	while line:
		line = msg_html.readline()
		if line.startswith("<!--X-Reference:"):
			msg_ref_ids.append(line[17:-5])
		elif line.startswith("<!--X-Head-End"):
			break
	if len(msg_ref_ids) == 0:
		msg_ref_ids.append(None)

	# Read from and date
	# From: text up to end of line following <EM>From:</EM>,
	# this is a name with no from-email available.
	while line:
		line = msg_html.readline()
		if line.startswith("<LI><EM>From:</EM>"):
			msg_from = line[18:].strip() # From
			break

	# Date: text up to end of line following <EM>Date:</EM>,
	# of the format Sat May 29 01:24:26 1999
	while line:
		line = msg_html.readline()
		if line.startswith("<LI><EM>Date:</EM>"):
			msg_date_str = line[18:].strip()
			msg_date = datetime.datetime.strptime(msg_date_str,
												"%a %b %d %H:%M:%S %Y")
			break

	# Read body text, between <!--X-Body-of-Message--> and
	# <!--X-Body-of-Message-End--> markers
	msg_text = ""
	text_end = False
	while line:
		line = msg_html.readline()
		if line.startswith("<!--X-Body-of-Message-->"):
			msg_text += line[24:]
			while line:
				line = msg_html.readline()
				if line.endswith("<!--X-Body-of-Message-End-->\n"):
					msg_text += line[:-29]
					text_end = True
					break
				msg_text += line
		if text_end:
			# Break out of the loop, no more parsing needed
			break

	if _debug:
		print "Message: %d" % (msg_seq)
		print "Subject: %s" % msg_subject
		print "ID: %s" % msg_id
		print "Ref: %s" % msg_ref_ids
		print "From: %s" % msg_from
		print "Date: %s" % msg_date.isoformat()
		#print msg_text
		print

	if _insert:
		# Now insert into db, assume msg_ref_ids[0] is message being
		# responded to. Have to make this assumption, since there is no
		# in-reply-to header; but there's typically only one reference, so
		# this shouldn't be a big deal.
		_curs.execute("""insert into mail
			(fromemail, fromname, fromcname, sent, messageid, subject, inreplyto, body, legacy)
		values ("", %s, %s, %s, %s, %s, %s, %s)""",
			(msg_from, msg_from, msg_date.strftime("%Y-%m-%d %H:%M:%S"),msg_id,msg_subject, msg_ref_ids[-1], msg_text, True))
		for msg_ref_id in msg_ref_ids:
			if msg_ref_id is not None:
				_curs.execute("""insert into refs values (%s, %s, %s)""",
					(msg_id, msg_ref_id, True))
		_con.commit()
