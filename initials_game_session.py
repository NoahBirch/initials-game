from collections import OrderedDict

class InitialsGameSession:

	def __init__(self, initials, user_id):
		self.initials = initials
		self.user_answers = self.create_user_answer_dict()
		self.user_id = user_id

	def create_user_answer_dict(self):
		# Create a blank dictionary 
		user_dict = OrderedDict()
		for initial_pair in self.initials:
			user_dict[initial_pair] = ""
		return user_dict
		
	def find_matches(self, candidate_answers):	
		# Now that we have the combos the player could be referencing, we need to
		# check this against our list of game initials. There could be multiple.
		# for example "Sarah Jessica Parker" outputs (S,J) and (S,P) as possible combos.

		# This list below will hold all the possible dict matches the player
		# could be refencing until they choose which one they meant later. 
		matches = []

		# Now we match all our possible combos to our game initials and add any
		# possible ones to the list we just created.
		for combo in candidate_answers:
			if combo in self.user_answers.keys():
				matches.append(combo)

		return matches

	def add_answer(self, i, matches, dict_index):	
		# This gets called if there is only one potential match, and this adds the match to the list.
		self.user_answers[matches[dict_index]] = i.title().strip()


	def display(self):
		# This function displays the users dictionary and any new additions
		# they have made eveyrtime it is called.
		for initial_pair in self.user_answers:
			print("".join(("".join(initial_pair) + " - ", self.user_answers[initial_pair])))
