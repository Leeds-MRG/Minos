
import pandas as pd






def main():

    baseDir = '/home/luke/Documents/MINOS/ARC_Out/output/baseline/'
    intDir = '/home/luke/Documents/MINOS/ARC_Out/output/livingWageIntervention/'

    df = pd.DataFrame()
    for id in range(50, 100):

        if id == 10:
            continue
        elif id == 53:
            continue
        elif id == 76:
            continue
        elif id == 80:
            continue

        print(f'Extracting information for run {id}')
        # read in both datafiles
        base = pd.read_csv(baseDir + f'run_id_' + str(id) + '_2019.csv')
        lwage = pd.read_csv(intDir + f'id_' + str(id) + '_2019.csv')

        base = base[['pidp', 'SF_12']]
        lwage = lwage[['pidp', 'SF_12']]

        if id == 50:
            df['pidp'] = base['pidp']

        df[f'baseline_{str(id)}'] = base['SF_12']
        df[f'lwage_{str(id)}'] = lwage['SF_12']

        print(f'Run {id} complete')

    df.reset_index(inplace=True, drop=True)
    df.to_csv('/home/luke/Documents/MINOS/test2.csv')
    print('Data saved successfully')


if __name__ == '__main__':
    main()
