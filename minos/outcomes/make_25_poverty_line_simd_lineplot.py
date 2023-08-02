from minos.outcomes.make_lineplots import main as lineplot_main

if __name__ == '__main__':
    directories = "baseline," + ("hhIncomePovertyLineChildUplift," * 10)[:-1] # repeat 11 times and cut off last comma.
    tags = "National Average,First,Second,Third,Fourth,Fifth,Sixth,Seventh,Eighth,Ninth,Tenth"
    subset_function_strings = """who_kids,who_kids_first_simd_decile,who_kids_second_simd_decile,who_kids_third_simd_decile,who_kids_fourth_simd_decile,who_kids_fifth_simd_decile,who_kids_sixth_simd_decile,who_kids_seventh_simd_decile,who_kids_eighth_simd_decile,who_kids_ninth_simd_decile,who_kids_tenth_simd_decile"""
    prefix="25_poverty_simd_deciles"
    config_mode = "glasgow_scaled"
    ref = "National Average"
    v = "SF_12"
    method='nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)

    directories = "baseline,hhIncomePovertyLineChildUplift"
    tags = "National Average,Tenth"
    subset_function_strings = """who_kids_tenth_simd_decile,who_boosted_tenth_simd_decile"""
    prefix="25_poverty_tenth_simd_decile"
    config_mode = "glasgow_scaled"
    ref = "National Average"
    v = "SF_12"
    method='nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)

    directories = "baseline,hhIncomePovertyLineChildUplift"
    tags = "National Average,Fifth"
    subset_function_strings = """who_kids_fifth_simd_decile,who_boosted_fifth_simd_decile"""
    prefix="25_poverty_fifth_simd_decile"
    config_mode = "glasgow_scaled"
    ref = "National Average"
    v = "SF_12"
    method='nanmean'
    lineplot_main(directories, tags, subset_function_strings, prefix, mode=config_mode, ref=ref, v=v, method=method)
