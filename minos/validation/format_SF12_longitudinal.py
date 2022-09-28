import pandas as pd
import glob as glob
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt



def main(sources, years, labels):
    df = pd.DataFrame(columns=['SF_12', 'label', 'year'])
    for year in years:
        for i, source in enumerate(sources):
            file = glob.glob(f'{source}means*{year}.csv')[0]
            new = pd.DataFrame(pd.read_csv(file)["SF_12"])
            if labels[i] == 'Baseline': # for normalising for relative difference against baseline
                baseline_mean = np.nanmean(new)
            new /= baseline_mean
            new['label'] = labels[i]
            new['year'] = year
            df = pd.concat([df, new])
    df.reset_index(inplace=True, drop=True)
    baseline_mean = np.nanmean(df.loc[df['label']=="Baseline"]["SF_12"])
    df["SF_12"] /= baseline_mean
    #df = df.groupby(['label', 'year'])["SF_12"].mean()
    f = plt.figure()
    sns.lineplot(data=df, x='year', y="SF_12", hue = 'label', style='label', markers=True, palette='Set2')
    plt.savefig("plots/test_means.pdf")

if __name__ == '__main__':
    years = np.arange(2010, 2019)
    sources = ['output/baseline/', 'output/povertyUplift/', 'output/childUplift/']
    labels = ['Baseline', '£20 Poverty Line', '£20 All']
    main(sources, years, labels)