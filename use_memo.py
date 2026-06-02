from play import import_memo
from play import write_to_file

memo = import_memo("memo.json")

data = dict()
i = 0
for key,value in memo.items():
    if i % 10000 == 0:
        print(i)
    board = key[0]
    num_plys = key[1]
    best_moves = value[1]
    if num_plys == 4:
        data[board] = best_moves

    i += 1

write_to_file("use_memo_test.json",data)
