import sys

from BeautifulSoup import BeautifulSoup
import _mysql
import requests

from db import DB


db = DB('mymusic32')


def image_is_online(url):
    try:
        status_code = requests.head(url).status_code
    except Exception, e:
        return False
    if not 200 <= status_code < 300:
        return False
    return True


def add_media(_id, xml, img_type):
    sql = 'insert into art (media_id, media_type, type, url) values ("{0}", "{1}", "{2}", "{3}");'
    soup = BeautifulSoup(xml)
    url = None
    for tag in soup.findAll('thumb'):
        url = tag.text
        if 'htbackdrops.com' in url:
            # htbackdrops.com is down, ignore
            continue
        elif not url:
            continue
        if image_is_online(url):
            # image still online? Ok, let's use it.
            break
    if not url:
        return
    print 'Adding {0} image for artist {1}'.format(img_type, _id)
    db.perform_sql(sql.format(_id, 'artist', img_type, url))


def remove_404s():
    print 'Scanning old thumbnail URLs for 404s...'
    print 'This may take some time...'
    rows = db.perform_sql('select * from art where media_type="artist";',
                          full_row=True)
    i = 0
    total = len(rows)
    for row in rows:
        i += 1
        if i % 100 == 0:
            print 'Scanned {0} of {1}'.format(i, total)
        _id = row[0]
        url = row[4]
        if not image_is_online(url):
            db.perform_sql('delete from art where art_id={0};'.format(_id))


def add_artwork():
    print 'Adding missing artwork...'
    artists = db.perform_sql('select idArtist, strImage, strFanart from artistinfo;',
                             full_row=True)
    sql = 'select * from art where media_id={0} and media_type="artist" and type="{1}";'
    for artist in artists:
        _id = artist[0]
        strImage = artist[1]
        strFanart = artist[2]
        if 'http' in strImage and not db.perform_sql(sql.format(_id, 'thumb')):
            add_media(_id, strImage, 'thumb')
        if 'http' in strFanart and not db.perform_sql(sql.format(_id, 'fanart')):
            add_media(_id, strFanart, 'fanart')
                

if __name__ == '__main__':
    if '--remove-404s' in sys.argv:
        remove_404s()
    add_artwork()
