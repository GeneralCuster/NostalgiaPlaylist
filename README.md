# NostalgiaPlaylist
Google Play Music Nostalgia Playlist Maker

This is a program which uses a 3rd party Google Play Music API (gmusicapi) and another 3rd party api
for billboard.com (billboard-charts) to grab a list of the top n number of songs from a given year,
find them all on play music, add them to library and then to a playlist.

Currently, it is functionally done but strings within the script must be edited for custom functionality,
unless you just want the top 100 for August 31st, 2014 to download constantly ;)

Plans for the future:
+ Check for "live", "concert", "acoustic", etc. in song titles to avoid adding versions of songs other than the studio version by the specified artist
+ Check that album artist the the actual artist to aid in only downloading songs from their original albums
+ Add option to avoid adding songs from certain genres, or to focus on certain genres
+ Add option to add explicit or clean versions
+ Implement command line arguments
+ GUI???
