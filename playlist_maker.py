import os
import socket

#Install ifaddr if not already installed, and import it
try:
    import ifaddr
except:
    print("ifaddr not installed, installing...")
    try:
        os.system("python3 -m pip install ifaddr")
        import ifaddr
    except:
        print("Error installing ifaddr")

#Install gmusicapi if not already installed, and import necessary modules
try:
    from gmusicapi import Musicmanager
    from gmusicapi import Mobileclient
except:
    print("gmusicapi not installed, installing...")
    try:
        os.system("python3 -m pip install gmusicapi")
        from gmusicapi import Musicmanager
        from gmusicapi import Mobileclient
    except:
        print("Error installing gmusicapi")

#Install getmac if not already installed, and import it
try:
    from getmac import get_mac_address
except:
    print("getmac not installed, installing...")
    try:
        os.system("python3 -m pip install getmac")
        from getmac import get_mac_address
    except:
        print("Error installing getmac")

#Install billboard.com api if not already installed, and import it
try:
    import billboard
except:
    print("billboard.com api not installed, installing...")
    try:
        os.system("python3 -m pip install billboard.py")
        import billboard
    except:
        print("Error installing billboard")

#Method to grab the currently used network interface so the user doesn't have to manually figure it out
def get_network_interface():
    interface = ""
    ip_address = ""

    #Get list of ip addresses from all interfaces to compare against each interface
    ips = socket.gethostbyname_ex(socket.gethostname())[-1]

    #Grab the first ip address that isn't localhost. This may need to be tweaked later for systems with multiple ips - the first that isn't localhost may not always be the correct choice
    for ip in ips:
        if ip != "127.0.0.1":
            ip_address = ip
            break

    #Use ifaddr to get a list of all network adapter names, and check each of their ip addresses to find one that matches the one we found above, which means that adapter is the one we want
    adapters = ifaddr.get_adapters()
    for adapter in adapters:
        for ip in adapter.ips:
            if ip.ip == ip_address:
                interface = adapter.nice_name
                break
    #Return the interface we found
    return interface

#Initialize list of songs to add, as touples of artist name and song ex. (Brantley Gilbert, Bottoms Up)
songs_to_add = []

#GET SONGS INFO FROM BILLBOARD.COM with their API first up here
billboard_year = "2013"
billboard_month = "11"
billboard_day = "15"

chart = billboard.ChartData('hot-100', date= billboard_year + '-' + billboard_month + '-' + billboard_day, fetch=True, timeout=25)
for song in chart:
    songs_to_add.append((song.artist, song.title))

#MUST USE OPENSSL 1.0.2s
#IDK but using the most recent version has given me issues

#Get MAC Address for en1, which happens to be the inteface my laptop is using to connect to the internet. On other machines this will be different.
#Ideally I'll find a way to determine which network interface a machine is using to connect, and then get the MAC Address for that interface.
wifi_mac = get_mac_address(interface=get_network_interface()).upper()

#Instantiate the gmusicapi session, imitating a mobile device
mc = Mobileclient()

#BEFORE any of this code will be able to run, this code must be executed and the directions followed, and then comment it out again and re-run the program:
#mc.perform_oauth()
#exit(1)

#This is an id for one of MY specific devices. I had to try connecting with a bogus id first, and it then told me a list of my actual device ids I could pick from
android_id = "184F32F408A1"
#Complete the login process with the device id
mc.oauth_login(device_id=android_id)

#Ensure the device is is authenticated (it probably is, since we were just able to login, but can't hurt to be explicit)
if mc.is_authenticated():
    print("Connected Successfully!")
else:
    print("Could not connect to Play Music, authentication failure. Exiting...")
    exit(1)

#Ensure the device/account actually has a google play subscription and is able to play/download/etc content
if mc.is_subscribed:
    print("This account DOES have a Play Music subscription!")
else:
    print("This account deos NOT have a Play Music subscription! Exiting...")
    exit(1)

#Get a list of the songs already in the account's library so we can compare songs we're looking for to it and ensure we don't add multiples of songs
owned_songs = mc.get_all_songs()

#Get a list of all playlists the user has so we can be sure not to try a name for ours that's already taken
users_playlists = mc.get_all_playlists(incremental=False)

#Create a name for the playlist, utilizing a root name so that we can add numbers to the end appropriately in the event that a playlist with our chosen name already exists
playlist_root_name = "Nostalgia Playlist " + billboard_year
playlist_name = playlist_root_name

#We're going to want to check to make sure that this name isn't already used for a playlist
users_playlists_names = []
for user_playlist in users_playlists:
    users_playlists_names.append(user_playlist["name"])

#Start this number at 2 since that's most likely what a human would do (playlist, playlist2, playlist3, etc)
appendable_num = 2
while playlist_name in users_playlists_names:
    playlist_name = playlist_root_name + " " + str(appendable_num)
    appendable_num = appendable_num + 1

#Once that loop finishes, playlist_name will be a uniquie-to-user playlist name, and we can go ahead and create that playlist.
#So create the actual playlist and keep its id so we can add songs to it easily later
playlist_id = mc.create_playlist(name=playlist_name, description="A playlist of nostalgic songs", public=False)

#Present some interesting stats to the user about the content on their account
print(str(len(owned_songs)) + " songs on account.")

#Begin looping through the list of songs from billboard.com
for song_to_add in songs_to_add:

    #Perform the search with the specified criteria
    artist_name = song_to_add[0]
    song_title = song_to_add[1]

    song_already_in_library = 0
    library_song_id = None

    #Check owned_songs to see if a song with that title by that artist is already in our account so we don't add duplicates of songs
    for owned_song in owned_songs:
        if owned_song["title"] == song_title and owned_song["artist"] == artist_name:
            #The song is already in our library, skip to the next song in songs_to_add
            song_already_in_library = 1
            library_song_id = owned_song["storeId"]
            break

    if song_already_in_library == 0:
        results = mc.search(artist_name + " " + song_title)

        #Traverse the results, but only if the list of songs has things in it
        if len(results) > 0 and len(results["song_hits"]) > 0:
            for result in results["song_hits"]:
                track = result["track"]
                title = track["title"]
                artist = track["artist"]
                length = track["durationMillis"]

                #Check that the length of the specific track we're looking at is greater than 0:00 - I was burned by this already, there's some glitchy things in the Play Music store.
                #Also check to make sure the artist name is exact, and the song title is exact
                if int(length) > 0 and track_title == song_title and track_artist == artist_name:

                    #If the length indicates we're working with a real song, then go ahead and cautiously grab the information we think we need. Not all tracks have all this information.
                    try:
                        store_id = track["storeId"]
                    except:
                        print("No Store ID for Query")
                    try:
                        artist_id = track["artistId"]
                    except:
                        print("No Artist ID for Query")

                    #Add the song to Play Music library
                    mc.add_store_tracks([store_id])
                    mc.add_songs_to_playlist(playlist_id, store_id)
                    print("Added song: \"" + track_title + "\" by " + track_artist + " to playlist: " + playlist_name)

                    #Break out of the loop cause we don't need to check any of the other results
                    break

        else:
            print("No results found, moving to next search query")
    else:
        #Song was already in library, reset the flag to 0 and inform user we didn't add the song
        song_already_in_library = 0
        print("Song: \"" + song_title + "\" by " + artist_name + " is already in your music library. Adding that track to playlist.")
        mc.add_songs_to_playlist(playlist_id, library_song_id)
        song_already_in_library = 0
        library_song_id = None
