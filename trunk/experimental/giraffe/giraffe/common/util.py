def flatten( i ):
    if hasattr(i, "__iter__"):
        for j in i:
            for k in flatten(j):
                yield k
    else:
        yield i


