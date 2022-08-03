# contact: jasonbitan.jiang@mail.utoronto.ca

import lyricsgenius
from os.path import exists
import pandas as pd
import re
from typing import List

################################################################################

## Global variables
ALTERNATE_SONG_INDICATORS = ('(Live', 'Modest Mouse - ', '(album version)',
                             '(BBC', '[Live]', '(Aborted)', '(radio edit)',
                             '(live studio session)', '(1995 Demo)', '(live')

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
    songs = {song.title: get_lyric_pairs(song.lyrics) for song in artist.songs \
        if not is_alternate_or_duplicate_song(song.title)}

    # create lists of song titles + all pairs of consecutive song lyric lines
    # for each song
    song_titles = []
    lyric_pairs = []
    for song in songs:
          song_titles.extend([song] * len(songs[song]))
          [lyric_pairs.extend(songs[song])]
        
    songs_df = pd.DataFrame(list(zip(song_titles, lyric_pairs)),
                            columns = ['song_title', 'lyric_pair'])

    return songs_df


def is_alternate_or_duplicate_song(title: str) -> bool:
    """Return True if the song title in some row indicates that it is an
    alternate version of a song (ex: demo, live performance) or duplicate.
    
    Args:
        title (:obj:`str`): song title for a Modest Mouse song
    """
    return any([s in title for s in ALTERNATE_SONG_INDICATORS]) or \
        any([title == s for s in DUPLICATE_SONGS])


def get_lyric_pairs(lyrics: str) -> List[str]:
    """Return all pairs of consecutive lyric lines from a song, where each pair
    is a ' || ' separated string of 2 lyric lines.
    
    Args:
        lyrics (:obj:`str`): lyrics for some Modest Mouse song, scraped from
        Genius.
    """
    lyrics = [l for l in format_song_lyrics(lyrics).split('\n') \
        if l not in (' ', '')]

    lyric_pairs = []
    for i in range(len(lyrics) - 1):
        # remove parentheses and square brackets that may be enclosing lyrics
        # ex: "(It was hanging out by itself)" -> "It was hanging out by itself"
        lyric_pairs.append(
            re.sub(r'(\(|\)|\[|\])', '', lyrics[i]) + ' || ' + \
                re.sub(r'(\(|\)|\[|\])', '', lyrics[i + 1])
            )
    
    return lyric_pairs


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