# contact: jasonbitan.jiang@mail.utoronto.ca

import lyricsgenius
from os.path import exists
import pandas as pd

################################################################################

## Global variables
## TODO - replace some indicators with regex patterns, or use a spaCy matcher?
ALTERNATE_SONG_INDICATORS = ('(Live ', 'Modest Mouse - ', '(album version)',
                             '(BBC Radio ', '[Live]', '(Aborted)', '(radio edit)',
                             '(live studio session)')

DUPLICATE_SONGS = ('The ionizes & atomize',
                   'Whenever I Breathe Out (Positive/Negative)',
                   'Styrofoam Boots',
                   'Styrofoam Boots (intro)')

################################################################################

def main() -> None:
    # load in client access token for API access to Genius
    if not exists('../access_token'):
        print("Please paste your client access token to a file named 'access_token'")
        return

    with open('../access_token', 'r') as f:
        token = f.readlines()[0].strip()

    if not exists('../data/modest_mouse_lyrics.csv'):
        genius = lyricsgenius.Genius(token)
        artist = genius.search_artist('Modest Mouse')
        song_titles = [song.title for song in artist.songs]
        song_lyrics = [song.lyrics for song in artist.songs]
        
        songs_df = pd.DataFrame(list(zip(song_titles, song_lyrics)),
                                columns = ['title', 'lyrics'])
        songs_df.to_csv('../data/modest_mouse_lyrics.csv')

    else:
        songs_df = pd.read_csv('../data/modest_mouse_lyrics.csv')

    # stuff to clean:
    # 1) remove song title header from all lyrics
    # 2) remove verse, chorus, etc indicators
    # 3) remove trailing '{numbers}embed' at end of all lyrics
    # 4) remove duplicate songs (demos, live performances, etc)
    # 5) instrumentals (ex: Interlude (Milo))
    

################################################################################

## Helper functions

def is_alternate_or_duplicate_song(title: str) -> bool:
    """Return True if the lyrics for some song title are a duplicated entry in
    Genius, or it's lyrics for a live performance/demo.
    
    Args:
        title (:obj:`str`): title of the song
    """
    return any([indicator in title for indicator in ALTERNATE_SONG_INDICATORS]) or \
        any([title == dup for dup in DUPLICATE_SONGS])


def clean_song_lyrics(lyrics: str) -> str:
    pass

################################################################################

if __name__ == '__main__':
    main()