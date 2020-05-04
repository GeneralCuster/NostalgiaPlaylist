import os
from gmusicapi import Musicmanager
from gmusicapi import Mobileclient
from getmac import get_mac_address

#Get MAC Address for en1, which happens to be the inteface my laptop is using to connect to the internet. On other machines this will be different.
#Ideally I'll find a way to determine which network interface a machien is using to connect, and then get the MAC Address for that interface.
wifi_mac = get_mac_address(interface="en1").upper()

#Instantiate the session
mc = Mobileclient()

#BEFORE any of this code will be able to run, this code must be executed and the directions followed:
#mc.perform_oauth()

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

#Present some interesting stats to the user about the content on their account
print(str(len(owned_songs)) + " songs on account.")

#Perform the search with the specified criteria
results = mc.search("Brantley Gilbert Bottoms Up")

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

            print(artist + " " + album + " " + title)
            mc.add_store_track(store_id)
            break


        #song_url = mc.get_stream_url(song_id=store_id)

else:
    print("No results found, moving to next search query")
