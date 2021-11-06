import random
import math

class AI_max:
	def __init__(self, name, past_data):
		self.name = name
		self.type = "AI_max"
		self.past_data = past_data

	def getBid(self, hand):
		return math.floor(sum([self.past_data['card_win_count'][card.id] / self.past_data['count'] for card in hand]))
		# return 3

	def getCard(self, selectable, currently_played):
		return selectable[-1]
		# return random.choice(selectable)

	def handResults(self):
		pass