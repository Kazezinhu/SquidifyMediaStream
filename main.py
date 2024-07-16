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
player = instance.media_list_player_new()
player.get_media_player().audio_set_track(1)
player.get_media_player().audio_set_volume(50)
instance.log_unset()
medialist = instance.media_list_new()
medialist.retain()
player.set_media_list(medialist)


global t_duration, t_id, t_album, t_title

playqueue = queue.Queue()


def player_free():
    state = player.get_state()
    return state in (vlc.State.Stopped, vlc.State.NothingSpecial, vlc.State.Ended, vlc.State.Error)


def set_play():
    track = playqueue.get()
    global t_duration, t_id, t_album, t_title
    t_id = track.get('id')
    t_album = track.get('album')
    t_title = track.get('title')
    # media = instance.media_new(rq.get_url(t_id))
    # player.set_media(media)
    t_duration = str(datetime.timedelta(seconds=track.get('duration')))[:-7]


async def play():
    player.play()


def song_ended(self, event):
    player.next()
    set_play()
    print(f"Now playing: \n Album: {t_album}\n Title: {t_title}\n Duration: {t_duration}")


def media_list_ended(self, event):
    print("Playlist ended.")


def next_item_set(self, event):
    set_play()
    print(f"Now playing: \n Album: {t_album}\n Title: {t_title}\n Duration: {t_duration}")


async def play_album(album):
    for track in album:
        medialist.add_media(rq.get_url(track.get('id')))
        playqueue.put(track)
    if not player.is_playing():
        player.next()
        await play()
    else:
        print("Queued: " + album.get('title'))


async def main():
    event_manager = player.event_manager()
    event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, song_ended, 1)
    event_manager.event_attach(vlc.EventType.MediaListEndReached, media_list_ended, 1)
    event_manager.event_attach(vlc.EventType.MediaListPlayerNextItemSet, next_item_set, 1)
    close = False
    print("Enter 'q' to quit.")
    print("Enter 'p' to pause/resume, 'stop' to stop and 'next' for next.")
    print("Types: a - album, t - track, get - get album, dl - download track")
    while close is False:

        request_type = input("Enter id type: ")

        match request_type:

            case 'a':
                request_id = input("Enter album id: ")
            case 't':
                request_id = input("Enter track id: ")
            case 'get':
                request_id = input('Album id: ')
            case 'p':
                if player.get_state() == vlc.State.Paused:
                    print("Resuming")
                else:
                    print("Pausing")
                player.pause()
                continue
            case 'stop':
                player.stop()
                continue
            case 'next':
                player.next()
                continue
            case 'status':
                print(player.get_state())
                if player.get_state() == vlc.State.Playing:
                    print(f"Now playing: \n Album: {t_album}\n Title: {t_title}\n Current: {str(datetime.timedelta(seconds=player.get_media_player().get_time() / 1000))[:-7]}\n Duration: {t_duration}")
                continue
            case 'dl':
                request_id = input("Enter track id to download: ")
                await asyncio.create_task(rq.song_dl(request_id))
                continue
            case 'q':
                break
            case _:
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

            medialist.add_media(rq.get_url(track.get('id')))
            playqueue.put(track)
            if player.is_playing():
                print("Queued: " + track.get('title'))
            else:
                player.next()
                await play()

    player.stop()
    instance.vlm_release()
    asyncio.current_task().cancel()

asyncio.run(main())
