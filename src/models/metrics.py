import numpy as np
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error, mean_absolute_error


def calculate_smape(A, F):
    '''
    symmetric mean abs perc error 
    '''
    with np.errstate(divide='ignore', invalid='ignore'):
        tmp = 2 * np.abs(F-A) / (np.abs(A) + np.abs(F))
    tmp[np.isnan(tmp)] = 0 # if Actual and Prediction are 0, take sMAPE as 0 
    return np.sum(tmp) / len(tmp) * 100


def calculate_model_metrics(X_val, y_val, model):
    pred_val= model.predict(X_val)
    rmse = np.sqrt(mean_squared_error(y_val, pred_val))
    mape = mean_absolute_percentage_error(y_val, pred_val)
    mae = mean_absolute_error(y_val, pred_val)
    me = np.mean(y_val - pred_val)
    try:
        smape = calculate_smape(y_val, pred_val)
    except:
        smape = -1
    return rmse, mape, mae, me, smape, pred_val

def calculate_metrics(pred_val, y_val):
    rmse = np.sqrt(mean_squared_error(y_val, pred_val))
    mape = mean_absolute_percentage_error(y_val, pred_val)
    mae = mean_absolute_error(y_val, pred_val)
    me = np.mean(y_val - pred_val)
    try:
        smape = calculate_smape(y_val, pred_val)
    except:
        smape = -1
    return rmse, mape, mae, smape, me