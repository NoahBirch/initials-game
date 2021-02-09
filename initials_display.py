from initials_database import InitialsDatabase
from initials_game_session import InitialsGameSession
from game_setup import InitialsSetup
import re
import threading
import time
from pynput.keyboard import Key, Controller

keyboard = Controller()

game_over = False


# --------- TIMER STUFF ---------- #

def count_1_sec(duration):
	global game_over
	sec = 0
	while sec < duration:
		sec += 1
		time.sleep(1)

	game_over = True
	keyboard.press(Key.enter)

def timer_initialization():
	while True:
		try: 
			timer_duration = int(input("How many seconds would you like to play?\n>"))
			break
		except:
			print("That's not a valid amount of seconds.")

	return timer_duration


# ----------- GAMEPLAY FUNCTIONS --------------- #

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

	extracted_initials = re.findall(r"(\b[a-zA-Z])", i.replace("'", "").upper())

	# Now because players can input more than just two words, we want to check
	# all the posible combos of initials starting with the first one. 
	# for example "Sarah jessica parker" outputs (S,J) & (S,P)
	initial_combos = []
	
	for num in range(1, len(extracted_initials)):
		possible_combo = (extracted_initials[0],extracted_initials[num])
		initial_combos.append(possible_combo)

	# Now we have the possible combos the player could have intended to add to their answers. 
	# But if they have put "Little Severus Snape" they will get 2 matches of ('L', 'S')
	# So we use this to eliminate duplicates:
	initial_combos = list(dict.fromkeys(initial_combos))

	return initial_combos
	
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
					print("Adding %s to your list." % i)
					game_session.add_answer(i, matches, (int(match_num)-1))
					break
				elif int(match_num) not in multiple_match_dict.keys():	
					print("%s is not one of the available options." % match_num)
					print("Type one of the above numbers then hit RETURN.")
			except:
				print("Not valid. Type one of the above numbers then hit RETURN.")

# ----------------- SETUP -------------------- #

# First part of our gameplay is establishing a db connection and determing what user is playing. InitialsSetup handles this: 
game_setup = InitialsSetup()
db = game_setup.db
user_id = game_setup.user_id

#now we need to determine the game mode and wait for people to join if its multiplayer. 
game_id = game_setup.game_mode_prompt()
print("returned game ID:", game_id)
# Here we generate the initials we will be using for the game
game_initials = db.get_initials_from_game_id(game_id)

# Now that we have our user and our initials, we can start a game session for that user. 
game_session = InitialsGameSession(game_initials, user_id)

# Then we need to see how long the user wants to play and initialize the timer thread.
timer_duration = timer_initialization()
timer_thread = threading.Thread(target=count_1_sec, args=(timer_duration,))

# Then we display the timer duration so the player knows how long they are playing
print("And Go! The timer will be up in %s seconds." % timer_duration)
time.sleep(1)

# ---------------- GAMEPLAY ------------------ #

def main_gameplay_loop():
	# First we check if the game is over
	check_for_game_over()
	# Then if not we display initials & answers as a list
	game_session.display()
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
	matches = game_session.find_matches(extracted_combos)
	# Now that we have a list of 0 or more matches, we can move on to match processing.
	if len(matches) < 1:
		print("Couldn't find a match. Try again.\n")
	elif len(matches) == 1:
		print("Adding %s to your list." % i)
		game_session.add_answer(i, matches, 0)
	else:
		multi_match_processing(i, matches)

	# We loop thru this gameplay, adding names to our list until the endgame is triggered. 
	# Then we move to the end game function below.
	main_gameplay_loop()

def end_game():
	print("\n")	
	print("----------------------------------------------------")
	print("-- DING - DING - DING - DING - DING - DING - DING --")
	print("----------------------------------------------------")

	print("\nTime is up! The game is done!")
	time.sleep(1)
	print("Here is your final list:\n")
	time.sleep(1)
	game_session.display()
	print(f"Thanks for playing, {user_id}! Now we want to add these values to the database.")




	# Now that we have a game ID, we want to insert our game answers to the DB.
	db.commit_game_answers_to_db(game_id, user_id, game_session.user_answers)

	time.sleep(1)

	###### now we go into our answer processing functions. first we get the current game score and past high score from the DB:
	current_game_score = db.tally_game_score_primitive(game_id, user_id)
	prev_high_score = db.get_prev_high_score(user_id)

	# Now we check if this was their first game. This will return true if it is. 
	first_game_tf = db.check_if_first_game(prev_high_score)

	if first_game_tf == True:
		# if its the first game, we know we definitely want to update their score, cause it will be null on default.
		print(f"Looks like this is your first game! Setting your brand new high score of {current_game_score}!")
		db.commit_new_high_score(current_game_score, user_id)
		print("Ending game.")
		exit()
	else:
		pass

	# Now we know there is a past high score, we need to check if the current game  higher than the past hi score.
	# This func will return a true answer if the current game is higher. 
	print(f"This game you got {current_game_score} names.")
	print(f"{user_id}\'s previous high score  {prev_high_score} names.")
	current_game_higher_tf = db.compare_scores(current_game_score, prev_high_score, user_id)

	if current_game_higher_tf == True:
		# if its not a new game we execute this if the current game was higher than the previous high score. 
		print(f"Awesome, looks like {current_game_score} is your new high score! Updating that now!")
		db.commit_new_high_score(current_game_score, user_id)

	else:
		print("Aww man. You failed to beat your previous high score. Maybe next time!")


	exit()

timer_thread.start()

main_gameplay_loop()