import copy

GLD = 'gld'
CLT = 'clt'
SCN = 'scn'
PPR = 'ppr'
RLG = 'rlg'


def purse(*coins):
    return {cn['currency']: cn for cn in coins}


def coin(amount, currency=GLD):
    return {
        'currency': currency,
        'amount': amount,
    }


def has_enough(purse, price):
    return compare_purses(purse, price) >= 0


def compare_purses(p1, p2):
    """ -1 if p1 < p2 - all coins of p1 less then corresponding coin from p2
         0 if eq
         1 if p1 > p2 - all coins of p1 greater then corresponding coin from p2
    """
    diff = 0
    for curr in p2:
        if curr not in p1:
            return -1

        coin_diff = p1[curr]['amount'] - p2[curr]['amount']
        if coin_diff < 0:
            return -1

        diff += coin_diff

    if diff == 0:
        return 0

    return 1


def sum_purses(p1, p2):
    ttl = copy.deepcopy(p1)
    for curr in p2:
        if curr not in ttl:
            ttl[curr] = coin(0, curr)

        ttl[curr]['amount'] = ttl[curr]['amount'] + p2[curr]['amount']

    return ttl


def sub_purses(p1, p2):
    for curr in p2:
        p1[curr]['amount'] = p1[curr]['amount'] - p2[curr]['amount']

    return p1
