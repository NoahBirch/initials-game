import mysql.connector


class InitialsDatabase:
	var connection

def __init__():
	connection = connection()


def connection():
	return mysql.connector.connect(
		host="localhost",
		user="monkey2",
		password="bananas",
		database="test")


def create_game_id():
	mycursor = mydb.cursor()
	mycursor.execute("INSERT INTO game VALUE ()")
	mydb.commit()
	# Now that we have commited this DB change, we need to grab the last row id which will be the game id.
	current_game_id = mycursor.lastrowid
	print ("New game ID created:", current_game_id)
	return current_game_id

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

def return_list_for_db(game_id, valid_user_id):
	# This function takes the final user dict of answers and
	# put it in a list for adding to an SQL DB.
	db_return_list = []
	for initial_pair in user_dict:
		db_return_list.append((("".join(initial_pair)), user_dict[initial_pair], game_id, valid_user_id))
	return db_return_list

def check_if_first_game(prev_high_score):
	"""Checks the previous high score value passed to it and returns true if its a valid integer, returns false if not"""
	try:
		int(prev_high_score)	
	except:
	 	return True

	return False

def compare_scores(current_game_score, prev_high_score, user_id):
	print(f"This game you got {current_game_score} names.")
	print(f"{user_id}\'s previous high score  {prev_high_score} names.")
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
