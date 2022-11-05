def max_int(a: int, b: int) -> int:
    if a > b:
        return a
    return b

def min_int(a: int, b: int) -> int:
    if a < b:
        return a
    return b

def between_int(x: int, minimum: int, maximum: int) -> int:
    x = max_int(x, minimum)
    return min_int(x, maximum)
