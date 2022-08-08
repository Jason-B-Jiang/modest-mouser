# contact: jasonbitan.jiang@mail.utoronto.ca

import torch
from random import seed
from lyrics_dataset import LyricsDataset
from model import LyricsLSTM
from torch.nn.utils.rnn import pad_sequence

################################################################################

## Global variables

seed(42)

lyrics_dataset = LyricsDataset()
model = LyricsLSTM()

BATCH_SIZE = 32
EPOCHS = 4
TRAIN_SIZE = int(round(len(lyrics_dataset) * 0.7))
VALID_SIZE = int(round(len(lyrics_dataset) * 0.2))
TEST_SIZE = len(lyrics_dataset) - TRAIN_SIZE - VALID_SIZE

################################################################################

def collator(batch):
    """Function for padding lyrics tensors in minibatches, so each minibatch has
    same size tensors.
    """
    line_1 = [lyric_pair[0] for lyric_pair in batch]
    line_2 = [lyric_pair[1] for lyric_pair in batch]

    # perform padding on both input lyric lines + lyric lines to predict
    # stacking of tensors done by pad_sequence produces the minibatch
    all_lines = line_1 + line_2
    padded_lines = pad_sequence(all_lines)

    return padded_lines[:,:len(line_1)], padded_lines[:,len(line_1):]


def train(lyrics_dataset: LyricsDataset, model: LyricsLSTM):
    lyrics_dataset.shuffle_dataset()
    
    train_split, valid_split, test_split = \
        torch.utils.data.random_split(lyrics_dataset,
            (TRAIN_SIZE, VALID_SIZE, TEST_SIZE))

    train_loader = torch.utils.data.DataLoader(train_split,
                                               batch_size=BATCH_SIZE,
                                               shuffle=True,
                                               collate_fn=collator)

    valid_loader = torch.utils.data.DataLoader(valid_split,
                                               batch_size=BATCH_SIZE,
                                               shuffle=True,
                                               collate_fn=collator)

    test_loader = torch.utils.data.DataLoader(test_split,
                                              batch_size=BATCH_SIZE,
                                              shuffle=True,
                                              collate_fn=collator)