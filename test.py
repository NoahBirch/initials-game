from initials_database import InitialsDatabase

print_players_in_game(13)

db = InitialsDatabase

def print_players_in_game(game_id):
		print(f"CHECKING GAME {game_id}")
		print(db.return_all_players_in_game(game_id))