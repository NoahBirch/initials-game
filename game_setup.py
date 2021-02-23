from letter_gen import gen_start
import http.client
import sys  
import json
import time

class InitialsSetup:

	def __init__(self,):
		http_server = "127.0.0.1"
		self.conn = http.client.HTTPConnection(http_server, port=5000) 

		self.user_id = self.user_id_loop()
		self.game_id = self.game_mode_prompt()
		#self.game_initials = self.db.get_initials_from_game_id(self.game_id)
		self.game_initials = self.server_to_db_func(server_func= 'DBFUNC_FETCH1', body=("get_initials_from_game_id|"+self.game_id))
		self.game_duration = int(self.server_to_db_func(server_func= 'DBFUNC_FETCH1', body=("get_duration_from_game_id|"+self.game_id)))

	def server_to_db_func(self, server_func, body):
		self.conn.request(server_func, url="", body= body)
		rsp = self.conn.getresponse()
		#print(rsp.status, rsp.reason)  
		return rsp.read().decode("utf-8").strip("\"")

	def user_id_loop(self):
		# First we need to get user input for our possible user id:
		print("Welcome to the initials game! What is your USER ID?")
		print("If you want to check your answers against past answers you need to use the same USER ID.")
		user_id_to_check = input("USER ID: ").strip()

		# Next we check that user input with check_user_id and return an object
		user_id_match = self.server_to_db_func(server_func= 'DBFUNC_FETCH1', body=("check_user_id|"+user_id_to_check))
		if user_id_match == "":
			user_id_match = None

		# Then if that object is empty we know there is no match, so we give the player opportunity to create one.
		if user_id_match == None:
			print("There is no USER ID '%s'" % user_id_to_check)
			print("Would you like to create one?")
			yn = input("type yes or no and hit RETURN.\n>").lower()
			if yn == "yes":

				user_id_to_add = self.server_to_db_func(server_func= 'DBFUNC_FETCH1', body=("create_user_id|"+user_id_to_check))

				print(f"User {user_id_to_add} added! Welcome to the party!")
				valid_user_id = user_id_to_add

			else:
				print("Starting over.")
				self.user_id_loop()
		# If there is a match we know we can continue with the game start process.
		else:
			valid_user_id = user_id_to_check
			print("Great! Welcome back, %s." % user_id_to_check)
		
		return valid_user_id

	def game_mode_prompt(self):
		print("Are you starting a game (single or multiplayer) or trying to join a multiplayer game?")

		game_mode_choice = input("Starting game - Type 1 then hit RETURN\nJoining game - Type 2 then hit RETURN\n> ").strip()
		if game_mode_choice == "1" :
			return self.start_game_route() 
		elif game_mode_choice == "2" :
			return self.join_game_route() # This is the game id of the game they wish to join. 
		else:
			raise

	def start_game_route(self):
		#if the player wants to start a game, we then need to see if they want to play single player or multi.
		#single player option will just start the game. 
		print("Great! so you want to start a game. Do you want to play by yourself or play with other players?")
		 
		game_mode_choice = input("Single player game - Type 1 then hit RETURN\nMultiplayer game - Type 2 then hit RETURN\n> ").strip()
		if game_mode_choice == "1":
			return self.single_player_create_game() # This creates a game id, commits inits to it and returns a game id
		elif game_mode_choice == "2":
			return self.multiplayer_create_game() # This creates a game id, commits inits to it and returns a game id
		else:
			raise

	def join_game_route(self):
		print("So you want to join a game. Thats great!")
		print("Get the game id from your friend and input it below:")
		while True:
			try:
				i = int(input(">"))
				if i <= 0:
					raise
				break
			except:
				print("Thats not a valid entry. Get the game id from your friend and input it below:")

		print(f"Checking for openings in game id: {i}")
 
		open_game_match = self.server_to_db_func(server_func= 'DBFUNC_FETCH1', body=("check_for_open_game|"+str(i)))
		if open_game_match == "":
			open_game_match = None

		if open_game_match != None:
			print("Great! Joining the game.")
			self.game_id = str(i)
			open_game_match = self.server_to_db_func(server_func= 'DBFUNC_FETCH1', body=("join_game|"+self.user_id+"|"+self.game_id))
			print("You have joined the game and now we are waiting for the host to start.\nThe game will start automatically when the host is ready.")
			while True:
				game_start_trigger = self.server_to_db_func(server_func= 'DBFUNC_FETCH1', body=("check_for_game_finished|"+self.game_id))
				if game_start_trigger == "1":
					break
				time.sleep(1)

			print("EVERYONE IS READY! Starting game in:\n3")
			time.sleep(1)
			print("2")
			time.sleep(1)
			print("1")
			time.sleep(1)

			return self.game_id
		else:
			print(f"Sorry, there is no game {i} or it's not joinable at this time.")
			print("Starting you over at the beginning.")
			self.start_game_route()

	def single_player_create_game(self):
		print("Great! A single player game it is. Starting you off now!")
		self.game_id = self.server_to_db_func(server_func= 'DBFUNC_FETCH1', body=("create_game_id|"+self.user_id))
		print ("New game ID created:", self.game_id)

		generated_initials = gen_start()
		generated_initials = "*".join(["".join(x) for x in generated_initials])
		self.server_to_db_func(server_func= 'DBFUNC_FETCH1', body=("initialize_initials_to_db|" + self.game_id + "|" + generated_initials))
		#self.server_to_db_func(server_func= 'DBFUNC_FETCH1', body=("initialize_initials_to_db|"+self.game_id+"|"+generated_initials))
		
		timer_setting = self.timer_initialization()
		self.server_to_db_func(server_func= 'DBFUNC_FETCH1', body=("initialize_duration_to_db|" + self.game_id + "|" + str(timer_setting)))

		return self.game_id

	def multiplayer_create_game(self):
		print("Awesome, so you want to create a multiplayer game.")
		self.game_id = self.server_to_db_func(server_func= 'DBFUNC_FETCH1', body=("create_game_id|"+self.user_id))
		print("New game ID created:", self.game_id)
		print("Now we need to decide what initials the game will play with.")
		print("Because you are starting the game, we will let you decide:")

		generated_initials = gen_start()
		generated_initials = "*".join(["".join(x) for x in generated_initials])
		self.server_to_db_func(server_func= 'DBFUNC_FETCH1', body=("initialize_initials_to_db|" + self.game_id + "|" + generated_initials))
		#self.server_to_db_func(server_func= 'DBFUNC_FETCH1', body=("initialize_initials_to_db|"+self.game_id+"|"+generated_initials))
		
		timer_setting = self.timer_initialization()
		self.server_to_db_func(server_func= 'DBFUNC_FETCH1', body=("initialize_duration_to_db|" + self.game_id + "|" + str(timer_setting)))

		print("Great, your game is setup and we're ready for other players to join.")
		print(f"Have your friend start the game, and enter {self.game_id} when prompted for a game id.")
		print("The user id of players will appear below. Hit RETURN")

		while True:
			print ("Refresh players - type 1 then hit RETURN\nStart game with below players - type 2 then hit RETURN")
			self.print_players_in_game()
			i  = input("> ")
			if i == "1":
				pass
			if i == "2":
				break
		
		self.server_to_db_func(server_func= 'DBFUNC_FETCH1', body=("start_game_mark_finished|" + self.game_id))
		print("OKAY!! Starting game in:\n3")
		time.sleep(1)
		print("2")

		time.sleep(1)
		print("1")
		time.sleep(1)
		return self.game_id

	def print_players_in_game(self):
		print(f"CHECKING GAME {self.game_id}")
		json_string = json.dumps({ 
			"func" : "return_all_players_in_game", 
			"data" : self.game_id
			} )
		current_players = self.server_to_db_func(server_func= 'DBFUNC_1FETCH2', body=json_string)
		current_players = json.loads(current_players)
		current_players = current_players[0]
		print(f"player 1 : {current_players[0]} ")
		print(f"player 2 : {current_players[1]} ")

	def timer_initialization(self):
		while True:
			try: 
				timer_duration = int(input("Finally, how many seconds should the game be played for?\n>"))
				break
			except:
				print("That's not a valid amount of seconds.")
		return timer_duration

		

