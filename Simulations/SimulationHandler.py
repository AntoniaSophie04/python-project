import random
import numpy as np
import pandas as pd
import sys
import os
#need file to be able to see the Game and Strategies folders to run it driectly
current_dir = os.path.dirname(os.path.abspath(__file__))  
parent_dir = os.path.dirname(current_dir)                  
sys.path.insert(0, parent_dir)

from Strategies.RandomStrategy import RandomStrategy
from Strategies.GreedyStrategy import GreedyStrategy
from Strategies.MCTS import MCTSStrategy
from Strategies.safe_choice_strategy import SafeChoiceStrategy
from Strategies.minimax_f import AlphaBetaStrategy
from Game.Player import Player




class SimulationEngine:
    """
    need a new class that can run an entire game from start to finish in memory, without opening any windows
    """
    def __init__(self, player1, player2, board_matrix):
        """
        initializes a new game 
        """
        self.players = [player1, player2]       #store players in list
        self.matrix = np.copy(board_matrix)     #create copy of the board to not modify original matrix
        self.dim = len(self.matrix)             #store dim of board
        self.score = [0, 0]                     #initialize score count
        self.current_player = 0                 #start game with player 1
        self.last_move = None                   #no moves yet-> initializes last move made with None

    def get_available_moves(self):
        """
        find all valid moves for the current player
        """
        moves = []
        
        #first move-> everything is possible-> iterate over entire board and assure no move already taken
        if self.last_move is None:
            for r in range(self.dim):
                for c in range(self.dim):
                    if self.matrix[r][c] != "-": 
                        moves.append((r, c))
            return moves

        #subsequent moves
        last_r, last_c = self.last_move

        #same column
        for r in range(self.dim):
            if self.matrix[r][last_c] != "-":
                moves.append((r, last_c))
        
        #same row, assure to add the intersection a second time
        for c in range(self.dim):
            if c != last_c and self.matrix[last_r][c] != "-": 
                moves.append((last_r, c))
        
        return moves

    def run_game(self):
        """
        run until no moves are left, return final score and winner
        """

        while True:
            #find all moves based on current board
            available_moves = self.get_available_moves()
            
            #if no moves available-> end
            if not available_moves:
                break

            #get current player
            player = self.players[self.current_player]

            #ask AI strategy to choose a move 
            move = player.move(self.matrix, self.last_move, self.score) 

            #if move is non legal-> return VAlue Error
            if move not in available_moves:
                raise ValueError(f"Non-available move by player {self.current_player}.")
                            
            #devide returned move in coordinates
            row, col = move

            #get value from chosen move and add to player's score
            value = self.matrix[row][col]
            self.score[self.current_player] += value
            
            #mark cell as taken and store the move as last taken move
            self.matrix[row][col] = "-" 
            self.last_move = (row, col)

            # switch players
            self.current_player = 1 - self.current_player 


        #left loop-> can determine a winner
        p1_score = self.score[0]
        p2_score = self.score[1]
        
        winner = "Tie"
        if p1_score > p2_score:
            winner = "P1"
        elif p2_score > p1_score:
            winner = "P2"
            
        #return result in dic
        return {"p1_score": p1_score,"p2_score": p2_score,"winner": winner}
    


def create_random_board(size):
    """
    geenerate random NxN board for the simulation
    """
    #create list of lists
    matrix = [[random.randint(1, 9) for length in range(size)] for width in range(size)]
    #convert to array with object type, so will be able to store '-' for used fields
    return np.array(matrix, dtype=object)

def create_strategy(name):
    """
    match string names to the strategies
    """
    if name == "Random": return RandomStrategy()
    if name == "Greedy": return GreedyStrategy()
    if name == "SafeChoice": return SafeChoiceStrategy()
    if name == "MCTS": return MCTSStrategy()
    if name == "Minimax": return AlphaBetaStrategy()
    raise ValueError(f"{name}-strategy not existent for game")


class SimulationRunner:
    def __init__(self, number_of_simulations=None, strategies=None, board_dims=None):
        """
        initialize one simulation run
        """
        if strategies is None:
            strategies= ["Random", "Greedy", "SafeChoice", "MCTS", "Minimax"]

        if board_dims is None:
            board_dims = [3,5,6,8,9]       #decide for small medium and large games of even and odd row/col numbers

        self.strategies= strategies                         #which strategies to be used
        self.number_of_simulations= number_of_simulations   #set the number of simulations to 100 for each board dimension
        self.results= []                #initialize list with results (Win, Loss, Tie)
        self.board_dim =board_dims      


    def run_match(self,board_dim, P1_strat, P2_strat, set_of_boards):
        """
        run one single match up of competing strategy pairs, but both of them get first mover advantage once-> check how performance
        is as 1. and 2. player
        """
        
        #initialize wins and ties:
        total_wins_Strat1_as_Player1= 0
        total_wins_Strat1_as_Player2 =  0
        total_ties = 0
        total_starter_wins = 0  #to track first-mover advantage

        #iterate through pre-generated boards, so that the strategies can play the exact same boards twice 
        for board in set_of_boards:
            #1.game: strategy 1 is player 1 and strategy 2 is player 2
            #set up game with random board, creating player with their strategies
            engine1 = SimulationEngine(Player(P1_strat, False, create_strategy(P1_strat)),
                              Player(P2_strat, False, create_strategy(P2_strat)),
                              np.copy(board))
            
            #run game simulation to completion and give winner the point
            result1 = engine1.run_game()
        
            if result1["winner"] == "P1": 
                total_wins_Strat1_as_Player1 += 1
                total_starter_wins += 1
            elif result1["winner"] == "Tie": 
                total_ties += 1 

            #2. game: strategy 1 is player 2 and strategy 2 is player 1
            engine2 = SimulationEngine(Player(P2_strat, False, create_strategy(P2_strat)),
                              Player(P1_strat, False, create_strategy(P1_strat)),
                              np.copy(board))
            result2 = engine2.run_game()

            if result2["winner"] == "P2": 
                total_wins_Strat1_as_Player2 += 1 
            elif result2["winner"] == "P1":  #starter strategy 2 wins
                total_starter_wins += 1
            elif result2["winner"] == "Tie": 
                total_ties += 1
        
        #get number of games played: N=400 as player 1 and N=400 as player 2
        total_sims_per_role = len(set_of_boards)
        total_games_played = 2 * total_sims_per_role 

        #return key stats
        return {"board_size": board_dim, "S1": P1_strat, "S2": P2_strat, "S1_win_rate_as_P1": total_wins_Strat1_as_Player1 / total_sims_per_role,
            "S1_win_rate_as_P2": total_wins_Strat1_as_Player2 / total_sims_per_role, "total_tie_rate": total_ties / total_games_played, 
            "starter_win_rate" : total_starter_wins / (total_games_played - total_ties)}


    def run_iteration(self):
        """
        iterate through board dimensions and strategies
        """
       
        for size in self.board_dim:
            print(f"{size}x{size}")
            #generate all boards per size to ensure fair match ups
            boards_set = [create_random_board(size) for simulation in range(self.number_of_simulations)]

            #iterate through strategies, while avoiding duplicate pairs (A,B) and (B,A)
            for index1, strategy1 in enumerate(self.strategies):
                for index2, strategy2 in enumerate(self.strategies):
                    #avoid duplication
                    if index1>= index2: continue
                    
                    #run the games on fixed boards for fairness
                    data = self.run_match(size, strategy1, strategy2, boards_set)
                    #append the generated results to the result list
                    if data:
                        self.results.append(data)
    
    def save_results(self, filename="simulation_results.csv"):
        """
        saves hte simulation results as csv and exports
        """
        df = pd.DataFrame(self.results)
        #define directory to same folder (simulations)
        out_dir = os.path.join(current_dir, "results") 
        os.makedirs(out_dir, exist_ok=True)
        
        csv_path = os.path.join(out_dir, filename)
        df.to_csv(csv_path, index=False)


#execute simulation by calling functions
#choose simulation number as follows:
#treat each game as Bernoulli trial with two outcomes: win /loss
#p(1-p) is maximized when p=0.5-> worst-case variance
#Constructing a 95% confidence Interval:
#N=0.25(0.051.96​)^2=384.16 -> 384 independent games are needed per matchup to estimate the win rate within approx. 5 %
#set N=400
runner = SimulationRunner(number_of_simulations=400, strategies=["Random", "Greedy", "SafeChoice", "MCTS", "Minimax"], board_dims=None)
    
runner.run_iteration()
runner.save_results()