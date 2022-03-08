with open("ddd.txt", encoding='utf-8') as f:
    stsr = '('
    for line in f:
        stsr += "'" + line.strip() + "',"
    stsr += ')'
    print(stsr)