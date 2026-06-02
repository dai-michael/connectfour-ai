# AlphaFour

Connect Four AI combining a minimax engine with alpha-beta pruning and a feedforward neural network trained on minimax-generated game data.

Built for Prof. Mark Hopkins' Foundations of AI class at Williams College. 

---

## Components

**`connectfour.py`** — Core game logic: board representation, move execution, and win detection.

**`players.py`** — AI player implementations:
- `random_player_fn` — picks a random valid column
- `_connect_four_eval_fn` — heuristic scoring function (counts threats, positional weight)
- `minimax` — minimax search with alpha-beta pruning and memoization
- `initialize_my_player_fn` — returns a minimax player at a given search depth
- `initialize_my_player_fn_data` — variant that returns all optimal moves (used for data collection)

**`play.py`** — Game infrastructure: `play_game`, tournament runners, and dataset generation.
Run directly to generate training data. Optionally loads a memoization file (`memo.json`) to speed up minimax.

**`use_memo.py`** — Utility script that converts a memoization file into a training dataset. Filters entries by search depth and writes to JSON. Basic but configurable.

**`alphafour.py`** — Neural network: 3-layer feedforward net trained via cross-entropy on minimax-labeled board states. Run directly to train; saves best weights to `params.pt`.

---

## How to Run

### 1. Generate a dataset

```bash
python play.py
```

This runs tournaments between minimax agents and saves board states + optimal moves to `data.json`.
If `memo.json` exists in the directory, it will be loaded automatically to cache minimax results across runs.

Optionally generate data from an existing memo file:

```bash
python use_memo.py
```

### 2. Train the neural network

```bash
python alphafour.py
```

Loads the dataset, trains the network, and saves the best-performing weights to `params.pt`.
Evaluation runs every 10,000 steps and prints win rate against a baseline opponent.

---

## Credits

Code structure and foundational implementation provided by **Professor Mark Hopkins**, CSCI 270. Adapted from course starter code.
