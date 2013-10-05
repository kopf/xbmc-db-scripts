from db import DB

videos_db = DB('myvideos75')
music_db = DB('mymusic32')


def perform_fix(db, table, column, rows=None, distinct=False):
    print 'Fixing column {0} in table {1}...'.format(column, table)
    if rows is None:
        if distinct:
            sql = 'select distinct '
        else:
            sql = 'select '
        sql += '{0} from {1};'.format(column, table)
        rows = db.perform_sql(sql)
    sql = "update {table} set `{column}`='{new}' where `{column}`='{old}';"
    for row in rows:
        old_value = row.replace('\\', '\\\\').replace("'", "\\'")
        db.perform_sql(sql.format(
            table=table, column=column,
            new=old_value.replace('\\\\\\\\', 'smb://').replace('\\\\', '/'),
            old=old_value))


if __name__ == '__main__':
    VIDEOS_FIXES = [
        # List of (table, column) tuples to be fixed
        ('movieview', 'strPath'),
        ('episodeview', 'strPath'),
        ('movieview', 'c22'),
        ('episodeview', 'strShowPath'),
        ('episode', 'c18'),
        ('path', 'strPath'),
        ('tvshow', 'c16'),
        ('tvshowview', 'strPath')
    ]
    for entry in VIDEOS_FIXES:
        perform_fix(videos_db, entry[0], entry[1])
    rows = videos_db.perform_sql('select strFileName from movieview where strFileName like "stack://\\\\\\\\%";')
    perform_fix(videos_db, 'movieview', 'strFileName', rows=rows)

    perform_fix(music_db, 'songview', 'strPath', distinct=True)
    perform_fix(music_db, 'path', 'strPath', distinct=True)
