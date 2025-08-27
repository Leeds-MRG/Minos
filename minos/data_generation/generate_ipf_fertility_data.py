# HR 15/08/25 Produce births and population tables via IPF for use with fertility modules
from minos.fertility_ipf import *

year_start, year_end = 2010, 2045


def main():
    print("Generating births and population data from {} to {}".format(year_start, year_end))
    year_range = range(year_start, year_end + 1)

    for year in year_range:
        print('\nGetting IPF solutions for {}'.format(year))
        get_ipf_solutions(year=year, recalculate=True, _save=True)


if __name__ == "__main__":
    main()
