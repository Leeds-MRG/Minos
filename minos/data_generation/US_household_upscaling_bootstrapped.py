from US_household_upscaling import main

if __name__ == '__main__':
    do_bootstrapping = False
    bootstrap_sample_size = 1_000_000
    main(do_bootstrapping, bootstrap_sample_size)
