# cd Documents/MyFiles; source venv/bin/activate; sync-music-playlists/python sync.py

from sync_music_playlists import sync

username = 'jax'  # your computer username
pc_music_root_directory = '/home/' + username + '/Music/'  # root location of your music library for Rhythmbox (pc)
mb_music_root_directory = '/storage/3530-3564/Music/'  # root location of your music library for Vanilla Music
mb_playlist_pc_untouched = 'Top 100'  # playlist automatically created by Vanilla Music to keep untouched by pc
# text file to store the changes in the playlists resulting by the sync, create it before deploy
log = '/home/' + username + '/Documents/MyFiles/logs/sync.log'

sync(pc_playlists_root_directory='/home/' + username + '/.local/share/rhythmbox/',
     pc_music_root_directory=pc_music_root_directory, mb_music_root_directory=mb_music_root_directory,
     mb_playlist_pc_untouched=mb_playlist_pc_untouched, log=log,
     pc_playlists='playlists.xml', mb_playlists='*.m3u',
     start_playlists='  <playlist name="', end_playlists='  </playlist>\n',
     start_playlist_songs='    <location>file://', end_playlist_songs='</location>\n',
     pc_playlists_data='" show-browser="true" browser-position="180" search-type="search-match" type="static">')
