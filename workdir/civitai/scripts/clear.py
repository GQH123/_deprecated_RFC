import os
import shutil
from tqdm import tqdm


with open('clear.txt', 'r') as f:
    clear_path = f.read().split('\n')

clear_path = list(set([os.path.split(path)[0] for path in clear_path if path]))
# print(clear_path)

for path in tqdm(clear_path):
    if os.path.exists(os.path.join('../saves/models/', path)):
        shutil.rmtree(os.path.join('../saves/models/', path))