# Fixes normalized aliases from hand-sanitized output of normalize_names.py
import MySQLdb
import sys
import time
from match_names import match_names # Hand-sanitized output from normalize_names.py

con=MySQLdb.connect(host='127.0.0.1', port=3306,
                    user='root', passwd='dballz',
                    use_unicode=1, charset='utf8', db='nanogmail')
curs=con.cursor()
curs.execute("set names utf8")

"""
# Temporary code to copy fromname to fromcname
curs.execute("select distinct fromname from mail where fromcname is null")
names = curs.fetchall()
print "Fixing %d names... " % len(names)
i = 1
for name in names:
	upd_name = name[0]
	#upd_name = upd_name.replace("'", "\\'")
	print "%d: update %s" % (i, upd_name)

	# Copy from fromname to fromcname

	curs.execute("update mail set fromcname=%s where fromname=%s",
					(upd_name, upd_name))
	con.commit()

	if i % 500 == 0:
		print "Sleeping..."
		time.sleep(120)

	i += 1

sys.exit(-1)
"""

# Fix names using standard rules:
# - Strip non-alphabet characters
# - Lowercase everything
curs.execute("select distinct fromname from mail")
names = curs.fetchall()

print "Normalizing %d names... " % len(names)

# Map normalized name to original name(s)
n_names_map = {}

i = 1
upd_sql = ""
f = ''.join(c for c in map(chr, range(256)) if not c.isalpha())
for name in names:
	n_name = str(name[0]).translate(None, f).lower()
	if n_name not in n_names_map:
		n_names_map[n_name] = []
	n_names_map[n_name].append(name[0])
	i += 1

print "Updating %d aliases..." % len(match_names)

# Update aliases for rows
i = 1
for name in match_names:
	alias = n_names_map[name][0] # Default to first match as alias
	from_names = ""
	comma = ""

	print "%d: Updating %s alias %s" % (i, name, alias)
	print match_names[name]

	for match_name in match_names[name]:
		# Get the original names for a given match
		o_names_match = n_names_map[match_name]
		for o_name_match in o_names_match:
			curs.execute("update mail set fromcname=%s where fromname=%s",
							(alias, o_name_match))
		con.commit()

	i += 1
