with open("ddd.txt", encoding='utf-8') as f:
    stsr = ''
    for line in f:
        if 'Index' in line:
            stsr += line.replace('Index: ', '')
    print(stsr)