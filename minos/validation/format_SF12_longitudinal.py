import pandas as pd
import glob as glob
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def main():
    uplift = [0.0, 1000.0, 10000.0]
    percent= [25.0, 50.0, 75.0]
    df = pd.DataFrame(columns=['SF_12', 'uplift', 'percent', 'year'])
    years = np.arange(2012, 2017)
    for x in uplift:
        for y in percent:
            for year in years:
                file = glob.glob(f'output/ex1/means_{x}_{y}_{year}*.csv')
                new = pd.DataFrame(pd.read_csv(file[0])["SF_12"])
                new['year'] = year
                new['uplift'] = x
                new['percent'] = y
                df = pd.concat([df, new])
    df = df.loc[df['percent']==25.0,]
    df.reset_index(inplace=True, drop=True)

    f = plt.figure()
    sns.lineplot(data=df, x='year', y="SF_12", hue = 'uplift', style='uplift', markers=True, palette='Set2')
    plt.savefig("plots/test_means.pdf")

if __name__ == '__main__':
    main()