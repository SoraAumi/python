from tabulate import tabulate


def pretty_print(res_data):
    if len(res_data) > 0:
        grid_head = res_data[0].keys()
        grid_data = []
        for data in res_data:
            gd = []
            for column in grid_head:
                gd.append(data[column])
            grid_data.append(gd)
        print(tabulate(grid_data, headers=grid_head, tablefmt='grid'))


if __name__ == '__main__':
    pretty_print([{"a": 1, "b": 2, "c": "3"}, {"a": 4, "b": 5, "c": 6}])
