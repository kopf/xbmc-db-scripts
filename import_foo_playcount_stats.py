#!/usr/bin/env python
import json
import os

from BeautifulSoup import BeautifulSoup

from db import DB


EXCLUDE = ['!!!!!1000']
db = DB('mymusic32')


if __name__ == '__main__':
    print 'Loading data from fb2k.json...'
    with open('fb2k.json', 'r') as f:
        raw_data = f.read()
    songs = []
    for line in raw_data.replace('\\', '/').split('\n'):
        songs.append(json.loads(line))
    print 'Loading last_sync.json'
    try:
        with open('last_sync.json', 'r') as f:
            last_sync = json.load(f)
    except IOError:
        print 'last_sync.json not found. Using empty last_sync data...'
        last_sync = {}
    else:
        print 'Done'
    i = 0
    results = {}
    for song in songs:
        for exclusion in EXCLUDE:
            if exclusion in song['path']:
                continue
        i += 1
        if i % 1000 == 0:
            print '{0} done'.format(i)
        path = song['path']
        rating = song['rating']
        play_count = int(song['playcount'])
        last_played = song['last_played']
        if rating == '?':
            rating = 0

        update_data = {}
        if rating > 0:
            update_data['rating'] = int(rating)
        if play_count > 0:
            update_data['play_count'] = play_count
        if last_played != 'N/A':
            update_data['last_played'] = last_played
        if update_data and update_data != last_sync.get(path, {}):
            path_split = path.split('/')
            del path_split[0]
            strPath = u'smb://192.168.92.20/' + u'/'.join(path_split[:-1]).replace('"', '\\"') + '/'
            strFileName = path_split[-1].replace('"', '\\"')
            sqlstrings = []
            if update_data.get('rating'):
                sqlstrings.append(u'rating = {0}'.format(update_data['rating']))
            if update_data.get('play_count'):
                plays_since_last_sync = update_data['play_count'] - last_sync.get(path, {}).get('play_count', 0)
                if plays_since_last_sync:
                    sqlstrings.append(u'iTimesPlayed = IF(iTimesPlayed IS NULL, {plays}, iTimesPlayed + {plays})'.format(plays=plays_since_last_sync))
            if update_data.get('last_played'):
                sqlstrings.append(u'lastplayed = IF(lastplayed IS NULL OR lastplayed < "{lp}", "{lp}", lastplayed)'.format(lp=update_data['last_played']))
            if sqlstrings:
                sql = u'UPDATE songview SET {0} WHERE strPath = "{1}" and strFileName = "{2}";'
                sql = sql.format(', '.join(sqlstrings), strPath, strFileName).encode('utf-8')
                db.perform_sql(sql)
        results[path] = update_data
    print 'Dumping sync to last_sync.json'
    with open('last_sync.json', 'w') as f:
        json.dump(results, f, indent=4)
