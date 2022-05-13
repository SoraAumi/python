import tqdm
import time

for i in tqdm.tqdm(range(100)):
    # i = 0, 1, 2, ..., 99
    time.sleep(0.01)

lt = ["a", "b", "c", "d"]
for i in tqdm.tqdm(lt):
    # i = "a", "b", "c", "d"
    time.sleep(1)
