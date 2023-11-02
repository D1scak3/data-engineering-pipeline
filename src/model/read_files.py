import numpy as np
import pandas as pd
from datetime import datetime

def read_files(path="C:/Users/Vasco/OneDrive - Universidade de Aveiro/Grupo/AIA/", product_group_id=27,time_series_folder = 1):
    df_long = pd.read_pickle(path+"Data/time_series_"+str(time_series_folder)+"/long_product_group_id_" + str(product_group_id))
    df_wide = df_long.reset_index().groupby(['timestamp', "company"])["price"].first().unstack().reset_index().set_index("timestamp")

    # Fill missing timestamps
    timestamps  = pd.DataFrame(index = pd.date_range(df_wide.index[0],df_wide.index[-1], freq='D'))
    df_wide = pd.merge(timestamps, df_wide, left_index = True, right_index = True, how = 'left')
    df_wide.columns.name = None

    return df_long, df_wide


def read_files2(path):
    df_long = pd.read_pickle(path)
    df_wide = df_long.reset_index().groupby(['timestamp', "company"])["price"].first().unstack().reset_index().set_index("timestamp")

    # Fill missing timestamps
    timestamps  = pd.DataFrame(index = pd.date_range(df_wide.index[0],df_wide.index[-1], freq='D'))
    print(df_wide)
    input(...)
    df_wide = pd.merge(timestamps, df_wide, left_index = True, right_index = True, how = 'left')
    df_wide.columns.name = None

    print(df_wide)
    input(...)

    return df_long, df_wide