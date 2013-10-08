xbmc-db-scripts
===============

This repo houses scripts I've thrown together to scratch various itches I had with the XBMC database. 

In order to use any of the scripts here, you'll need to be using [XBMC with a MySQL backend](http://wiki.xbmc.org/index.php?title=HOW-TO:Share_libraries_using_MySQL). 

## Warning

* __ALWAYS backup your xbmc databases before running any of these tools. I'm not responsible for any data loss.__
* These scripts worked for me. They may or may not work for you.
* These scripts were (somewhat shoddily) thrown together on hungover Sundays. The code within is rather inelegant and ugly. There are no tests. Proceed at your own risk.

## Requirements

* Python 2.7
* Install package dependencies with `pip install -r requirements.txt`
* Create a `settings.py` file containing your MySQL credentials in the form:

````
USERNAME = 'mysql_username'
PASSWORD = 'mysql_password'
HOST = 'hostname_or_ip'
````

Note: if you have trouble installing `MySQL-python`, [this may help](http://stackoverflow.com/a/7461662/221001).

## The scripts

### fix_thumbnails.py

#### The Problem

The "Query info for all artists" context menu item doesn't exactly do what you'd expect it to. You may have artists in your library which XBMC has already scanned thumbnails for, but whose thumbnails it doesn't display (e.g. if you go to `Artist information -> Get thumb` you'll see XBMC is already aware of thumbnails it can use for the artist, but still isn't showing any by default). 

This script scans through all artists in your database for which it finds links to thumbnails and fanart. Then, if it finds the artist doesn't already have a thumbnail or fanart assigned, it assigns the artwork. 

This can massively improve the artwork coverage in your music collection.

#### Configuration and execution

* No configuration necessary. Simply `python fix_thumbnails.py`.
* Running `python fix_thumbnails.py --remove-404s` will check whether all fanart and thumbnails that have already been linked to artists are still online. For any images it finds that return a 404, it removes them, before continuing with the normal process of adding thumbnails. This option issues an awful lot of HTTP requests and therefore takes an awfully long time. It shouldn't be necessary in most cases.

### fix_recently_added.py

#### The Problem

Albums are ordered in XBMC by the time at which they were added to XBMC. So, when you first scan your music library, your "Recently Added" music will be comprised of music beginning with the letter 'Z', since that's the last stuff scanned in to XBMC. 

Similarly, if you retag some albums and update your music library on XBMC, the retagged albums will suddenly jump to the top of the "Recently Added" playlist, even though you've had the albums for a long time.

This script re-orders entries in the database based on the age of each album's folder. After running the script, your albums in the XBMC library will be in the order in which you _actually_ added them to your hard disk.

There is however one possible problem point: if songs belonging to more than one album are found in the same directory, the directory will be ignored and its albums will not be re-ordered. These albums will therefore be marked as some of the oldest in the XBMC database. This shouldn't be a problem if you have a well-organised music library.

#### Configuration and execution

* If you want to ignore any directories, add them to `EXCLUDE` at the top of `fix_recently_added.py`.
* If you're using network shares to share your media, you'll need to map the share to your local drive letter in `fix_recently_added.py`. See the `REPLACEMENTS` dictionary at the top of `fix_recently_added.py`.
* Run the script: `python fix_recently_added.py`

### ensure_smb_protocol_in_paths.py

#### The Problem

I always used a single Windows XBMC client, streaming media across the network from another Windows box. I then bought a Raspberry Pi and want to use XBMC on it. 

The problem is, all of the paths in my XBMC database were in the form `\\192.168.1.1\movies\fargo\fargo.avi`, which is essentially meaningless on a Linux system such as the Raspberry Pi. Instead, paths in the form `smb://192.168.1.1/movies/fargo/fargo.avi` are required. This script converts the former into the latter linux-friendly form.

#### Configuration and execution

* No configuration necessary. Simply `python ensure_smb_protocol_in_paths.py`

### import_foo_playcount_stats.py

#### The Problem

You use both XBMC and foobar2000 for listening to music. You only want to update song ratings on foobar2000 and have them appear in XBMC. The same goes for play counts and songs and albums you last listened to. 

This script imports `foo_playcount` statistics into your XBMC database. 

#### Configuration and execution

* Add any folders containing files whose playcount stats should be ignored to the `EXCLUDE` list at the top of `import_foo_playcount_stats.py`.
* Install [foo_texttools](http://www.foobar2000.org/components/view/foo_texttools) on your foobar2000 player.
* Set up a new Quickcopy command in `Preferences -> Tools -> Text Tools`. Give it the name "Export Statistics" and the following pattern:

````
{"path": "$replace(%path%,'"','\"')", "rating": "%rating%", "playcount": "%play_count%", "last_played": "%last_played%"}
````

* Select all files in foobar2000 whose statistics you want to export. 
* Right click the selection and select `Utilities -> Text Tools -> Copy: Export Statistics.`
* Create a new file in the directory where you cloned this repo called `fb2k.json`. Paste the contents of the clipboard into this file. 
* Run the script: `python import_foo_playcount_stats.py`

The script also creates a file called `last_sync.json`, to keep track of what statistics it's already added to the XBMC database. This way, you can simply repeat the last few steps of the process (copying the statistics to the clipboard, saving them to `fb2k.json` and running the script) as often as you want in order to keep the XBMC database up to date with your changing statistics in foobar2000. If, however, the `last_sync.json` file is deleted, _all_ statistics will be added from foobar2000, instead of just changes since the last sync.

This is also a rather long-winded process. Improvements are welcome!
