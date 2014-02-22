from stats_common import *

con = db_connection()
curs = con.cursor()

"""
Run manually to get data into intermediate tables.

drop table user_msg_year;
create table user_msg_year (fromcname varchar(100), year int, count int);
insert into user_msg_year select fromcname, year(sent) as y, count(*) from mail group by fromcname, y;

drop table user_thread_year;
create table user_thread_year (fromcname varchar(100), year int, count int);
insert into user_thread_year select fromcname, year(sent) as y, count(distinct subject) from mail group by fromcname, y;

"""

users_by_years = {}

def find_users_by_years(c):
	curs.execute("""select fromcname, count(*) as c from user_msg_year
					where count >= %d
					group by fromcname order by c""" % c)
	rows = curs.fetchall()
	for row in rows:
		user, year_count = row
		if year_count not in users_by_years:
			users_by_years[year_count] = {}
		if c not in users_by_years[year_count]:
			users_by_years[year_count][c] = []
		users_by_years[year_count][c].append(user)

find_users_by_years(20)
find_users_by_years(10)
find_users_by_years(5)
find_users_by_years(0)

year_counts = sorted(users_by_years.iteritems(), key=lambda k: k[0])
for year_count in year_counts:
	counts = ""
	for c in sorted(year_count[1].keys()):
		counts += "	%d" % len(year_count[1][c])
	print "%d	%s" % (year_count[0], counts)
	
