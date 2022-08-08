# contact: jasonbitan.jiang@mail.utoronto.ca

import torch
import spacy
import pandas as pd
from typing import List, Tuple
from random import seed, shuffle
from torch.nn.utils.rnn import pad_sequence

################################################################################

seed(42)

class LyricsDataset(torch.utils.data.Dataset):
    """Create a PyTorch dataset for Modest Mouse lyric pairs, where each item
    in the dataset is a tuple of sequential lyrics in songs.
    """
    def __init__(self):
        # use blank spaCy pipeline just for text tokenization
        self._tokenizer = spacy.blank('en')
        self._lyrics = pd.read_csv('../data/modest_mouse_lyrics.csv')
        self._tokens = self._load_tokens()
        self._unique_tokens = self._get_unique_tokens()

        # create dictionaries mapping token indices in vocabulary back to the
        # tokens, and vice versa
        self._idx_to_token = {idx: token for idx, token in enumerate(self._unique_tokens)}
        self._token_to_idx = {token: idx for idx, token in enumerate(self._unique_tokens)}

        # format training example as tuples of word indices in vocabulary
        self._lyric_pairs = self._get_lyric_pairs()


    def _load_tokens(self) -> spacy.tokens.doc.Doc:
        """Get a set of all unique word tokens found in Modest Mouse lyrics, using
        spaCy's tokenization algorithm
        """
        # get a big string of all modest mouse lyrics concatenated together
        # make the string lowercase, so we don't end up making word embeddings for
        # different capitalizations of the same word
        all_lyrics = \
            self._lyrics['lyric_pair'].str.replace(' \|\| ', ' ').str.cat(sep=' ').lower()
        
        return self._tokenizer(all_lyrics)


    def _get_unique_tokens(self) -> List[str]:
        """Return set of all unique tokens in modest mouse lyrics
        """
        return set([tok.text for tok in self._tokens])


    def _get_lyric_pairs(self) -> List[Tuple[List[int], List[int]]]:
        """Return a List of tuples of the word indices of all words in a pair
        of lyrics.
        """
        return [(self._convert_to_idx(line_1), self._convert_to_idx(line_2)) for line_1, line_2 \
            in self._lyrics['lyric_pair'].str.lower().str.split(' \|\| ')]
    

    def _convert_to_idx(self, line: str) -> List[int]:
        """Docstring goes here.
        """
        tokens = self._tokenizer(line)
        return [self._token_to_idx[token.text] for token in tokens]


    def get_num_unique_tokens(self) -> int:
        """Return number of unique tokens in modest mouse lyrics.
        """
        return len(self._unique_tokens)


    def shuffle_dataset(self) -> None:
        """Randomly shuffle contents in this dataset.
        """
        shuffle(self._lyric_pairs)


    def __len__(self) -> int:
        """Return number of lyric pairs in the dataset.
        """
        return len(self._lyrics)


    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """Return the i-th pair of modest mouse song lyrics to use as a
        training/testing example.

        Pad lyrics tensors so they are of the same length.
        """
        padded_lyrics = pad_sequence(
            [torch.tensor(self._lyric_pairs[idx][0]),
            torch.tensor(self._lyric_pairs[idx][1])]
        )

        return padded_lyrics[:,0], padded_lyrics[:,1]