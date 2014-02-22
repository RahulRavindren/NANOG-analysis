import urllib2
import os
import codecs
import StringIO
from parse_nanog_legacy_archives import

# Setup database connectivity
process_msg_setup()

# Old archives are scraped from MERIT site at:
base_url = "http://www.nanog.org/mailinglist/mailarchives/old_archive/"

# Message IDs must include both the year-month ("1999-05") as well as
# a 5 digit message sequence number ("00017").
# Messages can be scraped by constructing URLs of the form:
# base_url + year-month + "msg" + id + ".html"
# starting from 1994-05, ending at 2008-12.
# For each year-month, keep getting messages with ascending IDs until
# a HTTP 404 is returned, i.e., no more messages for that month.

for year in range(1994, 2008+1):
	for month in range (1, 12+1):
		year_month = "%s-%02d/" % (year, month)
		print "* Retrieving for %s" % year_month
		year_month_base = base_url + year_month
		http404 = False
		msg_seq = 0

		# Just keep looking for messages by msg_seq until a 404
		while not http404:
			msg_url = year_month_base + "msg%05d.html" % msg_seq
			try:
				msg_html_url = urllib2.urlopen(msg_url)
			except urllib2.HTTPError as e:
				if e.code == 404:
					http404 = True
					print "--- Captured %d messages" % msg_seq
					break
				else:
					print "***** HTTP Error!!!!!"
					print e
					sys.exit(-1)

			# Wrap the text from the URL in a StringIO object
			# so that it can be read twice: once to write the file
			# and a second time to parse the data. Encode it, stripping
			# out the occasional weird unicode characters that cause problems.
			enc_msg_html = unicode(msg_html_url.read(), errors="ignore")
			msg_html = StringIO.StringIO(enc_msg_html)

			if msg_seq == 0:
				# Make year_month directory on the first message found
				_dir_path = "legacy-data-raw/%s" % year_month
				if not os.path.exists(_dir_path):
					os.makedirs(_dir_path)

			# Save file in year_month directory
			_file_path = "%smsg%05d.html" % (_dir_path, msg_seq)
			_file = codecs.open(_file_path, "w", "utf-8")
			_file.write(msg_html.read())
			_file.close()

			# Reset the msg_html string file
			msg_html.seek(0)

			# Parse and save the message
			process_msg(msg_html, msg_seq)

			msg_seq += 1

# Tear down database connection
process_msg_teardown()
