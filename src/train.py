# contact: jasonbitan.jiang@mail.utoronto.ca

import torch
from lyrics_dataset import LyricsDataset
from model import LyricsLSTM
from torch.nn.utils.rnn import pad_sequence

################################################################################

def collator(batch):
    """Function for padding lyrics tensors in minibatches, so each minibatch has
    same size tensors.
    """
    line_1 = torch.tensor([lyric_pair[0] for lyric_pair in batch])
    line_2 = torch.tensor([lyric_pair[1] for lyric_pair in batch])

    all_lines = line_1 + line_2
    padded_lines = pad_sequence(all_lines)

    return padded_lines[:len(line_1)], padded_lines[len(line_1):]
