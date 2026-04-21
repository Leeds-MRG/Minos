
import os
import pandas as pd
import numpy as np
from statsmodels.miscmodels.ordinal_model import OrderedModel
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

from sipherdb.sipher_database import SipherDatabase
from sipherdb.sipher_database import SqlDB
from sipherdb.query.queries import Queries

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '../..'))
os.chdir(ROOT_DIR)

max_number_of_rooms = 8


def db_init(sql_db=SqlDB.POSTGRESQL):
    db_obj = SipherDatabase()
    db_obj.init_class(sql_db=sql_db, db_config_file=os.path.join(ROOT_DIR, 'database.ini'))
    return Queries()


def compute_clogit(data_latest_df, epc_retrofit_df):

    df = epc_retrofit_df[['imd_decile', 'housing_tenure', 'number_of_habitable_rooms',
                          'rating_previous', 'rating_latest']].copy()

    # Map EPC ratings (worst->best) G..A to integers 0..6
    rating_map = {'G': 0, 'F': 1, 'E': 2, 'D': 3, 'C': 4, 'B': 5, 'A': 6}
    df['y'] = df['rating_latest'].map(rating_map)
    df['rating_previous_num'] = df['rating_previous'].map(rating_map)

    # Encode features
    X = pd.get_dummies(
        df[['imd_decile', 'number_of_habitable_rooms', 'housing_tenure', 'rating_previous_num']],
        columns=['housing_tenure'],
        drop_first=True,  # avoid dummy trap
        dtype=float
    )

    # Optional: scale continuous predictors to aid optimization
    scaler = StandardScaler()
    X[['imd_decile', 'number_of_habitable_rooms', 'rating_previous_num']] = scaler.fit_transform(
        X[['imd_decile', 'number_of_habitable_rooms', 'rating_previous_num']]
    )

    # Fit proportional-odds (logit link)
    model = OrderedModel(
        endog=df['y'].astype(int),
        exog=X.astype(float),
        distr='logit',  # cumulative logit
    )

    # Use a robust optimizer; increase maxiter if needed
    res = model.fit(method='bfgs', maxiter=100000, disp=False)

    # res.params contains both betas and threshold cutpoints (a_k)
    # print(res.summary()) provides a readable table

    # Convert current EPC rating to numerals
    data_latest_df['rating_previous_num'] = data_latest_df['energy_rating'].map(rating_map)

    X_latest = pd.get_dummies(
        data_latest_df[['imd_decile', 'number_of_habitable_rooms', 'housing_tenure', 'rating_previous_num']],
        columns=['housing_tenure'],
        drop_first=True,  # avoid dummy trap
        dtype=float
    )

    cont_cols = ['imd_decile', 'number_of_habitable_rooms', 'rating_previous_num']
    X_latest[cont_cols] = scaler.transform(X_latest[cont_cols])

    # Align columns with the training matrix X
    X_latest = X_latest.reindex(columns=X.columns, fill_value=0.0)

    # Example: compute cumulative probabilities P(y <= k) for each observation
    # cumprob = res.model.predict(res.params, exog=X, which='cumprob')
    cumprob = res.model.predict(res.params, exog=X_latest, which='cumprob')
    cumprob = pd.DataFrame(cumprob, index=data_latest_df.index)
    cumprob.columns = ['F', 'E', 'D', 'C', 'B', 'A']

    thresholds = cumprob[['F', 'E', 'D', 'C', 'B']].to_numpy()  # shape (n, 5)
    cumprob['random'] = np.random.rand(len(cumprob), 1)
    r = cumprob['random'].to_numpy().reshape(-1, 1)  # shape (n, 1)
    mask = (r < thresholds)  # True where random is below the threshold

    # First True along the row gives the chosen band among F..B; if none, choose A
    first_true_idx = mask.argmax(axis=1)  # index 0..4; 0 if none True as well
    has_true = mask.any(axis=1)
    labels = np.array(['F', 'E', 'D', 'C', 'B'])
    chosen = np.where(has_true, labels[first_true_idx], 'A')

    # Assign as ordered categorical
    categories = ['F', 'E', 'D', 'C', 'B', 'A']
    data_latest_df['energy_rating_new'] = pd.Categorical(chosen, categories=categories, ordered=True)

    return


def rforest(X, y, filename):

    regr = RandomForestRegressor(n_estimators=100, oob_score=True)
    regr.fit(X, y)

    oob_score = regr.oob_score_
    print(f'Out-of-Bag Score: {oob_score}')

    # Retrieve OOB predictions
    oob_predictions = regr.oob_prediction_

    # Plotting True values vs OOB Predicted values
    import matplotlib.pyplot as plt
    import seaborn as sns

    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=y, y=oob_predictions, alpha=0.5)

    # Add a diagonal line for reference (perfect prediction)
    line_coords = [min(y.min(), oob_predictions.min()), max(y.max(), oob_predictions.max())]
    plt.plot(line_coords, line_coords, color='red', linestyle='--')

    plt.xlabel('True Values')
    plt.ylabel('OOB Predicted Values')
    # plt.title(f'OOB Predictions vs True Values (R²: {oob_score:.4f})')
    plt.tight_layout()
    # plt.show()  # or plt.savefig('oob_plot.png')
    plt.savefig(filename)

    predictions = regr.predict(X)

    from sklearn.metrics import mean_squared_error, r2_score
    mse = mean_squared_error(y, predictions)
    print(f'Mean Squared Error: {mse}')

    r2 = r2_score(y, predictions)
    print(f'R-squared: {r2}')

    return regr


def main():

    np.random.rand(4)

    dbquery = db_init()  # initialise connection to the database

    # Get EPC latest data and merge with IMD
    epc_latest = dbquery.ca_epc_latest_at_lsoa_level(ca_name='Greater Manchester')
    lvars = ['lsoa_code', 'housing_tenure', 'number_of_habitable_rooms', 'energy_rating',
             'environment_impact', 'co2_emissions', 'co2_emissions_per_floor']
    epc_latest_df = pd.DataFrame(epc_latest, columns=lvars)
    epc_latest_df['number_of_habitable_rooms'] = np.where(
        epc_latest_df['number_of_habitable_rooms'] > max_number_of_rooms,
        max_number_of_rooms, epc_latest_df['number_of_habitable_rooms'])

    imd_data = dbquery.imd_rank_in_ca(ca_name='Greater Manchester')
    imd_data_df = pd.DataFrame(imd_data, columns=['lsoa_code', 'imd_rank', 'imd_decile'])
    imd_data_df = imd_data_df[['lsoa_code', 'imd_decile']]
    epc_latest_df = pd.merge(epc_latest_df, imd_data_df, on='lsoa_code', how='left')

    # Get the EPC retrofit data and merge with IMD
    db_vars = ['housing_tenure', 'number_of_habitable_rooms',
               'rating_previous', 'rating_latest',
               'environment_impact_prev', 'co2_emissions_prev', 'co2_emissions_per_floor_prev',
               'environment_impact_diff', 'co2_emissions_diff', 'co2_emissions_per_floor_diff']
    epc_retrofit = dbquery.ca_epc_retrofit_at_lsoa_level(db_vars=db_vars, ca_name='Greater Manchester')
    cols = ['lsoa_code'] + db_vars
    epc_retrofit_df = pd.DataFrame(epc_retrofit, columns=cols)
    # All number of habitable rooms higher than max_number_of_rooms, make them max_number_of_rooms
    epc_retrofit_df['number_of_habitable_rooms'] = np.where(epc_retrofit_df['number_of_habitable_rooms'] > max_number_of_rooms,
                                                            max_number_of_rooms, epc_retrofit_df['number_of_habitable_rooms'])
    epc_retrofit_df = pd.merge(epc_retrofit_df, imd_data_df, how='left', on='lsoa_code')

    # Predict new EPC by using a cumulative logit
    compute_clogit(epc_latest_df, epc_retrofit_df)

    rating_map = {'G': 0, 'F': 1, 'E': 2, 'D': 3, 'C': 4, 'B': 5, 'A': 6}
    epc_latest_df['rating_latest_num'] = epc_latest_df['energy_rating_new'].map(rating_map)
    epc_latest_df['rating_latest_num'] = epc_latest_df['rating_latest_num'].astype(int)

    # Predict the environmental impact improvement based on the
    # number of habitable rooms, IMD and energy rating improvement
    # Use a Random Forest Regressor model

    df_model = epc_retrofit_df.copy()
    df_model['rating_previous_num'] = df_model['rating_previous'].map(rating_map)
    df_model['rating_latest_num'] = df_model['rating_latest'].map(rating_map)
    df_model['rating_previous_num'] = df_model['rating_previous_num'].astype(int)
    df_model['rating_latest_num'] = df_model['rating_latest_num'].astype(int)


    df_model.rename(columns={'environment_impact_prev': 'environment_impact_var',
                             'co2_emissions_prev': 'co2_emissions_var',
                             'co2_emissions_per_floor_prev': 'co2_emissions_per_floor_var'},
                    inplace=True)

    x_vars = ['number_of_habitable_rooms', 'rating_previous_num', 'rating_latest_num', 'imd_decile',
              'environment_impact_var', 'co2_emissions_var', 'co2_emissions_per_floor_var']
    X = df_model[x_vars]

    y1 = df_model['environment_impact_diff']
    y2 = df_model['co2_emissions_diff']
    y3 = df_model['co2_emissions_per_floor_diff']

    regr1 = rforest(X, y1, 'data/environment_impact_diff_validation.png')
    regr2 = rforest(X, y2, 'data/co2_emissions_diff_validation.png')
    regr3 = rforest(X, y3, 'data/co2_emissions_per_floor_diff_validation.png')

    epc_latest_vars = ['number_of_habitable_rooms', 'rating_previous_num', 'rating_latest_num', 'imd_decile',
                       'environment_impact', 'co2_emissions', 'co2_emissions_per_floor']
    epc_latest_x = epc_latest_df[epc_latest_vars].copy()
    epc_latest_x.rename(columns={'environment_impact': 'environment_impact_var',
                                 'co2_emissions': 'co2_emissions_var',
                                 'co2_emissions_per_floor': 'co2_emissions_per_floor_var'},
                        inplace=True)

    epc_latest_df['environment_impact_diff'] = regr1.predict(epc_latest_x)
    epc_latest_df['co2_emissions_diff'] = regr2.predict(epc_latest_x)
    epc_latest_df['co2_emissions_per_floor_diff'] = regr3.predict(epc_latest_x)

    # For those households with a predicted energy rating without improvement (or it got worse)
    # set the above predicted diff to zero (this is model extrapolation)
    epc_latest_df['environment_impact_diff'] = (
        np.where(epc_latest_df['rating_latest_num'] <= epc_latest_df['rating_previous_num'], 0.0,
                 epc_latest_df['environment_impact_diff'])
    )
    epc_latest_df['co2_emissions_diff'] = (
        np.where(epc_latest_df['rating_latest_num'] <= epc_latest_df['rating_previous_num'], 0.0,
                 epc_latest_df['co2_emissions_diff'])
    )
    epc_latest_df['co2_emissions_per_floor_diff'] = (
        np.where(epc_latest_df['rating_latest_num'] <= epc_latest_df['rating_previous_num'], 0.0,
                 epc_latest_df['co2_emissions_per_floor_diff'])
    )

    # format variables in epc_latest_df
    housing_tenure_reduced_dic = {
        'owned': 1,
        'private rented': 2,
        'social rented': 3
    }
    epc_latest_df['housing_tenure_num'] = epc_latest_df['housing_tenure'].map(housing_tenure_reduced_dic)
    epc_latest_df.rename(columns={'lsoa_code': 'ZoneID'}, inplace=True)
    epc_latest_df = epc_latest_df.astype({'housing_tenure_num': int, 'number_of_habitable_rooms': int})

    epc_latest_df.to_csv('data/epc_latest_gmca.csv', index=False)

    return epc_latest_df


if __name__ == "__main__":
    main()
