# HR 05/06/23 Added to Minos for fertility/parity testing
from minos.utils import search, generate_series, series_ok


# For testing; test cases confirmed by hand
# DEFAULTS = [1000, 5, 1937.5] # Test case 1, r = 0.5
DEFAULTS = [10, 10, 4450.584] # Test case 2, r = 1.8
# DEFAULTS = [10, 99, 200] # Test case 3, r = 0.9503
# DEFAULTS = [100, 100, 110] # Test case 4, r = 0.0909...
# TOL_DEFAULT = 1e-6
# MAX_ITER_DEFAULT = 50
# FACTOR_DEFAULT = 0.2 # Very important! Test case 1 blows up if this is close to unity
# ROUND_DEFAULT = "up"

N_DEFAULT = 15 # Max. number of children per mother


if __name__ == "__main__":
    a,n,s = DEFAULTS
    print("\n## Test run of 'solve'... ##\n")
    r = search(a,n,s)
    print("\n## Checking solution for (a,n,s,r) = ", a,n,s,r, "... ##\n")
    series = generate_series(a, r, n)
    _ok = series_ok(a, r, n, series)
    if _ok:
        print("\n## Series okay! ##\n")
    else:
        print("\n## Series NOT okay! ##\n")
