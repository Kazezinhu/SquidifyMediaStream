import datetime
import time

import vlc
import asyncio
import request as rq
import queue

# city ruins = 14b5f2fd652855752e115730d88488c2
# ancients = caa0ddc79bccc7f904b0f9192c9949a0
# hills = 3aab83f9ed78bbdacebdf86b74ca8db7
# orchestral = 3edbf1c8fe1e57c4d5df795e9e16318d
# automata = b0ba791b4cd84ab97446471734e97f70

instance = vlc.Instance()
player = instance.media_player_new()
player.audio_set_track(1)
player.audio_set_volume(50)
instance.log_unset()

global t_duration, t_id, t_album, t_title


def set_play(track):
    global t_duration, t_id, t_album, t_title
    t_id = track.get('id')
    t_album = track.get('album')
    t_title = track.get('title')
    media = instance.media_new(rq.get_url(t_id))
    player.set_media(media)
    t_duration = str(datetime.timedelta(seconds=track.get('duration')))[:-7]


async def play():
    player.play()
    print(f"Now playing: \n Album: {t_album}\n Title: {t_title}\n Duration: {t_duration}")


async def play_album(album):
    for track in album:
        set_play(track)
        await asyncio.create_task(play())
        time.sleep(track.get('duration'))


async def main():
    close = False
    print("Enter 'q' to quit.")
    print("Enter 'p' to pause/resume and 's' to stop.")
    print("Types: a - album, t - track, get - get album, dl - download track")
    while close is False:

        request_type = input("Enter id type: ")

        if request_type == 'a':
            request_id = input("Enter album id: ")
        elif request_type == 't':
            request_id = input("Enter track id: ")
        elif request_type == 'get':
            request_id = input('Album id: ')
        elif request_type == 'p':
            if player.get_state() == vlc.State.Paused:
                print("Resuming")
            else:
                print("Pausing")
            player.pause()
            continue
        elif request_type == 's':
            player.stop()
            continue
        elif request_type == 'status':
            print(player.get_state())
            continue
        elif request_type == 'dl':
            request_id = input("Enter track id to download: ")
            await asyncio.create_task(rq.song_dl(request_id))
            continue
        elif request_type == 'q':
            break
        else:
            print('Invalid id type.')
            continue

        if request_type == 'get':
            album = rq.request_album_data(request_id)
            print(album)

            if album[0].get('error') is not None:
                print('Album not found.')
                continue

            for song in album:
                print(f"{song.get('title')} - {song.get('id')}")

        if request_type == 'a':
            album = rq.request_album_data(request_id)

            if album[0].get('error') is not None:
                print('Album not found.')
                continue

            await play_album(album)

        if request_type == 't':
            track = rq.request_song_data(request_id)

            if track.get('error') is not None:
                print('Track not found.')
                continue

            set_play(track)
            await asyncio.create_task(play())
    player.stop()
    instance.vlm_release()
    asyncio.current_task().cancel()

asyncio.run(main())
