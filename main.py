with open("ddd.txt", encoding='utf-8') as f:
    path_str = ''
    for line in f:
        if 'Index' in line:
            path_str += line.replace('Index: ', '')
    print(path_str)