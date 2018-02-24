"""Main script for generating output.csv."""
from __future__ import division
import pandas as pd

results = pd.DataFrame(columns=['SubjectId', 'Stat',
                                'Split', 'Subject', 'Value'])
hands = {'LHH': ('HitterSide', 'L'),
         'LHP': ('PitcherSide', 'L'),
         'RHH': ('HitterSide', 'R'),
         'RHP': ('PitcherSide', 'R')
         }


def truncate(f, n):
    """
    Truncates/pads a float f to n
    decimal places without rounding.
    """
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d + '0' * n)[:n]])


def my_round(r):
    """
    Check decimal places and 
    round/truncate accordingly.
    """
    r_dec = str(r - int(r))[1:]
    if len(r_dec) == 5:
        if int(r_dec[3]) < int(r_dec[4]):
            value = truncate(r, 3)
        else:
            value = round(r, 3)
    else:
        value = round(r, 3)
    return value


def calculate(row, comb):
    """
    Find the Baseball stats
    and append to a dataframe.
    """
    if row.PA >= 25:
        try:
            if comb.Stat == 'AVG':
                r = row.H / row.AB
                value = my_round(r)
            if comb.Stat == 'OBP':
                num = row.H + row.BB + row.HBP
                denom = row.AB + row.BB + \
                    row.SF + row.HBP
                r = num / denom
                value = my_round(r)
            if comb.Stat == 'SLG':
                r = row.TB / row.AB
                value = my_round(r)
            if comb.Stat == 'OPS':
                num = row.H + row.BB + row.HBP
                denom = row.AB + row.BB + \
                    row.SF + row.HBP
                obp = num / denom
                slg = row.TB / row.AB
                r = obp + slg
                value = my_round(r)
        except ZeroDivisionError:
            value = 0
        newrow = [row.name, comb.Stat, comb.Split, comb.Subject, value]
        results.loc[len(results)] = newrow


def combine(row, data):
    """
    Apply each combination to the
    dataframe.
    """
    hand = hands[row.Split.split(" ")[1]]
    temp = data.loc[data[hand[0]] == hand[1]]
    values = temp.groupby(
        row.Subject)[['PA', 'H', 'BB', 'HBP', 'SF', 'TB', 'AB']].sum()
    values.apply(
        lambda x: calculate(x, row), axis=1)


def main():
    # add basic program logic here
    global results
    data = pd.read_csv('data/raw/pitchdata.csv')
    data
    comb = pd.read_csv('data/reference/combinations.txt')

    comb.apply(lambda x: combine(x, data), axis=1)

    results = results.sort_values(['SubjectId', 'Stat',
                                   'Split', 'Subject'], ascending=True)
    results.to_csv('data/processed/output.csv', index=False)


if __name__ == '__main__':
    main()
