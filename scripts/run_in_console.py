from scripts.run import run_pipeline

if __name__ == "__main__":

    configuration_file = "config/testConfig.yaml"
    input_data_dir = "data"
    persistent_data_dir = "persistent_data"
    output_dir = "output"

    simulation = run_pipeline(configuration_file, input_data_dir, persistent_data_dir, output_dir)
