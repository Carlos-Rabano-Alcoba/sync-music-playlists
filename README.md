# Sync music playlists between Rhythmbox (pc) and Vanilla Music (mobile phone)

Fully synchronize your music playlists between Rhythmbox, in your computer, and Vanilla Music,
in your mobile phone.

1. In Vanilla Music: Settings > Playlists > Playlists Synchronization, select Full
synchronization.

2. Synchronize /home/username/.local/share/rhythmbox/ in your computer
with storage/emulated/0/Android/media/ch.blinkenlights.android.vanilla/Playlists in your
phone with Syncthing.

3. Modify sync.py and sync.sh scripts following inplace instructions.

4. Give sync.sh permission to run as a program, and add it to
Session and Startup > Application Autostart to trigger it on logging.

Deployed in Linux Mint 21.1 with Python 3.10.6 (watchdog 2.3.1).
For Rhythmbox 3.4.4 and Vanilla Music 1.3.0.
