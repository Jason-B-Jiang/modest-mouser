# contact: jasonbitan.jiang@mail.utoronto.ca

import lyricsgenius
from os.path import exists
import pandas as pd
import re

################################################################################

## Global variables
ALTERNATE_SONG_INDICATORS = ('(Live ', 'Modest Mouse - ', '(album version)',
                             '(BBC Radio ', '[Live]', '(Aborted)', '(radio edit)',
                             '(live studio session)', '(1995 Demo)', '(live ')

DUPLICATE_SONGS = ('The ionizes & atomize', 'Third Planet',
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
    if exists('../data/modest_mouse_lyrics.csv'):
        songs_df = pd.read_csv('../data/modest_mouse_lyrics.csv')
        print("Fetching previously scraped lyrics")
    else:
        songs_df = get_modest_mouse_lyrics(token)
        songs_df.to_csv('../data/modest_mouse_lyrics.csv')
    
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
    genius = lyricsgenius.Genius(token)
    artist = genius.search_artist('Modest Mouse')
    song_titles = [song.title for song in artist.songs]
    song_lyrics = [song.lyrics for song in artist.songs]
        
    songs_df = pd.DataFrame(list(zip(song_titles, song_lyrics)),
                            columns = ['title', 'lyrics'])

    # Flag duplicate/live song lyrics, and remove songs without lyrics
    songs_df = songs_df[songs_df['lyrics'].notnull()]
    songs_df = songs_df.assign(
        is_alternate_or_duplicate_song = lambda df: df['title'].map(
            lambda s: is_alternate_or_duplicate_song(s)
        )
    )

    # format song lyrics by removing irrelevant text (ex: song name, excess
    # newlines, etc
    songs_df = songs_df.assign(
        lyrics_formatted = lambda df: df['lyrics'].map(
            lambda s: format_song_lyrics(s)
        )
    )

    return songs_df


def is_alternate_or_duplicate_song(title: str) -> bool:
    """Return True if the song title in some row indicates that it is an
    alternate version of a song (ex: demo, live performance) or duplicate.
    
    Args:
        title (:obj:`str`): song title for a Modest Mouse song
    """
    return any([s in title for s in ALTERNATE_SONG_INDICATORS]) or \
        any([title == s for s in DUPLICATE_SONGS])


def format_song_lyrics(lyrics: str) -> str:
    """Format a song's lyrics by removing the following patterns:
    1) Song title + "Lyrics" boilerplate text at beginning of lyrics
    2) {numbers}Embed boilerplate text at end of lyrics
    3) Any text in [square brackets] (these indicate song choruses, etc)
    4) Leading/trailing newlines
    5) Excess newlines (i.e: >=2 consecutive newline characters)

    Args:
        lyrics (:obj:`str`): string for lyrics scraped by LyricsGenius
    """
    # remove song title + 'lyrics' boilerplate text at start of lyrics
    lyrics = re.sub(r"^.* ?Lyrics", "", lyrics)

    # remove '{numbers}Embed' boilerplate text at end of lyrics
    lyrics = re.sub(r"[0-9]*Embed$", "", lyrics)

    # remove song structure indicators (ex: [Chorus], [Verse 1], etc)
    lyrics = re.sub(r"\[[^\]]+\]", "", lyrics)

    # remove trailing and excess newlines
    lyrics = re.sub(r'\n{2,}', r"\n", lyrics.strip())

    return lyrics

################################################################################

if __name__ == '__main__':
    main()