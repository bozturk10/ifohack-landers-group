import sys
sys.path.append("../..") # Adds higher directory to python modules path.
print(sys.path)
import pandas as pd
import lightgbm as lgb
import time, logging
import numpy as np
from sklearn.model_selection import train_test_split

evals_result = {}  # to record eval results for plotting

df= pd.read_csv('../data/interim/nb_level_merged_all_cities_with_amenties.csv')
df = df.fillna(0)
# Prepare data for regression
X = df.drop(columns=["Neighborhood_Name","City_Name","Land_Value"])
y = df.Land_Value
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

callbacks=[lgb.log_evaluation(10),
           lgb.record_evaluation(evals_result),
           lgb.early_stopping(stopping_rounds=25),
        ]

def get_lgb_datasets(X_train,y_train,X_val,y_val):
    lgb_train = lgb.Dataset(X_train, y_train)
    lgb_val = lgb.Dataset(X_val, y_val, reference=lgb_train)
    return lgb_train,lgb_val


def run_lgb_model(params,lgb_train,lgb_val,callbacks=[]):
    start = time.time()
    gbm = lgb.train(params,
                    lgb_train,
                    valid_sets=[lgb_train, lgb_val],
                    callbacks=callbacks)
    end = time.time()
    runtime= end-start 
    
    return gbm, evals_result, runtime




def model_fit(X_train, y_train):
    callbacks=[lgb.log_evaluation(10)]
    params= {
        'num_boost_round':200,
        'device_type' : 'cpu',
        'num_threads': 8,
        'verbose': 0,
        'seed': 42,
        'metric': ['l2'],
        'early_stopping_round': 250,
        'force_col_wise': 'true',
        'min_data_in_leaf':10
        }
    X_train_1, X_val, y_train_1, y_val = train_test_split(X_train,y_train, test_size=0.2, random_state=42)

    lgb_train, lgb_val = get_lgb_datasets(X_train_1,y_train_1,X_val,y_val)
    regr, _, _ = run_lgb_model(params,lgb_train,lgb_val,callbacks=callbacks)

    return regr


def model_predict(regr, X_test):
	y_pred = regr.predict(X_test)
	return y_pred
