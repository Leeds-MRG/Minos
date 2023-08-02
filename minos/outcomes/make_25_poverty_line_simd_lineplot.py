from minos.outcomes.make_lineplots import main as lineplot_main

if __name__ == '__main__':
    directories = ("povertyLineChildUplift," * 11)[:-1] # repeat 11 times and cut off last comma.
    tags = "National Average,First,Second,Third,Fourth,Fifth,Sixth,Seventh,Eighth,Ninth,Tenth"
    subset_function_strings = "who_alive,who_first_simd_decile,who_second_simd_decile,who_third_simd_decile,who_fourth_simd_decile,who_fifth_simd_decile,who_sixth_simd_decile,who_seventh_simd_decile,who_eighth_simd_decile,who_ninth_simd_decile,who_tenth_simd_decile"
    prefix="25_poverty_simd_deciles"
    config_mode = "glasgow_scaled"
    ref = "National Average"
    v = "SF_12"
    method='nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)
