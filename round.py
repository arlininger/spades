# Author: Reilly Bova
# Date:   30 September 2018
# File:   round.py
# About:  Implements a "round" object in a game of Spades. Call the constructor,
#         and the rest of the round will be simulated until the round ends.

import random
import getpass
from card import Card
from contract import Contract
from spades_utils import *

# Consider moving thi section to it's own accumulator module

class Round:
    def __init__(self, num, players, game_header):
        self.num = num
        self.players = players
        self.game_state = game_header # Useful string to have on hand
        self.scores = [0, 0]
        self.bags = [0, 0]
        self.winnings = {'A1': 0, 'B1': 0, 'A2': 0, 'B2': 0}
        self.contracts = [Contract(), Contract()]
        self.hands = {}
        self.spade_in_play = False # Answers: Has a spade been played yet this round?

        self.card_win_count = [0 for id in range(52)]
        # for id in range(52):
        #     self.card_win_count[id] = 0

        # Run the round
        self.run()

    # Create deck of 52 cards, then shuffle and deal them (with splices)
    def deal_cards(self):
        deck = [Card(i) for i  in range(52)]
        random.shuffle(deck)
        for i, player in enumerate(self.players):
            hand = [c for c in deck[(i*13):((i+1) * 13)]]
            # Sort by suite and then order for user clarity
            hand.sort(key=(lambda k: k.id))

            self.hands[player] = hand

    # Handle printing cards to the screen. If selection is provided, then the index
    # of each card will under itself if its index is in selection. Otherwise, 'XXX' will
    # appear under the card
    def print_hand(self, hand, selection=[]):
        buffer = []
        # Preprocess all the cards into arrays of strings
        for i, card in enumerate(hand):
            data = card.viz()
            # Add an extra row to the string to denote user input selector
            if (len(selection) > 0):
                if (i not in selection):
                    selection_string = f"   XXX   "
                elif (i < 10):
                    selection_string = f"   [{i}]   "
                else:
                    selection_string = f"   [{i}]  "
                data.append(selection_string)

            buffer.append(data)

        # Print cards line by line
        if (len(buffer) > 0):
            for i in range(len(buffer[0])):
                line = []
                last_suite = hand[0].suiteID
                for j, card in enumerate(buffer):
                    # Add spacing between suite classes for clarity
                    if (hand[j].suiteID != last_suite):
                        line.append('   ')
                        last_suite = hand[j].suiteID
                    # Add this to the line we are working ACROSS
                    line.append(card[i])
                # Flush out results
                print(''.join(line))
        print()

    # Handle the printing of cards on the table. Similar to above method
    def print_table(self, table, ordering):
        print("On The Table:")
        buffer = []
        # Preprocess all the cards into arrays of strings
        for i, card in enumerate(table):
            data = card.viz()
            buffer.append(data)

        # Put ghost cards where cards will eventually go
        while (len(buffer) < 4):
            ghost_card = [ "┌ ─ ─ ─ ┐",
                           "         ",
                           "│       │",
                           "         ",
                           "└ ─ ─ ─ ┘"]
            buffer.append(ghost_card)

        # Mark the order of the players under their own cards
        for i, card_str in enumerate(buffer):
            player = ordering[i]
            player_string = f"  {i + 1}: {player}  "
            card_str.append(player_string)

        # Print cards line by line
        if (len(buffer) > 0):
            for i in range(len(buffer[0])):
                line = []
                for j, card in enumerate(buffer):
                    line.append(' ')
                    line.append(card[i])
                # Flush out results
                print(''.join(line))
        print()

    # Print the status of the game at the top of the screen
    def print_header(self):
        teamA = f"{self.contracts[0].to_string(self.winnings['A1'], self.winnings['A2'])}"
        teamB = f"{self.contracts[1].to_string(self.winnings['B1'], self.winnings['B2'])}"
        left = f"Round #{self.num} | Bids: (A) {teamA} vs. {teamB} (B)"
        right = self.game_state

        # Justify columns to edges
        padding = []
        for i in range(LINE_LEN - len(left) - len(right)):
            padding.append(' ')
        padding = ''.join(padding)
        print(left + padding + right)
        # Print a row of dashes to underline header
        print(DIVIDER)

    # # Handle user pin entry before their turn (TODO: Add graceful quitting)
    # def pin_check(self, player, msg, wipe=True):
    #     while (True):
    #         pin = getpass.getpass(msg)
    #         if (self.pins[player] != pin):
    #             print("Incorrect PIN! Are you sure it's your turn? (If you're stuck, force kill the game with \"^\\\")")
    #         else:
    #             break
    #     if (wipe):
    #         wipe_screen()

    # Force the user to enter a valid bet at the start of each round
    # def get_bet(self):
    #     msg = "Enter the number of hands you expect to win (enter 0 to bid nil):"
    #     while (True):
    #         bid = handle_input(msg)
    #         try:
    #             bid = int(bid)
    #             if ((bid < 0) or (bid > 13)):
    #                 print("Your bid must fall in the range [0, 13]!")
    #             else:
    #                 return bid
    #         except:
    #             print("Your bid must be an integer!")

    # Handle the bidding stage of the round
    def bidding(self):
        for i, player in enumerate(self.players):
            # msg = (f"It is your turn, {player.name}! \n")
            # self.print_header()

            # # Handle blindness
            # blind_msg = ("Would you like to view your cards? Answering no means "
            #                 "you will be bidding blind. (y/n)")
            # not_blind = handle_input(blind_msg, YORN)

            # # Show cards unless blind
            # if (not_blind):
            #     self.print_hand(self.hands[player])
            # else:
            #     print("Yikes! Good luck bidding blind!")

            # Get bid
            #bid_result = self.get_bet()
            not_blind = True
            bid_result = player.getBid(self.hands[player])

            # Log the bid in the team's contract under the player's name
            team = player.name[0]
            number = int(player.name[1])
            if (team == "A"):
                self.contracts[0].add_bid(number, bid_result, not not_blind)
            else:
                self.contracts[1].add_bid(number, bid_result, not not_blind)

    # A "trick" is a round of play (4 cards). This handles the execution of these rounds
    def play_trick(self, ordering):
        table = []      # Cards on the table
        lead_suite = -1 # Winning suite in play
        # self.print_header()
        # self.print_table(table, ordering)

        # Each player plays one card in a trick....
        for i, player in enumerate(ordering):
            msg = (f"It is your turn, {player}! \n")
            #self.pin_check(player, msg, wipe=False) # Enforce password

            # Record the indices of all playable cards
            selectable = []
            for i, card in enumerate(self.hands[player]):
                if (lead_suite == -1 and self.spade_in_play):
                    selectable.append(i) # Everything is good for first card when a spade has been played
                elif (lead_suite == -1 and card.suiteID != 3):
                    selectable.append(i) # Everything is good for first card but spades before a spade has been played
                elif (lead_suite == card.suiteID):
                    selectable.append(i) # Otherwise, try to match the lead suite
            if (len(selectable) == 0):
                selectable = [i for i in range(len(self.hands[player]))] # If nothing was playable, all cards are fair game!
            else:
                for i, card in enumerate(self.hands[player]):
                    if (card.suiteID == 3 and self.spade_in_play):
                        selectable.append(i) # Once a spade has been played, they may always be played

            result = player.getCard(selectable, table)
#            result = random.choice(selectable)

            # Remove card from hand and put it on the table
            played_card = self.hands[player].pop(result)
            table.append(played_card)

            # Update lead suite
            if (lead_suite == -1):
                lead_suite = played_card.suiteID
            if (played_card.suiteID == 3):
                lead_suite = 3
                self.spade_in_play = True

            # wipe_screen()
            # self.print_header()
            # self.print_table(table, ordering)
            # if (i < len(ordering) - 1):
            #     handle_input("Card played! Please pass the computer to the next player! Press any key to continue....")

        # Determine the winner of the trick
        best_card = table[0]
        winner = ordering[0]
        for i, card in enumerate(table):
            if (card.suiteID == lead_suite):
                if ((card.orderID > best_card.orderID) or (best_card.suiteID != lead_suite)):
                    best_card = card
                    winner = ordering[i]

        return winner, best_card

    # Handle a full round of play (all 13 4-card "tricks"/hands). Keeps track of
    # the ordering of players, and hands won by each player
    def play_round(self):
        ordering = [p for p in self.players]
        lead_player = ordering[0]

        # For each card in a hand...
        for i in range(13):
            lead_player, best_card = self.play_trick(ordering)
            self.card_win_count[best_card.id] = self.card_win_count[best_card.id] + 1
            self.winnings[lead_player.name] += 1
            # msg = (f"Player {lead_player} won the hand with {best_card.order}{best_card.suite}! Press any key to continue...")
            # handle_input(msg)
            # print(msg)

            # Rotate order until the winning player is first
            while (lead_player != ordering[0]):
                ordering.append(ordering.pop(0))

    # Score the round, and print the results
    def score(self):
        # self.print_header()
        # print("The round is over! Check out your scores below:")

        # Evaluate each contract on the round's results
        scoreA, bagA = self.contracts[0].eval(self.winnings['A1'], self.winnings['A2'])
        scoreB, bagB = self.contracts[1].eval(self.winnings['B1'], self.winnings['B2'])

        self.scores = [scoreA, scoreB]
        self.bags = [bagA, bagB]

        # print("Team A:")
        # print(f"\tContract:\t{self.contracts[0].to_string(self.winnings['A1'], self.winnings['A2'])}")
        # print(f"\tScore:\t\t{scoreA}")
        # print(f"\tBags:\t\t{bagA}")
        # print()
        # print("Team B:")
        # print(f"\tContract:\t{self.contracts[1].to_string(self.winnings['B1'], self.winnings['B2'])}")
        # print(f"\tScore:\t\t{scoreB}")
        # print(f"\tBags:\t\t{bagB}")
        # print()
        # print(card_win_count)
        # cards = dict()
        # values = dict()
        # for card_id in range(52):
        #     cards[card_id] = Card(card_id)
        #     values[card_id] = card_win_count[card_id]
        # for line in range(5):
        #     row = [cards[c].viz()[line] for c in range(0,13)]
        #     print(' '.join(row))
        # print("  ", '     '.join([("%5s" % values[c]) for c in range(0,13)]))
        # for line in range(5):
        #     row = [cards[c].viz()[line] for c in range(13,26)]
        #     print(' '.join(row))
        # print("  ", '     '.join([("%5s" % values[c]) for c in range(13,26)]))
        # for line in range(5):
        #     row = [cards[c].viz()[line] for c in range(26,39)]
        #     print(' '.join(row))
        # print("  ", '     '.join([("%5s" % values[c]) for c in range(26,39)]))
        # for line in range(5):
        #     row = [cards[c].viz()[line] for c in range(39,52)]
        #     print(' '.join(row))
        # print("  ", '     '.join([("%5s" % values[c]) for c in range(39,52)]))
        # handle_input("Press any key to end the round...")

    # Handle executing each stage of a round
    def run(self):
        self.deal_cards()
        self.bidding()
        self.play_round()
        self.score()
