def is_float(num: str) -> bool:
    if num is None:
        return False
    try:
        return float(num) >= 0
    except ValueError:
        return False