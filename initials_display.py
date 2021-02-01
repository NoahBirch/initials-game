from letter_gen import gen_start
from collections import OrderedDict
import re
import threading
import time
from pynput.keyboard import Key, Controller

keyboard = Controller()

game_over = False

timer_duration = 60 #seconds

# --------- TIMER STUFF ---------- #

def count_1_sec(duration):
	global game_over
	sec = 0
	while sec < duration:
		sec += 1
		time.sleep(1)

	game_over = True
	keyboard.press(Key.enter)

timer_thread = threading.Thread(target=count_1_sec, args=(timer_duration,))

# ----------- SETUP FUNCTIONS --------------- #

def create_user_answer_dict():
	# We need this function so we can create a blank dictionary
	# where the players answers will be stored. 
	for initial_pair in game_initials:
		user_dict[initial_pair] = ""

# ----------- GAMEPLAY FUNCTIONS --------------- #

def display_inits_as_list():
	# This function displays the users dictionary and any new additions
	# they have made eveyrtime it is called. 
	for initial_pair in user_dict:
		print("".join(("".join(initial_pair) + " - ", user_dict[initial_pair])))

def check_for_game_over():
	global game_over

	if game_over == True:
		end_game()
	else:
		pass

def take_input():
	# As a fail safe we always want to check for game over because this could be called
	# in the multiple matches function
	check_for_game_over()
	# Take input and return it
	i = input("\n> ")
	return i

def initial_extraction(i):
	"""Here we check our input that we will use to find matching initials.
	This function takes input, extracts initials from it, then outputs a set
	of combos those initials could be."""

	# Now we check our input and grab the beginning letter from each word.
	extracted_initials = re.findall(r"(\b[a-zA-Z])", i.replace("'", "").upper())

	###Line below used for testing
	###print("These initials were extracted: ", extracted_initials)

	# Now because players can input more than just two words, we want to check
	# all the posible combos of initials starting with the first one. 
	# for example "Sarah jessica parker" outputs (S,J) & (S,P) because
	# we don't want to determine which the player has to enter. 
	# So we create the below list to hold 
	initial_combos = []
	
	for num in range(1, len(extracted_initials)):
		possible_combo = (extracted_initials[0],extracted_initials[num])
		initial_combos.append(possible_combo)

	# Now we have the possible combos the player could have intended to add to their answers. 
	# But if they have put "Little Severus Snape" they will get 2 matches of ('L', 'S')
	# So we use this to eliminate duplicates:
	initial_combos = list(dict.fromkeys(initial_combos))

	return initial_combos
	
def extraction_check(initial_combos):	
	# Now that we have the combos the player could be referencing, we need to
	# check this against our list of game initials. There could be multiple.
	# for example "Sarah Jessica Parker" outputs (S,J) and (S,P) as possible combos.

	# This list below will hold all the possible dict matches the player
	# could be refencing until they choose which one they meant later. 
	dict_matches = []

	# Now we match all our possible combos to our game initials and add any
	# possible ones to the lsit we just created.
	for combo in initial_combos:
		if combo in user_dict.keys():
			dict_matches.append(combo)
		else:
			pass

	return dict_matches

def no_match_processing():
	print("Couldn't find a match. Try again.\n")

def add_to_list(i, matches, dict_index):	
	# This gets called if there is only one potential match, and this adds the match to the list.
	print("Adding %s to your list." % i)
	user_dict[matches[dict_index]] = i.title().strip()

def multi_match_processing(i, matches):
		print("There are %d matches this could be." % len(matches))
		print("Here they are:")

		multiple_match_dict = {}
		n = 1

		for match in matches:
			print("".join(match) + " -", i.title().strip(), " - Type %s then hit RETURN" % n)
			multiple_match_dict[n] = match
			n += 1

		while True:
			match_num = take_input()
			try:
				if int(match_num) in multiple_match_dict.keys():
					add_to_list(i, matches, (int(match_num)-1))
					break
				elif int(match_num) not in multiple_match_dict.keys():	
					print("%s is not one of the available options." % match_num)
					print("Type one of the above numbers then hit RETURN.")
			except:
				print("Not valid. Type one of the above numbers then hit RETURN.")

def end_game():
	print("\n")	
	print("----------------------------------------------------")
	print("-- DING - DING - DING - DING - DING - DING - DING --")
	print("----------------------------------------------------")

	print("\nTime is up! The game is done!")
	time.sleep(1)
	print("Here is your final list:\n")
	time.sleep(1)
	display_inits_as_list()
	print("Thanks for playing, goodbye!")
	exit()

# ----------------- SETUP -------------------- #

# Here we generate the initials we will be using for the game
game_initials = gen_start()

# Here we create an empty ordered dictionary that will store the user's answers
user_dict = OrderedDict()

# And then we add our initials to it
create_user_answer_dict()

# Then we display the timer duration so the player knows how long they are playing
print("And Go! The timer will be up in %s seconds." % timer_duration)
time.sleep(1)

# ---------------- GAMEPLAY ------------------ #

def main_gameplay_loop():
	# First we check if the game is over
	check_for_game_over()
	# Then if not we display initials & answers as a list
	display_inits_as_list()
	# Then we take input for a new name
	print("Input a name:")
	i = take_input()
	# Then we send that input to extraction. 
	# Initial extraction returns tuples of all possible combos of initials 
	# the player could have intended 
	extracted_combos = initial_extraction(i)
	###below used for testing
	###print("here are the possible initial combos:\n", extracted_combos)
	# Input check extracts initials and 
	matches = extraction_check(extracted_combos)
	# Now that we have a list of 0 or more matches, we can move on to match processing.
	if len(matches) < 1:
		no_match_processing()
	elif len(matches) == 1:
		add_to_list(i, matches, 0)
	else:
		multi_match_processing(i, matches)

	main_gameplay_loop()

timer_thread.start()

main_gameplay_loop()