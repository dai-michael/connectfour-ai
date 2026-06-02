import random
import connectfour

def random_player_fn(board, player):
    """
    Arguments:
        board: list of 42 ints representing board state (0=empty, 1=red, 2=yellow)
        player: int representing current player (1 or 2)
    Returns:
        col: int column index of randomly chosen valid move, or None if board is full
    """
    num_cols = 7
    valid_moves = [i for i in range(num_cols) if board[i] == 0]
    if len(valid_moves) == 0:
        return None
    else:
        return random.choice(valid_moves)


def _connect_four_eval_fn(board, player):
    """
    Arguments:
        board: list of 42 ints representing board state (0=empty, 1=red, 2=yellow)
        player: int representing the player to evaluate for (1 or 2)
    Returns:
        eval: int heuristic score; positive values favor player, negative values favor opponent
    """
    eval = 0
    my_winning_locations = [] # Keep track of winning locations for three in a row to truly check for double threats
    opp_winning_locations = [] # These lists keep track of only playable winning locations, unlike eval which is all possible moves
    three_row_reward = 10000

    def is_possible(location):
        '''If a location can be immediately occupied assuming it is currently unoccupied'''
        if location > 34:
            return True
        if board[location+7] != 0:
            return True
        return False

    def potential_4row_logic(rg, sign, curr_player):
        """
        Arguments:
            rg: range object of 4 board indices representing a potential connect-four window
            sign: int 1 if evaluating for player, -1 if evaluating for opponent
            curr_player: int player whose pieces are being counted (1 or 2)
        Returns:
            curr_eval: int score contribution from this window
        """
        curr_eval = 0
        open_positions = [j for j in rg if board[j] == 0]
        num_curr = [board[j] for j in rg].count(curr_player)
        if all(is_possible(pos) for pos in open_positions):
            curr_eval = num_curr ** 2 * sign
        if num_curr == 3:
            winning_location = open_positions[0]
            if is_possible(winning_location):
                if sign == 1: my_winning_locations.append(winning_location)
                else: opp_winning_locations.append(winning_location)
        return curr_eval

    opponent = 2 if player == 1 else 1
    for curr_player, sign in ((player, 1), (opponent, -1)):
        for i in range(len(board)):
            if i % 7 in (0,1,2,3):
                # scan right horizontal (covers all possible combos dont need to check left)
                rg = range(i,i+4)
                if all(board[j] in (curr_player,0) for j in rg) and any(board[j] == curr_player for j in rg):
                    eval += potential_4row_logic(rg, sign, curr_player)
            if i // 7 > 2:
                # scan bottom four pieces
                rg = range(i,i-22,-7)
                if all(board[j] in (curr_player,0) for j in rg) and any(board[j] == curr_player for j in rg):
                    eval += potential_4row_logic(rg, sign, curr_player)
            if i in (0,1,2,3,7,8,9,10,14,15,16,17):
                # scan right diagonal
                rg = range(i,i+25,8)
                if all(board[j] in (curr_player,0) for j in rg) and any(board[j] == curr_player for j in rg):
                    eval += potential_4row_logic(rg, sign, curr_player)
            if i in (3,4,5,6,10,11,12,13,17,18,19,20):
                # scan left diagonal
                rg = range(i,i+19,6)
                if all(board[j] in (curr_player,0) for j in rg) and any(board[j] == curr_player for j in rg):
                    eval += potential_4row_logic(rg, sign, curr_player)

    # Not logically robust but for some reason performs better than other solution
    eval += len(my_winning_locations) * three_row_reward - len(opp_winning_locations) * three_row_reward
    return eval


def minimax(board, eval_fn, whose_turn, who_am_i, num_plys, memo = None):
    """
    Arguments:
        board: list of 42 ints representing board state (0=empty, 1=red, 2=yellow)
        eval_fn: function(board, player) -> int heuristic used when num_plys reaches 0
        whose_turn: int player whose turn it is at the current node (1 or 2)
        who_am_i: int player being optimized for (maximizing player)
        num_plys: int number of plies (half-moves) to search ahead
        memo: dict mapping (board_tuple, num_plys) -> (utility, best_moves) for caching
    Returns:
        tuple of (utility, best_moves) where utility is int and best_moves is list of int column indices
    """
    if memo == None:
        memo = dict()

    def minimax_helper(board, whose_turn, num_plys, alpha, beta):
        """
        Arguments:
            board: list of 42 ints representing current board state
            whose_turn: int player to move at this node (1 or 2)
            num_plys: int remaining depth to search
            alpha: float best guaranteed utility for who_am_i found so far (for pruning)
            beta: float best guaranteed utility for opponent found so far (for pruning)
        Returns:
            tuple of (utility,) at terminal/leaf nodes, or (utility, best_moves) otherwise
        """
        # base cases: (does not return move because will never be allowed to directly input board that allows this)
        win = connectfour.check_win_conditions(board)
        if win != 0:
            if win == who_am_i:
                return (float('inf'),)
            return (-float('inf'),)

        available_columns = [i for i in range(7) if board[i] == 0]

        # no more possible moves 
        if len(available_columns) == 0:
            return (0,)
        
        # max plys reached (use eval function)
        if num_plys == 0:
            return (eval_fn(board,who_am_i),)

        if (tuple(board),num_plys) in memo:
            return memo[(tuple(board),num_plys)]
        
        sorted_columns = []
        for column in available_columns: # originally used eval func to sort but took too long 
            new_board = board.copy()
            connectfour.play_move(new_board,whose_turn,column)
            if column == 3: eval = 1
            elif column in (2,4): eval = 2
            elif column in (1,5): eval = 3
            else: eval = 4
            sorted_columns.append((eval,column))

        sorted_columns.sort(key=lambda x: x[0])
        sorted_columns = [x[1] for x in sorted_columns]

        # Recursion on all possible moves - alpha beta is only passed down, not up. alpha beta recomputed when higher
        potential_utilities = dict()
        for column in sorted_columns:
            new_board = board.copy()
            connectfour.play_move(new_board,whose_turn,column)
            next_turn = 1 if whose_turn == 2 else 2
            curr_utility = minimax_helper(new_board, next_turn, num_plys - 1, alpha, beta)[0]
            potential_utilities[column] = curr_utility
            
            if whose_turn == who_am_i: # modify alpha if max layer
                alpha = max(curr_utility, alpha)
            else: # modify beta if min layer
                beta = min(beta, curr_utility)
            
            # pruning (if either beta set too high or alpha set too high)
            if alpha > beta: 
                break

        if whose_turn == who_am_i: # max layer
            max_utility = max(potential_utilities.values())
            best_moves = [column for column in potential_utilities if potential_utilities[column] == max_utility]
            memo[(tuple(board),num_plys)] = (max_utility,best_moves)
            return (max_utility,best_moves)
        else: # min layer
            min_utility = min(potential_utilities.values())
            best_moves = [column for column in potential_utilities if potential_utilities[column] == min_utility]
            memo[(tuple(board),num_plys)] = (min_utility,best_moves)
            return (min_utility,best_moves)

    return minimax_helper(board,whose_turn,num_plys,float('-inf'),float('inf'))


def initialize_my_player_fn(num_plys=5,memo=None):
    """
    Arguments:
        num_plys: int number of plies to search ahead
        memo: dict for caching minimax results across calls; created fresh if None
    Returns:
        my_player_fn: function(board, player) -> int column index of chosen move
    """
    if memo == None:
        memo = dict()
    eval_fn = _connect_four_eval_fn

    def my_player_fn(board, player):
        best_moves = minimax(board,eval_fn,player,player,num_plys,memo)[1] # list of best moves
        move = random.choice(best_moves)
        return move
            
    return my_player_fn

def initialize_my_player_fn_data(my_playbook=None,num_plys=5, memo=None, return_best_moves=True):
    """
    Prepares player function with changes allowing memoization and data collection
    Does not modify playbook
    
    Arguments:
        my_playbook: dict representing optimal playbook
        num_plys: int number of plys of player
        memo: dict of memoized boardstates with extra information for minimax
            Key: tuple of tuple: boardstate, int: num_plys
            Value: Tuple of int: utility, int: best_moves
        return_best_moves: if True, return list of best moves (for data collection);
            if False, return a single randomly chosen best move (for gameplay)
    Returns: 
        Returns player function
        Player function returns: returns list of back moves as opposed to single best move
        for data collection purposes
    """
    if memo == None:
        memo = dict()
    eval_fn = _connect_four_eval_fn

    def my_player_fn(board, player):
        best_moves = []
        if my_playbook is not None and tuple(board) in my_playbook:
            best_moves = my_playbook[tuple(board)]
        else:
            best_moves = minimax(board,eval_fn,player,player,num_plys,memo)[1] # list of best moves
        if return_best_moves:
            return best_moves
        return random.choice(best_moves)
            
    return my_player_fn


if __name__ == "__main__":
    test_board = [0 for i in range(42)]
    test_board[35] = 1
    test_board[36] = 1
    test_board[37] = 1


    def test_eval_fn(board,player): 
        return 0
    print(minimax(test_board, test_eval_fn, 1,1,1))