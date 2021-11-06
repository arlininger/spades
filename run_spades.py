from mpi4py import MPI
from math   import pi as PI
from numpy  import array

import copy
import json

from spades import run_game

comm = MPI.COMM_WORLD
nprocs = comm.Get_size()
myrank = comm.Get_rank()

def main():
    # print(myrank)
    n    = array(0, dtype=int)
    pi   = array(0, dtype=float)
    mypi = array(0, dtype=float)

    past_data = dict()
    if myrank == 0:
        try:
            with open('/clusterfs/spades/data.txt','r') as json_file:
                past_data = json.load(json_file)
        except Exception as e:
            print(e)
            print("Failed to open data.txt on node %d" % ( myrank))
            past_data = dict()
            past_data['count'] = 0
            past_data['card_win_count'] = [0 for card_id in range(52)]
    past_data = comm.bcast(past_data, root=0)
    past_data_original = copy.deepcopy(past_data)
    winner_stats = {"A": 0, "B": 0}

    for i in range(5000000):
    # for i in range(1000):
        # print ("Rank %d running %d" % (myrank, i))
        gamestats = run_game(past_data)
        winner_stats[gamestats['winner']] = winner_stats[gamestats['winner']] + 1
        card_win_count = gamestats['card_win_count']
        past_data['count'] = past_data['count'] + card_win_count[51] # Ace of Spades always wins
        for card_id in range(52):
            past_data['card_win_count'][card_id] = past_data['card_win_count'][card_id] + card_win_count[card_id]

    winner_stats = comm.gather(winner_stats, root=0)
    past_data_array = comm.gather(past_data, root=0)

    if myrank == 0:
        stats = dict()
        for node_stats in winner_stats:
            for key, value in node_stats.items():
                if key in stats.keys():
                    stats[key] = stats[key] + value
                else:
                    stats[key] = value

        print(stats)
        past_data_final = dict()
        past_data_final['count'] = past_data_original['count'] + sum([x['count'] for x in past_data_array])
        #print(past_data_array)
        # for x in past_data_array:
        #     print(x)
        past_data_final['card_win_count'] = [past_data_original['card_win_count'][card_id] + sum([x['card_win_count'][card_id] for x in past_data_array])
            for card_id in range(52)]
        # print("Past data final")
        # print(past_data_final)
        with open('data2.txt', 'w') as outfile:
            json.dump(past_data, outfile)

if __name__ == '__main__':
    main()