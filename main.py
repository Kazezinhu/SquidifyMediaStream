import json
import os.path

import requests
import vlc
import time

# u, t, s, f, v, c
stream_url_parameter = ['Guest', '2dc98a10999257c14a0920f57d129b02', '318fe6', 'json', '1.8.0', 'NavidromeUI']
test_id = '14b5f2fd652855752e115730d88488c2'  # city ruins
# ancients = caa0ddc79bccc7f904b0f9192c9949a0
# hills = 3aab83f9ed78bbdacebdf86b74ca8db7


def request_data():
    song = "https://www.squidify.org/api/song/"
    response = requests.get(song)
    f = open("song.json", "w")
    f.write(response.content.decode("utf-8"))
    f.close()

    album = "https://www.squidify.org/api/album/"
    response = requests.get(album)
    f = open("album.json", "w")
    f.write(response.content.decode("utf-8"))
    f.close()


def request_album_data(id: str):
    url = "https://www.squidify.org/api/song/?_sort=album&_start=0&_end=0&album_id=" + id
    print(url)
    response = requests.get(url)
    print(response.content)
    return json.loads(response.content)


def request_song_data(id: str):
    url = "https://www.squidify.org/api/song/" + id
    print(url)
    response = requests.get(url)
    print(response.content)
    return json.loads(response.content)


def get_url(id: str):
    return f"https://www.squidify.org/rest/stream?u={stream_url_parameter[0]}&t={stream_url_parameter[1]}&s={stream_url_parameter[2]}&f={stream_url_parameter[3]}&v={stream_url_parameter[4]}&c={stream_url_parameter[5]}&id={id}"


if not os.path.isfile("data.json"):
    request_data()

instance = vlc.Instance()
player = instance.media_player_new()
player.audio_set_track(1)
player.audio_set_volume(50)


def play(length, t_id):
    media = instance.media_new(get_url(t_id))
    player.set_media(media)
    time.sleep(1)
    player.play()
    time.sleep(1)
    print("VLC State: ", player.get_state())
    time.sleep(length-1)


close = False
while close is False:

    request_type = input("Enter id type (a - album, t - track): ")

    request_id = test_id

    if request_type == 'a':
        request_id = input("Enter album id: ")
    elif request_type == 't':
        request_id = input("Enter track id: ")
    else:
        print('Invalid id type.')
        continue

    if request_type == 'a':
        album = request_album_data(request_id)

        if album[0].get('error') is not None:
            print('Album not found.')
            continue

        for track in album:
            play(float(track.get('duration')), track.get('id'))

    if request_type == 't':
        track = request_song_data(request_id)

        if track.get('error') is not None:
            print('Track not found.')
            continue

        play(float(track.get('duration')), request_id)
