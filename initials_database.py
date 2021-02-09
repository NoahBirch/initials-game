import mysql.connector


class InitialsDatabase:

	def __init__(self):
		self.connection = mysql.connector.connect(
			host="localhost",
			user="monkey2",
			password="bananas",
			database="test")


	def create_game_id(self, user_id):
		mycursor = self.connection.cursor()
		mycursor.execute("INSERT INTO game(host_user_id) VALUES ('%s') " % (user_id))
		self.connection.commit()
		current_game_id = mycursor.lastrowid
		return current_game_id

	def return_list_for_db(self, game_id, valid_user_id, user_dict):
		# This function takes the final user dict of answers and
		# put it in a list for adding to an SQL DB.
		db_return_list = []
		for initial_pair in user_dict:
			db_return_list.append((("".join(initial_pair)), user_dict[initial_pair], game_id, valid_user_id))
		return db_return_list

	def initialize_initials_to_db(self, current_game_id, game_initials):
		initials_to_initialize = []
		for initial_pair in game_initials:
			initials_to_initialize.append((("".join(initial_pair)), current_game_id))
		mycursor = self.connection.cursor()
		sql_answer_format = "INSERT INTO initials_answers (initials, game_id) VALUES (%s, %s)"
		mycursor.executemany(sql_answer_format, initials_to_initialize)
		self.connection.commit()

	def get_initials_from_game_id(self, game_id):
		mycursor = self.connection.cursor()
		mycursor.execute("SELECT initials FROM initials_answers WHERE game_id = %s" % (game_id))
		fetched_inits = mycursor.fetchall()
		game_initials = []
		for inits in fetched_inits:
			game_initials.append(tuple(inits[0]))

		print("heres game initals:", game_initials)
		return game_initials

	def commit_game_answers_to_db(self, current_game_id, valid_user_id, user_dict):
		mycursor = self.connection.cursor()
		sql_answer_format = "INSERT INTO initials_answers (initials, answer, game_id, user_id) VALUES (%s, %s, %s, %s)"
		val_answer = self.return_list_for_db(current_game_id, valid_user_id, user_dict)
		mycursor.executemany(sql_answer_format, val_answer)
		self.connection.commit()

	def check_if_first_game(self, prev_high_score):
		"""Checks the previous high score value passed to it and returns true if its a valid integer, returns false if not"""
		try:
			int(prev_high_score)	
		except:
		 	return True

		return False

	def compare_scores(self, current_game_score, prev_high_score, user_id):
		if current_game_score > prev_high_score:
			return True
		else:
			return False

	def tally_game_score_primitive(self, game_id, user_id):
		# The primitive tally game score method just counts how many names you succesfully commited
		# to your list. No point values assigned in this function. 
		mycursor = self.connection.cursor()
		mycursor.execute("SELECT * FROM initials_answers WHERE game_id = '%s' AND answer <> '' AND user_id = '%s' " % (game_id, user_id))

		score = len(mycursor.fetchall())
		return score

	def get_prev_high_score(self, user_id):
		mycursor = self.connection.cursor()
		mycursor.execute("SELECT high_score FROM users WHERE user_id = '%s' " % user_id)
		prev_high_score = mycursor.fetchone()[0]
		return prev_high_score

	def commit_new_high_score(self, current_game_score, user_id):
		"""This function will commit the current game score to the DB as the high score"""
		mycursor = self.connection.cursor()
		sql = "UPDATE users SET high_score = %s WHERE user_id = %s "
		values = (current_game_score, user_id)
		mycursor.execute(sql, values)
		self.connection.commit()

	def check_user_id(self, user_id_to_check):
		"""For now this function just returns the given user if its valid, exits program if not"""
		mycursor = self.connection.cursor()
		mycursor.execute("SELECT user_id FROM users WHERE user_id = '%s' " % user_id_to_check)
		return mycursor.fetchone()
		
	def create_user_id(self, user_id_to_add):
		mycursor = self.connection.cursor()
		mycursor.execute("INSERT INTO users (user_id) VALUES ('%s')" % (user_id_to_add))
		self.connection.commit()
		return user_id_to_add

	def check_for_open_game(self, user_id, game_id_input):
		"""Returns a match if there is an open game with the inputted game id, returns nothing if not"""
		mycursor = self.connection.cursor()
		mycursor.execute("SELECT game_id FROM game WHERE game_id = %s AND finished = '0' " % (game_id_input))
		return mycursor.fetchone()

	def join_game(self, user_id, game_id):
		"""This gets called if there is a successful opening found in a game. This will add the user id to player 2 in the game."""
		mycursor = self.connection.cursor()
		mycursor.execute("UPDATE game SET player_2_user_id = '%s' WHERE game_id = %s " % (user_id, game_id))
		self.connection.commit()

	def return_all_players_in_game(self, game_id):
		mycursor = self.connection.cursor()
		mycursor.execute("SELECT host_user_id, player_2_user_id FROM game WHERE game_id = %s " % game_id)

		results = mycursor.fetchall()
		self.connection.commit()
		return results

