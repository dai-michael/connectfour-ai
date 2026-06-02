from connectfour import check_win_conditions
from connectfour import play_move
from connectfour import print_board
from players import *
import sys
import time
import random
from tqdm import tqdm
import json
from pathlib import Path


def play_game(player1_fn, player2_fn, min_delay=0.2, visualize=True):
    def clear_screen():
        # Clear screen and move cursor to (0,0)
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

    num_rows, num_cols = 6, 7
    board = [0 for _ in range(num_rows * num_cols)]
    moves_made = 0
    current_player = 1
    while check_win_conditions(board) == 0 and moves_made < 42:
        if visualize:
            clear_screen()
            print_board(board)
            print(f"\nplayer {current_player} is thinking...")
        player_fn = player1_fn if current_player == 1 else player2_fn
        start = time.time()
        col = player_fn(board, current_player)
        if visualize:
            elapsed = time.time() - start
            if elapsed < min_delay:
                time.sleep(min_delay - elapsed)
        play_move(board, current_player, col)
        current_player = 2 if current_player == 1 else 1
        moves_made += 1
    winner = check_win_conditions(board)
    if visualize:
        clear_screen()
        print_board(board)
        if winner == 0:
            print("\ntie!")
        else:
            print(f"\nwinner is player {winner}!")
    return winner


def get_data(player1_fn, player2_fn, tracked_player, collect_data=True):
    '''
    Arguments:
        player1/2_fn: Player functions
        tracked_player: int with 1 representing player 1, 2 for player 2
        collect_data: if True, record board states and best moves for tracked player

    Returns tuple:
        winner: winning player (0/1/2)
        data: list of tuples. tuple[0]: boardstate tuple; tuple[1]: 
    '''
    data = []
    num_rows, num_cols = 6, 7
    board = [0 for _ in range(num_rows * num_cols)]
    moves_made = 0
    current_player = 1
    while check_win_conditions(board) == 0 and moves_made < 42:
        player_fn = player1_fn if current_player == 1 else player2_fn
        if collect_data and current_player == tracked_player: # 
            best_moves = player_fn(board, current_player)
            col = random.choice(best_moves)
            data.append((tuple(board),best_moves))
        else:
            col = player_fn(board, current_player)
        play_move(board, current_player, col)

        # Switch who is currently playing
        current_player = 2 if current_player == 1 else 1
        moves_made += 1
    winner = check_win_conditions(board)

    # Modify data:
    if collect_data:
        data = data[-2:] # get last two moves

    return winner,data


def play_tournament(player1_fn, player2_fn, num_rounds):
    p1_wins, p2_wins, ties = 0, 0, 0
    for _ in tqdm(range(num_rounds)):
        winner = play_game(player1_fn, player2_fn, visualize=False) 
        if winner == 0:
            ties += 1
        elif winner == 1:
            p1_wins += 1
        elif winner == 2:
            p2_wins += 1
        winner = play_game(player2_fn, player1_fn, visualize=False)
        if winner == 0:
            ties += 1
        elif winner == 1:
            p2_wins += 1
        elif winner == 2:
            p1_wins += 1
    print(f"P1-P2-T: {p1_wins}-{p2_wins}-{ties}")
    return p1_wins, p2_wins, ties

def get_tournament_data(player1_fn, player2_fn, num_rounds, tracked_player,playbook=None):
    """
    Plays tournament and stores data in playbook 
    Modifies playbook in place when provided
    Arguments:
        player1/2_fn: Player function
        num_rounds: Int number of rounds
        tracked_player: Int tracked player
        playbook: dict (optional):
            key: board
            value: best moves
    Returns: tuple of (p1_wins, p2_wins, ties)
    """
    collect_data = playbook is not None
    p1_wins, p2_wins, ties = 0, 0, 0
    for _ in tqdm(range(num_rounds)):
        winner,data_1=get_data(player1_fn, player2_fn, tracked_player, collect_data)
        if winner == 0:
            ties += 1
        elif winner == 1:
            p1_wins += 1
        elif winner == 2:
            p2_wins += 1


        tracked_player = 2 if tracked_player == 1 else 1 
        winner,data_2=get_data(player2_fn, player1_fn, tracked_player, collect_data)
        if winner == 0:
            ties += 1
        elif winner == 1:
            p2_wins += 1
        elif winner == 2:
            p1_wins += 1
        if playbook is not None:
            data = data_1 + data_2
            for d in data:
                playbook[d[0]] = d[1]
        
        tracked_player = 2 if tracked_player == 1 else 1
            

    print(f"P1-P2-T: {p1_wins}-{p2_wins}-{ties}")
    return p1_wins, p2_wins, ties

def write_to_file(filepath, d):
    """
    Arguments:
    filepath: string of filepath
    d: dictionary representing playbook
        Keys stored as "board", values stored as "moves"
    """
    my_data = []
    for board,best_moves in d.items():
        curr_state = {"board":list(board),"moves":best_moves}
        my_data.append(curr_state)

    with open(filepath,"w") as writer:
        json.dump(my_data,writer)

def import_memo(filepath):
    memo = dict()

    with open(filepath,"r") as f:
        raw_data = json.load(f)
        for object in raw_data:
            # Json cant store tuples, need to convert list back to tuple
            key = (tuple(object["board"][0]), object["board"][1])
            memo[key] = tuple(object["moves"])
    return memo
            

if __name__ == "__main__":
    '''
    Collect data 
    '''

    my_playbook = dict()
    memo = None
    if Path("memo.json").is_file():
        memo = import_memo("memo.json")
    else:
        memo = dict()
    print(len(memo))

    filepath = "data.json"
    # Data is collected through the player function
    my_player_data = initialize_my_player_fn_data(my_playbook,num_plys=4,memo=memo) # my_playbook mutated using player function
    my_player_4ply = initialize_my_player_fn(num_plys=4,memo=memo)
    my_player_1ply = initialize_my_player_fn(num_plys=1,memo=memo)
    my_player_2ply = initialize_my_player_fn(num_plys=2,memo=memo)

    
    #get_tournament_data(my_player_data,random_player_fn,100,1,my_playbook)
    #get_tournament_data(my_player_data,my_player_4ply,50000,1,my_playbook)
    get_tournament_data(my_player_data,my_player_1ply,30,1,my_playbook)
    get_tournament_data(my_player_data,my_player_2ply,30,1,my_playbook)

    write_to_file(filepath,my_playbook)

