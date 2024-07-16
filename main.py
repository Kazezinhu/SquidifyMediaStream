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


def update_data():
    url = "https://www.squidify.org/api/song/"
    response = requests.get(url)
    data = json.loads(response.content)
    f = open("data.json", "w")
    f.write(response.content.decode("utf-8"))
    f.close()
    return data


def retrieve_data():
    f = open("data.json", "r")
    data = json.loads(f.read())
    f.close()
    return data


data = 0
if os.path.isfile("data.json"):
    data = retrieve_data()
else:
    data = update_data()


def reload_data():
    global data
    data = update_data()


def get_line(id: str):
    for item in data:
        if item["id"] == id:
            return item


def get_url(id: str):
    return f"https://www.squidify.org/rest/stream?u={stream_url_parameter[0]}&t={stream_url_parameter[1]}&s={stream_url_parameter[2]}&f={stream_url_parameter[3]}&v={stream_url_parameter[4]}&c={stream_url_parameter[5]}&id={id}"


# f = open("songs.txt", "w")
# f.write(response.content.decode("utf-8"))
# f.close()

instance = vlc.Instance()
player = instance.media_player_new()
player.audio_set_track(1)
player.audio_set_volume(50)

song_id = test_id

close = False
while close is False:

    requested_song = input("Enter the song id: ")

    results = get_line(requested_song)

    if results is not None:
        song_id = requested_song
    else:
        print('Music not found.')
        continue

    length = float(results.get('duration'))

    media = instance.media_new(get_url(song_id))
    player.set_media(media)
    time.sleep(1)
    player.play()
    print("VLC State: ", player.get_state())
    time.sleep(length)


# media.parse_with_options(1, 0)
# prev = ""
# while True:
  # time.sleep(1)
  # m = media.get_meta(12) # vlc.Meta 12: 'NowPlaying',
    # if m != prev:
        # print("Now playing", m)
        # prev = m

# pya = pyaudio.PyAudio()
# audio_stream = requests.get(get_url(id), stream=True)
# stream = pya.open(format=pya.get_format_from_width(2), channels=2, rate=44100, output=True, output_device_index=6)
# stream.write(audio_stream.content[0].to_bytes())
# stream.stop_stream()
# stream.close()
