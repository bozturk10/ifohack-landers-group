import lightgbm as lgb
import time, logging
import numpy as np
from src.models.metrics import calculate_model_metrics
evals_result = {}  # to record eval results for plotting


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


def fit_boosting_model(X_train,y_train,X_val,y_val, params):
    lgb_train, lgb_val = get_lgb_datasets(X_train,y_train,X_val,y_val)
    gbm, evals_result, runtime = run_lgb_model(params,lgb_train,lgb_val,callbacks=callbacks)
    rmse, mape, mae, me, smape, pred_val = calculate_model_metrics(X_val,y_val,model=gbm)
    logging.info("Fitting model took " + str(runtime) + " seconds")


    feature_importances = gbm.feature_importance()

    return rmse, smape, mae, me, pred_val, feature_importances
