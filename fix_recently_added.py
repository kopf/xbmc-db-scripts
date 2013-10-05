#!/usr/bin/env python

import os
import sys

from db import DB

####################################

EXCLUDE = ['directories_to_exclude']

REPLACEMENTS = {
    # Escaped list of replacements for the path string. 
    # Necessary if your files are shared over SMB or some other network share,
    # so that this script can figure out the local filesystem location of the
    # directory and get its creation date.
    #
    # If your XBMC is not accessing files over a share, remove the next line.
    'smb://192.168.92.20/': 'G:\\'
}

####################################


def execute():
    print 'Connecting to MySQL...'
    db = DB('mymusic32')
    print 'Loading data...'
    paths = db.perform_sql('select distinct(strPath) from songview;')
    print 'Scanning dirs...'
    dirs = []
    for path in paths:
        for key, value in REPLACEMENTS.iteritems():
            local_path = path.replace(key, value)
        if not any(directory in path for directory in EXCLUDE):
            try:
                dirs.append({'time': os.path.getctime(local_path),
                             'orig_path': path})
            except Exception:
                pass
    dirs = sorted(dirs, key=lambda k: k['time'])

    i = 0
    start_id = int(db.perform_sql(
        'SELECT idAlbum from songview ORDER BY idAlbum DESC LIMIT 1;')[0])
    print 'Beginning to re-order album IDs, beginning with idAlbum={0}'.format(start_id + 1)
    for directory in dirs:
        i += 1
        new_id = start_id + i
        strPath = db.escape_string(directory['orig_path'])
        sql = 'select idAlbum from songview where strPath="{0}";'
        strPath_album_ids = db.perform_sql(sql.format(strPath))
        try:
            assert(all(strPath_album_ids[0] == album_id for album_id in strPath_album_ids))
        except AssertionError:
            print 'Multiple album IDs for media in {0}'.format(strPath)
            continue
        for table in ['album', 'albuminfo', 'album_artist', 'album_genre', 'song']:
            sql = 'update {table} set idAlbum={new} where idAlbum={old};'
            db.perform_sql(sql.format(table=table, new=new_id,
                                      old=strPath_album_ids[0]))
        sql = 'update {table} set media_id={new} where media_id={old};'
        db.perform_sql(sql.format(table='art', new=new_id,
                                  old=strPath_album_ids[0]))
        if i % 100 == 0:
            print 'Processed {0} of {1} albums'.format(i, len(dirs))
    db.perform_sql('alter table album auto_increment={0};'.format(i+start_id+1))
    print 'Done!'


if __name__ == '__main__':
    execute()
