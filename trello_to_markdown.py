#!/usr/bin/env python3

import argparse
import json
import os.path as op
from typing import Tuple


TEMPLATE = """
# {recipe_name}

## Keywords

{keywords}

## Image

{image}

## Metadata

{desc}
"""


def main(cards_path: str, save_path: str = 'recipes.md',
         card_idx: Tuple[int] = (0, 10)):
    """Convert Trello cards from .json to markdown

    Parameters
    ----------
    cards_path
        Path to the .json file containing recipe cards.
    save_path
        Path to the .md file to save at.
    card_idx
        Index of cards to save out (as the start and stop value in the range).

    """
    with open(cards_path) as f:
        cards = json.load(f)
    if op.splitext(save_path)[-1] != '.md':
        raise ValueError("save_path must end in .md!")
    # the lists they were in, which we'll use to grab keywords
    lists = cards['lists']
    lists = {l['id']: l['name'].lower() for l in lists}
    # recipes themselves
    cards = cards['cards']
    if card_idx is not None:
        cards = cards[slice(*card_idx)]
    recipes = ""
    for card in cards:
        desc = card['desc'].replace('# ', '## ')
        if not desc:
            # skip those cards which are just pictures of or links to recipes
            continue
        if '#' not in desc:
            # skip those cards which don't have any markdown
            continue
        # get the largest of the scaled cover images
        try:
            image = max(card['cover']['scaled'], key=lambda x: x['height'])['url']
        except KeyError:
            image = ''
        keywords = [lists[card['idList']]]
        keywords += [l['name'].lower() for l in card['labels']]
        name = card['name']
        # want to increase the header level of everything by 1
        recipes += TEMPLATE.format(recipe_name=name, keywords=', '.join(keywords),
                                   image=image, desc=desc)
    with open(save_path, 'w') as f:
        f.write(recipes)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=("Convert recipe cards (exported from Trello as a json)"
                     " into the custom Markdown format."))
    parser.add_argument('cards_path',
                        help='Path to the .json file containing recipe cards.')
    parser.add_argument('--save_path', default='recipes.md',
                        help='Path to the .md file to save at.')
    parser.add_argument('--card_idx', nargs=2, type=int, default=(0, 10),
                        help="Index of cards to save out (as the start and stop value in the range).")
    args = vars(parser.parse_args())
    main(**args)
