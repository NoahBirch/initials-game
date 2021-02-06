from letter_gen import gen_start
from collections import OrderedDict
import re
import threading
import time
from pynput.keyboard import Key, Controller
import mysql.connector

keyboard = Controller()

game_over = False

# --------- SQL DB SETUP ---------- #

mydb = mysql.connector.connect(
	host="localhost",
	user="monkey2",
	password="bananas",
	database="test"
)

# ------------ DB FUNCTIONS ----------------- #
def commit_game_answers_to_db(current_game_id, valid_user_id):
	mycursor = mydb.cursor()
	# The SQL format line below dictates how we are going to execute one SQL command with the 
	# data we give it. We have 3 columns we are affecting in the initials_answers table.
	# initials, answer, and game_id.
	sql_answer_format = "INSERT INTO initials_answers (initials, answer, game_id, user_id) VALUES (%s, %s, %s, %s)"
	# Now that we have the format we are passing into an SQL command, 
	# we need the data. we are getting this from the return_list_for_db function
	# and we need to pass it the game id we just got. 
	val_answer = return_list_for_db(current_game_id, valid_user_id)

	# Now that we have our SQL command format and our data setup, we can use the execute many command.
	# It will execute as many times as the amount of data we pass it in the val_answer list. 
	mycursor.executemany(sql_answer_format, val_answer)
	mydb.commit()
	print(mycursor.rowcount, "rows were inserted!")

def create_game_id():
	mycursor = mydb.cursor()
	mycursor.execute("INSERT INTO game VALUE ()")
	mydb.commit()
	# Now that we have commited this DB change, we need to grab the last row id which will be the game id.
	current_game_id = mycursor.lastrowid
	print ("New game ID created:", current_game_id)
	return current_game_id

def check_if_first_game(prev_high_score):
	"""Checks the previous high score value passed to it and returns true if its a valid integer, returns false if not"""
	try:
		int(prev_high_score)	
	except:
	 	return True

	return False

def compare_scores(current_game_score, prev_high_score, user_id):
	print(f"This game you got {current_game_score} names.")
	print(f"{user_id}\'s previous high score is {prev_high_score}")
	if current_game_score > prev_high_score:
		return True
	else:
		return False

def tally_game_score_primitive(game_id, user_id):
	# The primitive tally game score method just counts how many names you succesfully commited
	# to your list. No point values assigned in this function. 
	mycursor = mydb.cursor()
	mycursor.execute("SELECT * FROM initials_answers WHERE game_id = '%s' AND answer <> '' AND user_id = '%s' " % (game_id, user_id))

	score = len(mycursor.fetchall())
	return score

def get_prev_high_score(user_id):
	mycursor = mydb.cursor()
	mycursor.execute("SELECT high_score FROM users WHERE user_id = '%s' " % user_id)
	prev_high_score = mycursor.fetchone()[0]
	return prev_high_score

def commit_new_high_score(current_game_score, user_id):
	"""This function will commit the current game score to the DB as the high score"""
	mycursor = mydb.cursor()
	sql = "UPDATE users SET high_score = %s WHERE user_id = %s "
	values = (current_game_score, user_id)
	mycursor.execute(sql, values)
	mydb.commit()


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

# ----------- SETUP FUNCTIONS --------------- #

def create_user_answer_dict():
	# We need this function so we can create a blank dictionary
	# where the players answers will be stored. 
	for initial_pair in game_initials:
		user_dict[initial_pair] = ""

# ------------ GAME START FUNCTIONS --------------- #

def user_id_loop():
	# First we need to get user input for our possible user id:
	user_id_to_check = get_user_id()
	# Next we check that user input with check_user_id and return an object
	user_id_match = check_user_id(user_id_to_check)
	# Then if that object is empty we know there is no match, so we give the player opportunity to create one.
	if user_id_match == None:
		print("There is no USER ID '%s'" % user_id_to_check)
		print("Would you like to create one?")
		yn = input("type yes or no and hit RETURN.\n>").lower()
		if yn == "yes":
			create_user_id_check(user_id_to_check)
		else:
			print("Starting over.")
			user_id_loop()
	# If there is a match we know we can continue with the game start process.
	else:
		print("Great! Welcome back, %s." % user_id_to_check)

	return user_id_to_check

def get_user_id():

	print("Welcome to the initials game! What is your USER ID?")
	print("If you want to check your answers against past answers you need to use the same USER ID.")
	user_id_to_check = input("USER ID: ").strip()
	return user_id_to_check

def check_user_id(user_id_to_check):
	"""For now this function just returns the given user if its valid, exits program if not"""
	mycursor = mydb.cursor()

	mycursor.execute("SELECT user_id FROM users WHERE user_id = '%s' " % user_id_to_check)

	return mycursor.fetchone()
	
def create_user_id_check(user_id_to_add):
	print('%r' % user_id_to_add)
	mycursor = mydb.cursor()
	mycursor.execute("INSERT INTO users (user_id) VALUES ('%s')" % (user_id_to_add))
	mydb.commit()
	print(f"User {user_id_to_add} added! Welcome to the party!")
	time.sleep(1)


# ----------- GAMEPLAY FUNCTIONS --------------- #

def display_inits_as_list():
	# This function displays the users dictionary and any new additions
	# they have made eveyrtime it is called. 
	for initial_pair in user_dict:
		print("".join(("".join(initial_pair) + " - ", user_dict[initial_pair])))

def return_list_for_db(game_id, valid_user_id):
	# This function takes the final user dict of answers and
	# put it in a list for adding to an SQL DB.
	db_return_list = []
	for initial_pair in user_dict:
		db_return_list.append((("".join(initial_pair)), user_dict[initial_pair], game_id, valid_user_id))
	return db_return_list

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

# ----------------- SETUP -------------------- #

# First part of our gameplay is finding out which user is playing. 
# The below loop runs and only returns a valid user id whether one is created or
# a user is returning. 
valid_user_id = user_id_loop()

# Here we generate the initials we will be using for the game
game_initials = gen_start()

# Here we create an empty ordered dictionary that will store the user's answers
user_dict = OrderedDict()

# And then we add our initials to it
create_user_answer_dict()

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
	display_inits_as_list()
	print(f"Thanks for playing, {valid_user_id}! Now we want to add these values to the database.")


	# Now to start adding to the DB, we first need to create a game ID.
	current_game_id = create_game_id()

	# Now that we have a game ID, we want to insert our game answers to the DB.
	commit_game_answers_to_db(current_game_id, valid_user_id)

	time.sleep(1)

	###### now we go into our answer processing functions. first we get the current game score and past high score from the DB:
	current_game_score = tally_game_score_primitive(current_game_id, valid_user_id)
	prev_high_score = get_prev_high_score(valid_user_id)

	# Now we check if this was their first game. This will return true if it is. 
	first_game_tf = check_if_first_game(prev_high_score)

	if first_game_tf == True:
		# if its the first game, we know we definitely want to update their score, cause it will be null on default.
		print(f"Looks like this is your first game! Setting your brand new high score of {current_game_score}!")
		commit_new_high_score(current_game_score, valid_user_id)
		print("Ending game.")
		exit()
	else:
		pass

	# Now we know there is a past high score, we need to check if the current game  higher than the past hi score.
	# This func will return a true answer if the current game is higher. 
	current_game_higher_tf = compare_scores(current_game_score, prev_high_score, valid_user_id)

	if current_game_higher_tf == True:
		# if its not a new game we execute this if the current game was higher than the previous high score. 
		print(f"Awesome, looks like {current_game_score} is your new high score! Updating that now!")
		commit_new_high_score(current_game_score, valid_user_id)

	else:
		print("Aww man. You failed to beat your previous high score. Maybe next time!")


	exit()

timer_thread.start()

main_gameplay_loop()