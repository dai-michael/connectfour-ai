import torch
from connectfour import *
from play import *
from players import *

def convert_board_state_to_vector(board):
    """
    Arguments: 
    board: list representing boardstate
    (no next move because no longer binary classifier)
    Returns:
      vectored: tensor representing vectorified boardstate
    """
    vectored = torch.zeros(127)
    vectored[0] = 1. # bias

    for i, val in enumerate(board):
        cell_location = i * 3 + 1
        vectored[cell_location + val] = 1
    
    return vectored

def convert_vector_to_board_state(vector):
    """
    Arguments:
        vector: tensor created by convert_board_state_to_vector
    Returns:
        board: list of 42 ints representing board state
    """
    board = []

    for i in range(42):
        cell_start = i * 3 + 1
        cell_vector = vector[cell_start : cell_start + 3]
        cell_value = torch.argmax(cell_vector).item() # .item converts to integer
        board.append(cell_value)

    return board



def load_training_data(data):
    '''
    Arguments:
    data: dictionary of training data
    data example: {
        (1, 2, 0, 0, 0, 1, 2, 0, 0): [4, 8],
        (0, 0, 2, 1, 2, 1, 1, 1, 2): [0],
    
    Returns: 
    x: tensor of boardstates
    y: tensor of move probabilities
    }'''
    x = []
    y = []

    for board,optimal_moves in list(data.items()):
        x.append(list(convert_board_state_to_vector(board)))
        y_entry = torch.zeros(7)

        # Set up 7 way output
        for j in range(7):
            if board[j] == 0: # open column
                if j in optimal_moves:
                    y_entry[j] = 1/len(optimal_moves) if len(optimal_moves) > 0 else 0
        y.append(y_entry)
    
    x = torch.tensor(x)
    y = torch.stack(y)
    return x,y

def initialize_params(input_dim=127, hidden_dim=200): # optimal: h: 200, c: 64
    compressed_dim=100 # 100 / 90
    theta1 = torch.zeros(hidden_dim, input_dim)
    theta2 = torch.zeros(compressed_dim, hidden_dim) # Later layers can turn info into higher level features
    theta3 = torch.zeros(7, compressed_dim)
    for theta in [theta1, theta2, theta3]:
        theta.uniform_(-0.4, 0.4)
        theta.requires_grad = True
    return {"theta1": theta1, "theta2": theta2, "theta3": theta3}

def run_neural_net(parameters, x):
    theta1 = parameters["theta1"]
    theta2 = parameters["theta2"]
    theta3 = parameters["theta3"]

    if x.dim() == 1:
        x = x.unsqueeze(0)

    z1 = x @ theta1.T 
    x1 = torch.relu(z1)

    z2 = x1 @ theta2.T
    x2 = torch.relu(z2)


    z3 = x2 @ theta3.T
    u = torch.softmax(z3, dim = 1)
    return u.squeeze()



def compute_loss(output, y):
    output = torch.clamp(output, min=1e-13)  # avoid log(0) = -inf
    loss_per_output = -torch.sum(y * torch.log(output), dim=1)
    return torch.mean(loss_per_output)


def compute_nn_accuracy(parameters, x, y):
    preds = run_neural_net(parameters,x)

    preds_differences = torch.abs((y-preds))
    accuracy = torch.mean(1-preds_differences)

    return accuracy


def evaluate_neural_net(parameters, x, y,playbook=None,opp_num_plys=4):
    """
    Evaluates neural net
    Arguments: 
        parameters: tensor of neural net parameters 
        x,y: tensor of x and y values
        playbook: dictionary of best plays, if constructing playbook
        opp_num_plys: int number of plys for opponent
    Returns:
        wins: integer number of wins of ai_player
    """
    accuracy = compute_nn_accuracy(parameters, x, y)
    ai_player_fn = create_nn_player_fn(parameters)
    # test_player = initialize_my_player_fn(num_plys=1)
    if playbook is not None:
        test_player = initialize_my_player_fn_data(playbook,num_plys=opp_num_plys, return_best_moves=False)
    else:
        #test_player = initialize_my_player_fn(num_plys=opp_num_plys)
        test_player = random_player_fn
    wins, losses, ties = get_tournament_data(ai_player_fn, test_player,500,2)
    #play_game(ai_player_fn,test_player)
    accuracy_msg = f"Train accuracy: {accuracy: .3f}"
    tournament_msg = f"Tournament performance: {wins}-{losses}-{ties}"
    print(accuracy_msg + "; " + tournament_msg)
    return wins


def create_nn_player_fn(parameters):
    def my_player_fn(board,_):
        x = convert_board_state_to_vector(board)
        y = run_neural_net(parameters,x)

        for i in range(7):
            if board[i] != 0:
                y[i] = -float("inf")
        return torch.argmax(y).item()
    
    return my_player_fn

def load_my_ai():
    return create_nn_player_fn(torch.load("params.pt", weights_only=True))

def import_training_data_to_dict(filepath):
    import json
    data = dict()

    with open(filepath, "r") as f:
        raw_data = json.load(f)
        for object in raw_data:
            data[tuple(object["board"])] = object["moves"]
            
    return data


def train_model(num_steps=5000000, learning_rate=0.02, batch_size=100, opp_num_plys = 3, playbook = None):
    filepath = "data.json"
    # filepath = "minimax/starter/test_1plyand2ply.json"
    data = import_training_data_to_dict(filepath)
    print(len(data))

    X_train, y_train = load_training_data(data)
    parameters = initialize_params()
    batch_start = 0
    max_wins = 0
    wins = 0
    for step in range(num_steps):
        if step % 10000 == 0:  # we evaluate every 5000 steps
            wins = evaluate_neural_net(parameters, X_train, y_train,playbook, opp_num_plys)

        if wins > max_wins:
            print("new best performance! wins: ", wins)
            torch.save(parameters,'params.pt')
            max_wins = wins

        X_batch = X_train[batch_start : batch_start + batch_size, :]
        y_batch = y_train[batch_start : batch_start + batch_size]
        output = run_neural_net(parameters, X_batch)
        loss = compute_loss(output, y_batch)
        loss.backward()
        with torch.no_grad():
            for theta in parameters.values():
                theta -= learning_rate * theta.grad
                theta.grad = None
        batch_start = (batch_start + batch_size) % X_train.shape[0]


if __name__ == "__main__":
    train_model(opp_num_plys=1)




