from minos.outcomes.make_lineplots import main as lineplot_main

if __name__ == '__main__':
    directories = ("povertyLineChildUplift," * 11)[:-1] # repeat 11 times and cut off last comma.
    tags = "National Average,First,Second,Third,Fourth,Fifth,Sixth,Seventh,Eighth,Ninth,Tenth"
    subset_function_strings = """who_below_poverty_line_and_kids,who_poverty_kids_first_simd_decile,who_poverty_kids_second_simd_decile,who_poverty_kids_third_simd_decile,who_poverty_kids_fourth_simd_decile,who_poverty_kids_fifth_simd_decile,who_poverty_kids_sixth_simd_decile,who_poverty_kids_seventh_simd_decile,who_poverty_kids_eighth_simd_decile,who_poverty_kids_ninth_simd_decile,who_poverty_kids_tenth_simd_decile"""
    prefix="25_poverty_simd_deciles"
    config_mode = "glasgow_scaled"
    ref = "National Average"
    v = "SF_12"
    method='nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)
