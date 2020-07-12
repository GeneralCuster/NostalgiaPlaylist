# NostalgiaPlaylist
Google Play Music Nostalgia Playlist Maker

This is a program which uses a 3rd party Google Play Music API (gmusicapi) and another 3rd party api
for billboard.com (billboard-charts) to grab a list of the top n number of songs from a given year,
find them all on play music, add them to library and then to a playlist.

Takes command line arguments --year, --month, and --day for determining for which date to download the hot 100 songs from billboard.com.

Plans for the future:
+ Check for "live", "concert", "acoustic", etc. in song titles to avoid adding versions of songs other than the studio version by the specified artist
+ Add option to avoid adding songs from certain genres, or to focus on certain genres
+ Add option to add explicit or clean versions - In the works, but buggy right now
+ GUI???
