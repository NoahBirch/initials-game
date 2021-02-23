import random

def a_to_z():
	"""Outputs a set of letters as single characters a thru z."""
	letters_for_splitting = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z"
	split_a_to_z = letters_for_splitting.split(' ')
	return split_a_to_z

def random_a_to_z():
	"""Outputs a set of letters a thru z then scrambles it randomly."""
	letters_for_splitting = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z"
	rand_split_a_to_z = letters_for_splitting.split(' ')
	random.shuffle(rand_split_a_to_z)
	return rand_split_a_to_z

def sentence():
	"""Outputs a set of letters from a sentence in order pulled from a .txt file"""
	while True:
		open_text = open("christmas_carol.txt")
		read_whole_text = open_text.read()
		length_of_text = int(len(read_whole_text))
		# This determines a random spot to grab 100 characters from
		# and ensures it does so before the end of the file.
		start_of_100char = (random.randint(1, (length_of_text - 100)))
		open_text.seek(start_of_100char)
		try:
			str_100_char = str(open_text.read(100))
			break
		except:
			open_text.close()

	open_text.close()
	# This finds where the first space occurs. 
	first_space = str_100_char.find(" ") + 1
	# This trims the string from the first space spot to the end. -1 is shorthand for the end of a list.
	str_100_char = str_100_char[first_space : -1]
	# This converts all the characters to upper case
	str_100_char = str_100_char.upper()

	# Create a new list which will hold only alphabetical characters. 
	wanted_chars = []

	for search_char in str_100_char:
		if search_char == "A":
			wanted_chars.append(search_char)
		elif search_char == "B":
			wanted_chars.append(search_char)
		elif search_char == "C":
			wanted_chars.append(search_char)
		elif search_char == "D":
			wanted_chars.append(search_char)
		elif search_char == "E":
			wanted_chars.append(search_char)
		elif search_char == "F":
			wanted_chars.append(search_char)
		elif search_char == "G":
			wanted_chars.append(search_char)
		elif search_char == "H":
			wanted_chars.append(search_char)
		elif search_char == "I":
			wanted_chars.append(search_char)
		elif search_char == "J":
			wanted_chars.append(search_char)
		elif search_char == "K":
			wanted_chars.append(search_char)
		elif search_char == "L":
			wanted_chars.append(search_char)
		elif search_char == "M":
			wanted_chars.append(search_char)
		elif search_char == "N":
			wanted_chars.append(search_char)
		elif search_char == "O":
			wanted_chars.append(search_char)
		elif search_char == "P":
			wanted_chars.append(search_char)
		elif search_char == "Q":
			wanted_chars.append(search_char)
		elif search_char == "R":
			wanted_chars.append(search_char)
		elif search_char == "S":
			wanted_chars.append(search_char)
		elif search_char == "T":
			wanted_chars.append(search_char)
		elif search_char == "U":
			wanted_chars.append(search_char)
		elif search_char == "V":
			wanted_chars.append(search_char)
		elif search_char == "W":
			wanted_chars.append(search_char)
		elif search_char == "X":
			wanted_chars.append(search_char)
		elif search_char == "Y":
			wanted_chars.append(search_char)
		elif search_char == "Z":
			wanted_chars.append(search_char)
		else:
			continue

	# This trims the list down to 26 characters.
	wanted_chars = wanted_chars[0:26]

	return wanted_chars

def gen_start():

	left_column = left_column_select()

	print("""\nGreat! Your left column is set.""")

	right_column = right_column_select()

	print("\nGreat! Thanks for setting your game initials.")

	game_initials = zip(left_column, right_column)
	return game_initials
	#for pair in output_pairs:
	#	print pair
	#print "\n"

#This is for if you just want to test the program. 
#gen_start()
def left_column_select():
	print("""\nHello! Welcome to initials generation.
What would you like for your LEFT column?:\n
1 - A-Z characters in alphabetical order
2 - A-Z characters in random order
3 - A sentence selected at random from 'A Christmas Carol' by Charles Dickens\n""")
	while True:
		i = input("> ")
		if i == "1":
			return a_to_z()		
		elif i == "2":
			return random_a_to_z()
		elif i == "3":
			return sentence()
		else:
			print("Invalid answer. type 1, 2 or 3 and hit RETURN.")
		
def right_column_select():
	print("""\nHello! Welcome to initials generation.
What would you like for your RIGHT column?:\n
1 - A-Z characters in alphabetical order
2 - A-Z characters in random order
3 - A sentence selected at random from 'A Christmas Carol' by Charles Dickens\n""")
	while True:
		i = input("> ")
		if i == "1":
			return a_to_z()		
		elif i == "2":
			return random_a_to_z()
		elif i == "3":
			return sentence()
		else:
			print("Invalid answer. type 1, 2 or 3 and hit RETURN.")
		
