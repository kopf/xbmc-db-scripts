import sys

import _mysql

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
        self.db=_mysql.connect(host=HOST, user=USERNAME,
                               passwd=PASSWORD, db=db_name)

    def perform_sql(self, sql, full_row=False):
        self.db.query(sql)
        r = self.db.store_result()
        if not r:
            return None
        if full_row:
            return r.fetch_row(maxrows=0)
        else:
            return [x[0] for x in r.fetch_row(maxrows=0)]

    def escape_string(self, s):
        return self.db.escape_string(s)
