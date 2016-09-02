import sys

import MySQLdb

try:
    from settings import HOST, USERNAME, PASSWORD
except ImportError:
    print 'Configuration in settings.py incorrect or missing.'
    print 'Please create a settings.py file with the following lines:'
    print 'USERNAME="mysql_username"'
    print 'PASSWORD="mysql_password"'
    print 'HOST="mysql_hostname_or_ip"'
    sys.exit(-1)


class DB(object):

    def __init__(self, db_name):
        self.db = MySQLdb.connect(
            user=USERNAME, passwd=PASSWORD, db=db_name, host=HOST,
            use_unicode=True, charset='utf8')
        self.c = self.db.cursor()

    def perform_sql(self, sql, full_row=False):
        r = self.c.execute(sql)
        if not r:
            return None
        rows = self.c.fetchall()
        if full_row:
            return rows[0]
        else:
            return [row[0] for row in rows]

    def escape_string(self, s):
        return self.db.escape_string(s)
