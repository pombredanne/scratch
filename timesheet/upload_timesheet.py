import csv
import datetime
import itertools
import optparse
import os
import sqlite3
import sys
import time

# TODO
# report showing gaps in hamster hours
# replace vec_round with something more readable


# http://stackoverflow.com/questions/792460/how-to-round-floats-to-integers-while-preserving-their-sum

# Original C version by R. G. Becker 1980
def vec_round(v, s, m, cutoff=2):
    '''
    Given the list of numbers v,
    return a list, r, such that
    sum r[i] == s

    and r = m*v with a small number of deviations
    '''
    n = len(v)
    if not m: return (n*[0])[:]
    vs = 0
    r = []
    for i in v:
        ir = int(i*m+0.5)
        r.append(float(ir/m))
        vs += ir
    if vs==s: return r
    rincr = 1.0/m
    incr = 1
    if vs<s:
        xs = r
        rs = v
    else:
        xs = v
        rs = r
        incr = -incr
        rincr = -rincr

    while vs!=s:
        o = 10*abs(s)                   # infinity
        for i in xrange(n):
            t = float(xs[i]-rs[i])
            if t<=o or r[j] < cutoff:
                if o==t:
                    if abs(v[i])>abs(v[j]): j = i
                else:
                    j = i
                    o = t
        vs += incr
        r[j] += rincr
    return r


def working_week(dt):
    d = dt.date()
    start = d - datetime.timedelta(d.weekday())
    return [(start + datetime.timedelta(i)) for i in range(7)]


class Categories(object):

    def __init__(self, csv_file):
        self._categories = dict((row[0], row[1:]) for row in
                                csv.reader(csv_file))
        self._ignored = set()
        for name, mis_code in self._categories.iteritems():
            if mis_code == ["IGNORE"]:
                self._ignored.add(name)

    def is_ignored(self, name):
        return name in self._ignored

    def mis_code_from_hamster_category(self, name):
        return self._categories[name]


def make_categories(filename):
    return Categories(open(filename))


def sql_query(conn, sql, args=()):
    cur = conn.cursor()
    try:
        cur.execute(sql, args)
        return cur.fetchall()
    finally:
        cur.close()


def get_hamster_stints(start_datetime, end_datetime):
    new_db_filepath = os.path.expanduser(
        "~/.local/share/hamster-applet/hamster.db")
    if os.path.exists(new_db_filepath):
        db_filepath = new_db_filepath
    else:
        db_filepath = os.path.expanduser(
            "~/.gnome2/hamster-applet/hamster.db")
    conn = sqlite3.connect(db_filepath)
    sql = """\
SELECT
  c.name,
  date(f.start_time),
  sum(strftime("%s", f.end_time) - strftime("%s", f.start_time))
FROM
  facts AS f,
  activities AS a,
  categories c
WHERE a.id = f.activity_id
  AND a.category_id = c.id
  AND f.start_time >= ?
  AND f.end_time < ?
GROUP BY c.name, date(f.start_time)
ORDER BY c.name, date(f.start_time)"""
    args = (start_datetime, end_datetime)
    rows = sql_query(conn, sql, args)
    # hack: hamster gives uncategorized facts category_id -1, but that category
    # isn't in the categories table :-(
    unsorted_sql = """\
SELECT
  "Unsorted",
  date(f.start_time),
  sum(strftime("%s", f.end_time) - strftime("%s", f.start_time))
FROM
  facts AS f,
  activities AS a
WHERE a.id = f.activity_id
AND a.category_id = -1
AND f.start_time >= ?
AND f.end_time < ?
GROUP BY date(f.start_time)
ORDER BY date(f.start_time)"""
    unsorted_rows = sql_query(conn, unsorted_sql, args)
    print "Uncategorized hours %r" % unsorted_rows   # TODO: move
    return itertools.groupby(itertools.chain(rows, unsorted_rows),
                             lambda row: row[0])


def date_from_datestamp(text):
    tm = time.strptime(text, "%Y-%m-%d")
    return datetime.date(tm.tm_year, tm.tm_mon, tm.tm_mday)


def vector_add(a, b):
    assert len(a) == len(b), (a, b)
    return [ai + bi for ai, bi in zip(a, b)]


def mis_timesheet_from_hamster_stints(hamster_stints, categories, week):
    monday = week[0]
    mis_timesheet = {}
    missing_categories = set()
    for category, rows in hamster_stints:
        by_day = [0] * len(week)
        if categories.is_ignored(category):
            print "ignoring", list(rows)
            continue
        try:
            mis_code = categories.mis_code_from_hamster_category(category)
        except KeyError:
            missing_categories.add(category)
            continue
        for unused, datestamp, seconds in rows:
            date = date_from_datestamp(datestamp)
            by_day[(date - monday).days] = seconds / 3600.
        total_by_day = mis_timesheet.setdefault(tuple(mis_code),
                                                [0] * len(week))
        total_by_day[:] = vector_add(total_by_day, by_day)
    return mis_timesheet.items(), missing_categories


def fudge(mis_timesheet):
    # fudge uploaded hours so that each is a whole number of quarters of an
    # hour, without changing total hours, and changing each length of time only
    # a small amount
    all_hours = []
    for mis_code, hours in mis_timesheet:
        all_hours.extend(hours)
    m = 4
    all_fudged = [float(v)/m for v in vec_round([h * m for h in all_hours],
                                                int(round(m * sum(all_hours))),
                                                1)]
    fudged = []
    for i in range(0, len(mis_timesheet)):
        fudged_hours = all_fudged[7 * i:7 * i+7]
        mis_code = mis_timesheet[i][0]
        fudged.append((mis_code, fudged_hours))
    return fudged


def total_hours(mis_timesheet):
    total = 0.
    for mis_code, hours in mis_timesheet:
        total += sum(hours)
    return total


def print_timesheet(timesheet):
    for row in sorted(timesheet):
        print row, sum(row[1])


def almost_equal(a, b, places=7):
    return round(abs(a - b), places) == 0


def vector_almost_equal(a, b, places=7):
    assert len(a) == len(b), (a, b)
    return all(almost_equal(ai, bi) for ai, bi in zip(a, b))


def vector_is_zero(a, places=7):
    return vector_almost_equal(a, [0.] * len(a))


def drop_categories_with_zero_hours(timesheet):
    dropped = []
    r = []
    for mis_code, hours in sorted(timesheet):
        if vector_is_zero(hours):
            dropped.append(mis_code)
        else:
            r.append((mis_code, hours))
    return r, dropped


def get_week_start_date(year, week):
    """
    >>> get_week_start_date(2009, 1)
    datetime.datetime(2008, 12, 29)
    >>> get_week_start_date(2010, 1)
    datetime.datetime(2010, 1, 4)
    """
    day_1 = datetime.datetime(year, 1, 1)
    if day_1.isoweekday() > 4: # iso8601, first week is one with first thursday
        week_1 = day_1 + datetime.timedelta(days=8-day_1.isoweekday())
    else:
        week_1 = day_1 - datetime.timedelta(days=day_1.isoweekday()-1)
    return week_1 + datetime.timedelta(weeks=week-1)


import subprocess
import ConfigParser
import tempfile
import pickle


def upload_to_mis(monday, fudged):
    #mvn exec:exec -Dexec.executable="/home/stan/opt/jython2.5.1/jython"
    #-Dexec.args="-J-cp %classpath /home/stan/lpth/timesheet/get_categories.py"
    parser = ConfigParser.SafeConfigParser()
    parser.read(os.path.expanduser("~/.timesheet.conf"))
    temp = tempfile.NamedTemporaryFile()
    try:
        pickle.dump((parser.get("main", "username"), parser.get("main", "password"), monday, fudged), temp,
                    pickle.HIGHEST_PROTOCOL)
        temp.flush()
        cmd = ["mvn", "exec:exec",
            "-Dexec.executable=/home/stan/opt/jython2.5.1/jython",
            "-Dexec.args=-J-cp %%classpath /home/stan/lpth/timesheet/upload.py %s" % temp.name]
        print cmd
        subprocess.check_call(cmd, cwd="/home/stan/1003/htmlunit-2.7")
    finally:
        temp.close()
    

def upload_to_mis_from_hamster(options):
    config_path = "~/.timesheet-categories.csv"
    categories = Categories(open(os.path.expanduser(config_path)))
    today = datetime.datetime.now()
    if options.week:
        if options.weekyear:
            year = options.weekyear
        else:
            year = today.year
        today = get_week_start_date(year, options.week)
    elif options.last_week:
        today = today - datetime.timedelta(days=7)
    week = working_week(today)
    monday, next_monday = week[0], week[-1]
    print "Timesheet for week starting %s" % monday
    hamster_stints = get_hamster_stints(monday, next_monday)
    mis_timesheet, missing_categories = mis_timesheet_from_hamster_stints(
        hamster_stints, categories, week)
    print_timesheet(mis_timesheet)
    fudged, dropped = drop_categories_with_zero_hours(fudge(mis_timesheet))
    print "fudged timesheet"
    print_timesheet(fudged)
    print "unfudged total hours", total_hours(mis_timesheet)
    print "fudged total hours", total_hours(fudged)
    if missing_categories:
        print ("Missing category, omitted from timesheet (listed in the form "
               "of suggested %s entries):" % config_path)
        for category in missing_categories:
            print "%s,%s,SOFTWARE,3RDLINESUP" % (category, category)
    for mis_code in dropped:
        print "dropped (0 hours after fudging): %s" % (mis_code,)
    if options.upload:
        upload_to_mis(monday, fudged)


def parse_options(argv):
    parser = optparse.OptionParser()
    parser.add_option("--upload", action="store_true", default=False)
    parser.add_option("--last-week", action="store_true", default=False)
    parser.add_option("--week", type="int", help="Week number to use")
    parser.add_option("--weekyear", type="int",
                      help="Year week number specified via --week is in")
    options, args = parser.parse_args(argv[1:])
    return options


def main(argv):
    options = parse_options(argv)
    upload_to_mis_from_hamster(options)


if __name__ == "__main__":
    main(sys.argv)
