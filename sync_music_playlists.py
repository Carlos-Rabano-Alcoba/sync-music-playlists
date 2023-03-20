# Automatically sync favorite music playlist from Rhythmbox (pc) and Vanilla Music (mb, mobile) with Syncthing

def load_pc_playlist(pc_playlist_root_directory, pc_playlist, start_playlist, end_playlist,
                     pc_music_root_directory, start_fav_songs, end_fav_songs):

    from urllib.parse import unquote

    file = open(pc_playlist_root_directory + pc_playlist)
    pc = file.readlines()
    file.close()

    s = 0
    for line in pc:
        if start_playlist in line:
            break
        s = s + 1

    if s == len(pc):
        return False
    else:
        e = s
        for line in pc[s:]:
            if line == end_playlist:
                break
            e = e + 1

        pc = pc[s + 1:e]

        s = start_fav_songs + pc_music_root_directory
        e = end_fav_songs

        for i, l in enumerate(pc):
            pc[i] = unquote(l[l.find(s) + len(s):l.find(e)]).replace('&amp;', '&')

        pc.sort()

        return pc


def load_pc_playlists(pc_playlist_root_directory, pc_playlists, start_playlists):

    file = open(pc_playlist_root_directory + pc_playlists)
    pc = file.readlines()
    file.close()

    playlists = []
    for i, line in enumerate(pc):
        if start_playlists in line:
            line = line[len(start_playlists):]
            if start_playlists not in pc[i + 1]:
                playlists.append(line[:line.find('"')])

    playlists.remove('Play Queue')

    return playlists


def load_mb_playlist(synced_directory, mb_playlist, mobile_music_root_directory):

    from os.path import isfile

    if isfile(synced_directory + mb_playlist):
        file = open(synced_directory + mb_playlist)
        mb = file.readlines()
        file.close()

        for i, l in enumerate(mb):
            mb[i] = l[len(mobile_music_root_directory):-1]

        mb.sort()

        return mb

    else:
        return False


def update_pc_playlist(pc_playlist_root_directory, pc_playlists, start_playlist, end_playlist,
                       pc_music_root_directory, start_fav_songs, end_fav_songs, mb):

    from urllib.parse import quote

    file = open(pc_playlist_root_directory + pc_playlists)
    pc = file.readlines()
    file.close()

    s = 0
    for line in pc:
        if start_playlist in line:
            break
        s = s + 1

    e = s
    for line in pc[s:]:
        if line == end_playlist:
            break
        e = e + 1

    pcs = pc[:s + 1]
    pce = pc[e:]

    s = start_fav_songs + pc_music_root_directory
    e = end_fav_songs

    with open(pc_playlist_root_directory + pc_playlists, 'w') as file:
        for line in pcs:
            file.write(line)
        for f in mb:
            file.write(s + quote(f, safe="()'/!,&+").replace('&', '&amp;') + e)
        for line in pce:
            file.write(line)
    file.close()


def create_pc_playlist(pc_playlist_root_directory, pc_playlists, playlist, start_playlists, end_playlists,
                       pc_music_root_directory, start_fav_songs, end_fav_songs, pc_playlists_data, mb):

    from urllib.parse import quote

    file = open(pc_playlist_root_directory + pc_playlists)
    pc = file.readlines()
    file.close()

    i = len(pc)
    for line in pc[::-1]:
        if line == end_playlists:
            break
        i = i - 1

    s = start_fav_songs + pc_music_root_directory
    e = end_fav_songs

    with open(pc_playlist_root_directory + pc_playlists, 'w') as file:
        for line in pc[:i]:
            file.write(line)
        file.write(start_playlists + playlist + pc_playlists_data)
        for f in mb:
            file.write(s + quote(f, safe="()'/!,&+").replace('&', '&amp;') + e)
        file.write(end_playlists)
        for line in pc[i:]:
            file.write(line)


def delete_pc_playlist(pc_playlist_root_directory, pc_playlists, start_playlist, end_playlist):

    file = open(pc_playlist_root_directory + pc_playlists)
    pc = file.readlines()
    file.close()

    s = 0
    for line in pc:
        if start_playlist in line:
            break
        s = s + 1

    e = s
    for line in pc[s:]:
        if line == end_playlist:
            break
        e = e + 1

    with open(pc_playlist_root_directory + pc_playlists, 'w') as file:
        file.writelines(pc[:s] + pc[e + 1:])


def update_mb_playlist(synced_directory, mb_playlist, mobile_music_root_directory, pc):

    with open(synced_directory + mb_playlist, 'w') as file:
        for line in pc:
            file.write(mobile_music_root_directory + line + '\n')


def logging(log, printout):

    file = open(log, 'a')
    print(printout)
    file.write(printout + '\n')
    file.close()


def sync(pc_playlists_root_directory, pc_music_root_directory, mb_music_root_directory, mb_playlist_pc_untouched, log,
         pc_playlists='playlists.xml', mb_playlists='*.m3u',
         start_playlists='  <playlist name="', end_playlists='  </playlist>\n',
         start_playlist_songs='    <location>file://', end_playlist_songs='</location>\n',
         pc_playlists_data='" show-browser="true" browser-position="180" search-type="search-match" type="static">'):

    from os import listdir, remove
    from time import sleep
    from datetime import datetime
    from watchdog.observers import Observer
    from watchdog.events import PatternMatchingEventHandler

    my_event_handler = PatternMatchingEventHandler(patterns=[pc_playlists, mb_playlists], ignore_directories=True)

    # Update pc
    def on_modified(event):
        playlist = event.src_path[len(pc_playlists_root_directory):]
        if playlist != pc_playlists:
            start_playlist = start_playlists + playlist[:-4] + '"'
            pc = load_pc_playlist(pc_playlists_root_directory, pc_playlists, start_playlist, end_playlists,
                                  pc_music_root_directory, start_playlist_songs, end_playlist_songs)
            mb = load_mb_playlist(pc_playlists_root_directory, playlist, mb_music_root_directory)

            if pc:
                added = [s for s in mb if s not in pc]
                deleted = [s for s in pc if s not in mb]
                if added:
                    printout = 'added in ' + playlist[:-4] + ':\n' + '\n'.join(added)
                    logging(log, printout)
                if deleted:
                    printout = 'deleted in ' + playlist[:-4] + ':\n' + '\n'.join(deleted)
                    logging(log, printout)

                if bool(added) | bool(deleted):
                    update_pc_playlist(pc_playlists_root_directory, pc_playlists, start_playlist, end_playlists,
                                       pc_music_root_directory, start_playlist_songs, end_playlist_songs, mb)
                    printout = datetime.now().strftime('%H:%M:%S') + ' pc updated\n'
                    logging(log, printout)
            else:
                create_pc_playlist(pc_playlists_root_directory, pc_playlists, playlist[:-4], start_playlists,
                                   end_playlists, pc_music_root_directory, start_playlist_songs, end_playlist_songs,
                                   pc_playlists_data, mb)
                printout = datetime.now().strftime('%H:%M:%S') + ' created new playlist in mb: ' + playlist[:-4] + \
                           '\n' + '\n'.join(mb) + '\n'
                logging(log, printout)

    def on_created(event):
        playlist = event.src_path[len(pc_playlists_root_directory):]
        if playlist != pc_playlists:
            mb = load_mb_playlist(pc_playlists_root_directory, playlist, mb_music_root_directory)
            start_playlist = start_playlists + playlist[:-4] + '"'
            pc = load_pc_playlist(pc_playlists_root_directory, pc_playlists, start_playlist, end_playlists,
                                  pc_music_root_directory, start_playlist_songs, end_playlist_songs)
            if not bool(pc):
                create_pc_playlist(pc_playlists_root_directory, pc_playlists, playlist[:-4], end_playlists,
                                   pc_music_root_directory, start_playlist_songs, end_playlist_songs,
                                   pc_playlists_data, mb)
                printout = datetime.now().strftime('%H:%M:%S') + ' created new playlist in mb: ' + playlist[:-4] + \
                           '\n' + '\n'.join(mb) + '\n'
                logging(log, printout)

    def on_deleted(event):
        playlist = event.src_path[len(pc_playlists_root_directory):]
        sleep(5)
        if (playlist != pc_playlists) & (playlist[-4:] == mb_playlists[1:]) & \
                (playlist not in listdir(pc_playlists_root_directory)):
            start_playlist = start_playlists + playlist[:-4] + '"'
            pc = load_pc_playlist(pc_playlists_root_directory, pc_playlists, start_playlist, end_playlists,
                                  pc_music_root_directory, start_playlist_songs, end_playlist_songs)
            if pc:
                delete_pc_playlist(pc_playlists_root_directory, pc_playlists, start_playlist, end_playlists)
                printout = datetime.now().strftime('%H:%M:%S') + ' deleted playlist in mb: ' + playlist[:-4] + '\n' + \
                           '\n'.join(pc) + '\n'
                logging(log, printout)

    # Update mb
    def on_moved(event):
        if (event.src_path == pc_playlists_root_directory + pc_playlists + '.tmp') & \
                (event.dest_path == pc_playlists_root_directory + pc_playlists):
            playlists = load_pc_playlists(pc_playlists_root_directory, pc_playlists, start_playlists)
            for playlist in listdir(pc_playlists_root_directory):
                if (playlist[-4:] == mb_playlists[1:]) & (playlist[:-4] not in playlists) & \
                        (playlist[:-4] != mb_playlist_pc_untouched):
                    printout = datetime.now().strftime('%H:%M:%S') + ' deleted playlist in pc: ' + playlist[:-4]
                    logging(log, printout)
                    mb = load_mb_playlist(pc_playlists_root_directory, playlist,
                                          mb_music_root_directory)
                    if mb:
                        printout = '\n'.join(mb) + '\n'
                    else:
                        printout = ''
                    logging(log, printout)
                    remove(pc_playlists_root_directory + playlist)
            playlists.remove(mb_playlist_pc_untouched)
            for playlist in playlists:
                start_playlist = start_playlists + playlist + '"'
                playlist = playlist + mb_playlists[1:]
                pc = load_pc_playlist(pc_playlists_root_directory, pc_playlists, start_playlist, end_playlists,
                                      pc_music_root_directory, start_playlist_songs, end_playlist_songs)
                mb = load_mb_playlist(pc_playlists_root_directory, playlist,
                                      mb_music_root_directory)
                if mb:
                    added = [s for s in pc if s not in mb]
                    deleted = [s for s in mb if s not in pc]
                    if added:
                        printout = 'added in ' + playlist[:-4] + ':\n' + '\n'.join(added)
                        logging(log, printout)
                    if deleted:
                        printout = 'deleted in ' + playlist[:-4] + ':\n' + '\n'.join(deleted)
                        logging(log, printout)

                    if bool(added) | bool(deleted):
                        update_mb_playlist(pc_playlists_root_directory, playlist, mb_music_root_directory, pc)
                        printout = datetime.now().strftime('%H:%M:%S') + ' phone updated\n'
                        logging(log, printout)
                else:
                    update_mb_playlist(pc_playlists_root_directory, playlist, mb_music_root_directory, pc)
                    printout = datetime.now().strftime('%H:%M:%S') + ' created new playlist in pc: ' + playlist[:-4] + \
                               '\n' + '\n'.join(pc) + '\n'
                    logging(log, printout)

    my_event_handler.on_modified = on_modified
    my_event_handler.on_moved = on_moved
    my_event_handler.on_created = on_created
    my_event_handler.on_deleted = on_deleted

    my_observer = Observer()
    my_observer.schedule(my_event_handler, path=pc_playlists_root_directory, recursive=False)

    info = datetime.now().strftime('%d %b %H:%M:%S') + ' syncing\n'
    logging(log, info)

    my_observer.start()
    try:
        while True:
            sleep(60)
    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()
