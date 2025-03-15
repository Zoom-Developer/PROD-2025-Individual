def merge_stat_res(
        view: list[tuple[int, int, int]],
        click: list[tuple[int, int, int]]
) -> list[tuple[int, int, int, int, int]]:
    res = {}
    for i in view:
        res[i[2]] = [i[0], i[1], 0, 0, i[2]]
    for i in click:
        res.setdefault(i[2], [0, 0, 0, 0, i[2]])
        res[i[2]][2] = i[0]
        res[i[2]][3] = i[1]
    return sorted(res.values(), key=lambda x: x[4])