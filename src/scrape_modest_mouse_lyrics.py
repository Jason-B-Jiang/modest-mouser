# contact: jasonbitan.jiang@mail.utoronto.ca

import lyricsgenius
from os.path import exists
import pandas as pd

################################################################################

## Global variables
ALTERNATE_SONG_INDICATORS = ('(Live ', 'Modest Mouse - ', '(album version)',
                             '(BBC Radio ', '[Live]', '(Aborted)', '(radio edit)',
                             '(live studio session)', '(1995 Demo)', '(live ')

DUPLICATE_SONGS = ('The ionizes & atomize',
                   'Whenever I Breathe Out (Positive/Negative)',
                   'Styrofoam Boots',
                   'Styrofoam Boots (intro)',
                   'Sleepwalking (Couples Only Dance Prom Night)',
                   'Sleepwalkin’', 'I Came as a Rat (Long Walk Off a Short Dock)')

################################################################################

def main() -> None:
    # load in client access token for API access to Genius
    if not exists('../access_token'):
        print("Please paste your client access token to a file named 'access_token'")
        return

    with open('../access_token', 'r') as f:
        token = f.readlines()[0].strip()

    # dataframe of modest mouse songs and their lyrics
    songs_df = get_modest_mouse_lyrics(token)

    songs_df.to_csv('../data/modest_mouse_lyrics_filtered.csv')
    
################################################################################

## Helper functions

def get_modest_mouse_lyrics(token: str) -> pd.core.frame.DataFrame:
    """Use Genius API key, token, to retrieve all Modest Mouse song lyrics.

    Filter out duplicate songs, songs that correspond to live performances/demos
    (as their album versions already have lyrics) and songs without lyrics.

    Args:
        token (:obj:`str`): API access key for Genius
    
    Return:
        Pandas dataframe, with song names + song lyrics as columns
    """
    # haven't already scraped modest mouse lyrics with LyricsGenius yet, so do
    # that
    if not exists('../data/modest_mouse_lyrics_unfiltered.csv'):
        genius = lyricsgenius.Genius(token)
        artist = genius.search_artist('Modest Mouse')
        song_titles = [song.title for song in artist.songs]
        song_lyrics = [song.lyrics for song in artist.songs]
        
        songs_df = pd.DataFrame(list(zip(song_titles, song_lyrics)),
                                columns = ['title', 'lyrics'])

        # write csv of all song lyrics scraped from genius
        songs_df.to_csv('../data/modest_mouse_lyrics_unfiltered.csv')

    else:
        songs_df = pd.read_csv('../data/modest_mouse_lyrics.csv')

    # remove duplicate/live song lyrics, as well as songs without lyrics
    songs_df = songs_df[songs_df['lyrics'].notnull()]
    songs_df = \
        songs_df[~songs_df.apply(
            is_alternate_or_duplicate_song, axis=1
        )]

    # format song lyrics by removing irrelevant text (ex: song name, excess
    # newlines, etc
    songs_df = 



def is_alternate_or_duplicate_song(row: pd.core.series.Series) -> bool:
    """Return True if the song title in some row indicates that it is an
    alternate version of a song (ex: demo, live performance) or duplicate.
    
    Args:
        row (:obj:`pandas.core.series.Series`): row from songs_df dataframe
    """
    return any([s in row['title'] for s in ALTERNATE_SONG_INDICATORS]) or \
        any([row['title'] == s for s in DUPLICATE_SONGS])


def clean_song_lyrics(lyrics: str) -> str:
    # string patterns to remove from lyrics
    # ^.+Lyrics
    # [0-9]*Embed$
    # \[.+?\] (use non-greedy/lazy match)
    # leading/trailing newlines
    # excess newlines (ex: >= 2 consecutive newlines)
    pass

################################################################################

if __name__ == '__main__':
    main()