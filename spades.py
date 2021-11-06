#!/usr/bin/env python3

# Author: Reilly Bova
# Date:   30 September 2018
# File:   spades.py
# About:  The main file for my "Spades" python program for the terminal

import os
import json

from game import Game
from AI_random import AI_random
from AI_max import AI_max
from spades_utils import *
from card import Card

def print_card_win_rates(card_win_count):
    cards = dict()
    values = dict()
    for card_id in range(52):
        cards[card_id] = Card(card_id)
        values[card_id] = card_win_count[card_id]
    for line in range(5):
        row = [cards[c].viz()[line] for c in range(0,13)]
        print(' '.join(row))
    print("", '   '.join([("%7s" % values[c]) for c in range(0,13)]))
    for line in range(5):
        row = [cards[c].viz()[line] for c in range(13,26)]
        print(' '.join(row))
    print("", '   '.join([("%7s" % values[c]) for c in range(13,26)]))
    for line in range(5):
        row = [cards[c].viz()[line] for c in range(26,39)]
        print(' '.join(row))
    print("", '   '.join([("%7s" % values[c]) for c in range(26,39)]))
    for line in range(5):
        row = [cards[c].viz()[line] for c in range(39,52)]
        print(' '.join(row))
    print("", '   '.join([("%7s" % values[c]) for c in range(39,52)]))

# Handles game setup and invokes play
def run_game(past_data):
    winning_value = 500

    wipe_screen()

    A1 = AI_random("A1", past_data)
    A2 = AI_random("A2", past_data)
    B1 = AI_max("B1", past_data)
    B2 = AI_max("B2", past_data)
    spades = Game(winning_value, A1, B1, A2, B2)
    spades.run()

    return spades.run()
    # print_card_win_rates(card_win_count)



# Master method of script
# def main():
#     try:
#         with open('data.txt') as json_file:
#             past_data = json.load(json_file)
#         # print(past_data)
#     except Exception as e:
#         past_data = dict()
#         past_data['count'] = 0
#         past_data['card_win_count'] = [0 for card_id in range(52)]

#     winner_stats = {"A": 0, "B": 0}
#     for i in range(1000):
#         gamestats = run_game(past_data)
#         winner_stats[gamestats['winner']] = winner_stats[gamestats['winner']] + 1
#         card_win_count = gamestats['card_win_count']
#         past_data['count'] = past_data['count'] + card_win_count[51] # Ace of Spades always wins
#         for card_id in range(52):
#             past_data['card_win_count'][card_id] = past_data['card_win_count'][card_id] + card_win_count[card_id]

#     print(winner_stats)
#     with open('data.txt', 'w') as outfile:
#         json.dump(past_data, outfile)

# if __name__ == '__main__':
#     main()
