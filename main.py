import json
import requests
import vlc
import time

# u, t, s, f, v, c
stream_url_parameter = ['Guest', '2dc98a10999257c14a0920f57d129b02', '318fe6', 'json', '1.8.0', 'NavidromeUI']
test_id = '14b5f2fd652855752e115730d88488c2'

url = "https://www.squidify.org/api/song/"
response = requests.get(url)
data = response.json()


def get_url(id: str):
    return f"https://www.squidify.org/rest/stream?u={stream_url_parameter[0]}&t={stream_url_parameter[1]}&s={stream_url_parameter[2]}&f={stream_url_parameter[3]}&v={stream_url_parameter[4]}&c={stream_url_parameter[5]}&id={id}"


# f = open("songs.txt", "w")
# f.write(response.content.decode("utf-8"))
# f.close()

audio_stream = requests.get(get_url(test_id), stream=True)
instance = vlc.Instance()
player = instance.media_player_new()
media = instance.media_new(get_url(test_id))

player.set_media(media)
player.audio_set_track(1)
player.audio_set_volume(70)
player.play()
print("VLC State: ", player.get_state())
time.sleep(332.24)


# media.parse_with_options(1, 0)
# prev = ""
# while True:
  # time.sleep(1)
  # m = media.get_meta(12) # vlc.Meta 12: 'NowPlaying',
    # if m != prev:
        # print("Now playing", m)
        # prev = m

# pya = pyaudio.PyAudio()

# stream = pya.open(format=pya.get_format_from_width(2), channels=2, rate=44100, output=True, output_device_index=6)
# stream.write(audio_stream.content[0].to_bytes())
# stream.stop_stream()
# stream.close()
