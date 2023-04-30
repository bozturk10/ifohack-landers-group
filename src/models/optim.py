import logging, os, datetime
import pandas as pd
import numpy as np
import copy 
from sklearn.model_selection import train_test_split,TimeSeriesSplit,KFold

from src.hyperparams.utils import select_features
from src.data.data_import import read_feature_data, ROOT_PATH,read_main_data
from src.models.boosting import fit_boosting_model
ROOT_PATH =  os.path.abspath(os.path.join(__file__ ,"../../.."))
def evaluate_for_one_fold(fold_number, X_train, X_val, y_train, y_val, conf, logger,save):

    config = {
    'device_type' : 'cpu',
    'num_threads': 8,
    'verbose': 0,
    'seed': 42,
    'metric': ['l2'],
    'early_stopping_round': 50,
    }

    rmse, smape, mae, me, pred_val, imp = fit_boosting_model(X_train, y_train, X_val, y_val, config, log = False)


    logger.info(str([rmse, smape, mae, me]))

    if save:
        predictions.to_csv(os.path.join(ROOT_PATH, "models/predictions/latest_predictions.csv"))
        importances.to_csv(os.path.join(ROOT_PATH, "models/importances/latest_importance_"+dataset_name+ 'fold_{}'.format(fold_number)+".csv"))
        create_importance_plot(importances)

    return rmse, smape, mae, me