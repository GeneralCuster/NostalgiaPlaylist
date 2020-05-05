import os
from gmusicapi import Musicmanager
from gmusicapi import Mobileclient
from getmac import get_mac_address

#GET SONGS INFO FROM BILLBOARD.COM with their API first up here




#MUST USE OPENSSL 1.0.2s
#IDK but using the most recent version has given me issues

#Get MAC Address for en1, which happens to be the inteface my laptop is using to connect to the internet. On other machines this will be different.
#Ideally I'll find a way to determine which network interface a machien is using to connect, and then get the MAC Address for that interface.
wifi_mac = get_mac_address(interface="en1").upper()

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
playlist_root_name = "Nostalgia_Playlist_" + "year"
playlist_name = playlist_root_name

#We're going to want to check to make sure that this name isn't already used for a playlist
users_playlists_names = []
for user_playlist in users_playlists:
    users_playlists_names.append(user_playlist["name"])

#Start this number at 2 since that's most likely what a human would do (playlist, playlist2, playlist3, etc)
appendable_num = 2
while playlist_name in users_playlists_names:
    playlist_name = playlist_root_name + str(appendable_num)
    appendable_num = appendable_num + 1

#Once that loop finishes, playlist_name will be a uniquie-to-user playlist name, and we can go ahead and create that playlist.
#So create the actual playlist and keep its id so we can add songs to it easily later
playlist_id = mc.create_playlist(name=playlist_name, description="A playlist of nostalgic songs", public=False)

#Present some interesting stats to the user about the content on their account
print(str(len(owned_songs)) + " songs on account.")

#List of songs obtainted from billboard.com list
songs_to_add = [("Bastille", "Pompeii"), ("Brantley Gilbert", "Bottoms Up")]

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
                length = track["durationMillis"]
                #Check that the length of the specific track we're looking at is greater than 0:00 - I was burned by this already, there's some glitchy things in the Play Music store.
                if int(length) > 0:

                    #If the length indicates we're working with a real song, then go ahead and cautiously grab the information we think we need. Not all tracks have all this information.
                    try:
                        store_id = track["storeId"]
                    except:
                        print("No Store ID for Query")
                    try:
                        artist_id = track["artistId"]
                    except:
                        print("No Artist ID for Query")
                    try:
                        album_id = track["album_id"]
                    except:
                        print("No Album ID for Query")

                    title = track["title"]
                    artist = track["artist"]
                    album = track["album"]

                    #Add the song to Play Music library
                    mc.add_store_tracks([store_id])
                    mc.add_songs_to_playlist(playlist_id, store_id)
                    print("Added song: \"" + song_title + "\" by " + artist_name + " to playlist: " + playlist_name)

                    #Break out of the loop cause we don't need to check any of the other results
                    break


                #song_url = mc.get_stream_url(song_id=store_id)

        else:
            print("No results found, moving to next search query")
    else:
        #Song was already in library, reset the flag to 0 and inform user we didn't add the song
        song_already_in_library = 0
        print("Song: \"" + song_title + "\" by " + artist_name + " is already in your music library. Skipping.")
        mc.add_songs_to_playlist(playlist_id, library_song_id)
        song_already_in_library = 0
        library_song_id = None

        #HOWEVER, we're gonna want to use the song already in our library as our song to add to the nostalgia playlist
