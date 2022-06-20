import uuid

import tqdm
import time
from file.file_util import FileUtil

# with open('./ddd.txt', encoding='utf-8') as f:
#     for line in f.readlines():
#         if 'Index' in line:
#             print(line.replace('Index: ', ''), end='')

str = ''' decode(sai.document_number, '') '''

if __name__ == '__main__':
    fp = FileUtil('./ddd.txt')
    context = ''
    count = 0
    for line in fp.read_file(return_type="list"):
        context += f"'{line}',{count},"
        count += 1
    print(context[:-1])
