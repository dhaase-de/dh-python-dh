def unique(x):
    y = []
    for item in x:
        if item not in y:
            yield item
            y.append(item)


def which(x):
    index = 0
    for item in x:
        if item:
            yield index
        index += 1
