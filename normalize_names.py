# Normalizes aliases; same person may have slightly different names
# Write the output of this file to "match_names.py", to be used by
# fix_names.py to fix aliases.
import MySQLdb
import sys

con=MySQLdb.connect(host='127.0.0.1', port=3306,
                    user='root',passwd='dballz',
                    use_unicode=1, charset='utf8', db='nanogmail')
curs=con.cursor()
curs.execute("set names utf8")

# Fix names using standard rules:
# - Strip non-alphabet characters
# - Lowercase everything
curs.execute("select distinct fromname from mail")
names = curs.fetchall()
sys.stderr.write("Names to processed: %d\n" % len(names))

n_names = [] # Normalized names
n_names_map = {} # Map normalized name to original name(s)

f = ''.join(c for c in map(chr, range(256)) if not c.isalpha())
for name in names:

	n_name = str(name[0]).translate(None, f).lower()
	if not n_name in n_names_map:
		n_names_map[n_name] = []
	n_names_map[n_name].append(name)
	if len(n_name) > 0: # Ignore anything that's only non-alpha chars
		n_names.append(n_name)

sys.stderr.write("Normalized names: %d\n" % len(n_names))

# For a given name, find other names that start or end with that name
match_names = {}
for i in range(len(n_names)):
	sys.stderr.write("Matching %d...\n" % i)
	c_name = n_names[i]
	if c_name is None:
		continue

	if len(c_name) > 7: # Avoid strings that are just first name
		for j in range(len(n_names)):
			if j != i:
				d_name = n_names[j]
				if d_name is None:
					continue

				# Look for names as suffix or prefix, or names which match
				# 5 letters on either end, i.e., matching first name/last name
				# with a middle name or initial.
				if d_name.startswith(c_name) or d_name.endswith(c_name) \
				or d_name.startswith(c_name[:5]) and d_name.endswith(c_name[-5:]):
					if not c_name in match_names:
						# May need to match original variants of c_name which
						# reduce to the same normalized string
						match_names[c_name] = [c_name]
						# Since there are matches, make sure we don't match
						# on c_name again
						n_names[i] = None
					if not d_name in match_names[c_name]:
						match_names[c_name].append(d_name)
						# Make sure we don't process matches again
						n_names[j] = None

# Remove known duds - all eyeballed to find improper matches
#match_names.pop("systemsengineer")
match_names.pop("mailinglist")
match_names.pop("nanogmaillist")
match_names.pop("nanogmailinglist")
match_names.pop("administrator")
match_names.pop("systemadministrator")
match_names.pop("networkadministrator")
match_names.pop("networkeducationcenter")
match_names.pop("listslists")
match_names.pop("christopher")
match_names.pop("frederic")
match_names.pop("thornton")
match_names.pop("ferguson")
match_names.pop("listuser")
match_names.pop("benjamin")
match_names.pop("michaelg")
match_names.pop("hostmaster")
match_names.pop("christian")
match_names.pop("jeremiah")
match_names.pop("christoph")
match_names.pop("williamc")
match_names.pop("anderson")
match_names.pop("jonathan")
match_names.pop("webmaster")
match_names.pop("listnanog")
match_names.pop("listadminaccount")
match_names.pop("variable")
match_names.pop("operations")
match_names.pop("michaels")
match_names.pop("andyjohnson") # Matched randyjohnson
match_names.pop("danielkarrenberg") # Matched danielschauenberg
match_names.pop("scottgardneranderson") # Matched scottpatterson
match_names.pop("chrishall") # Matched chrishallman
match_names["davidhholtzman"].remove("davidwaitzman")

# Add known extra matches
match_names["bmanning"].append("williammanning")
match_names["bmanning"].append("billmanning")
match_names["Yakov Rekhter"] = ["Yakov Rekhter", "yakov"]

"""
match_names["joshuaklubi"].append("joshuawilliamklubi")
match_names["craiglabovit"].append("labovit")
match_names["christopherlmorrow"] = ["christopherlmorrow", "christophermorrow", "chrislmorrow"]
match_names["paulvixie"] = ["paulvixie", "paulavixie"]
match_names["nstratton"].append("nathanastratton")
match_names["richardasteenbergen"] = ["richardasteenbergen", "richardsteenbergen"]
"""

sys.stderr.write("Found %d unique names\n" % len(match_names))

print "match_names = {"
for name in match_names:
	print "'%s' : " % name
	print match_names[name]
	print ","
print "}"
