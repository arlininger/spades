import random

import math

class AI_random:
	def __init__(self, name, past_data):
		self.name = name
		self.type = "AI_random"
		self.past_data = past_data

	def getBid(self, hand):
		# for card in hand:
		# 	print(card.suite + card.order)
		return math.floor(sum([self.past_data['card_win_count'][card.id] / self.past_data['count'] for card in hand]))

	def getCard(self, selectable, table):
		return random.choice(selectable)