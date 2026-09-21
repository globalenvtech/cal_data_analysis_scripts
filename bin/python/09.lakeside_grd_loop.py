from pathlib import Path

import pytz
import numpy as np
import pandas as pd
import lewisctr_utils
#==========================================================================================================================================================
# region: Parameters
#==========================================================================================================================================================
base_path = Path(__file__).parent.parent.parent
data_path = Path.joinpath(base_path, 'data')
folder_name1 = 'lakeside_grd_loop'
folder_name2 = '2025_2026_may'
grd_loop_path = Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/grd_loop_overall.csv')
res_folderpath = Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/res_img')

cols2viz = ['Tsup(degC)', 'Tret(degC)']
color_ls = ['c', 'm']
linestyle_ls = ['solid', 'solid']

start_yr = 2025
start_mth = 5
start_day = 3
end_yr = 2026
end_mth = 5
end_day = 4
tneu = 10 #degC neutral temperature of the borehole

clg_season = ['2025-05-01', '2025-11-01']
htg_season = ['2025-11-01', '2026-05-01']
date_format = '%Y-%m-%d'
timezone = 'America/New_York'
#==========================================================================================================================================================
# endregion: Parameters
#==========================================================================================================================================================
#==========================================================================================================================================================
# region: Functions
#==========================================================================================================================================================
def replace_val_lower_than(df: pd.DataFrame, col_name: str, lower_than_val: float) -> pd.DataFrame:
    """
    replace any value in the column that is lower than specified value with the previous value
    
    Parameters
    ----------
    df: pd.DataFrame
        the dataframe

    col_name: str
        the name of the column to process

    lower_than_val: float
        if below this value change it to previous value

    Returns
    -------
    pd.DataFrame
        the processed dataframe
    """
    condition = df[col_name] < lower_than_val
    df[col_name] = np.where(condition, np.nan, df[col_name])
    df[col_name] = df[col_name].fillna(method='ffill')
    return df
#==========================================================================================================================================================
# endregion: Functions
#==========================================================================================================================================================
#==========================================================================================================================================================
# region: Main
#==========================================================================================================================================================
df = pd.read_csv(grd_loop_path)
df['Date'] = pd.to_datetime(df['Date'], yearfirst=True)
df.set_index('Date', inplace=True)
df = replace_val_lower_than(df, 'Tsup(degC)', 0)
tz = pytz.timezone('America/New_York')
print(df['Tsup(degC)'].idxmax().to_pydatetime().astimezone(tz))
print(df['Tsup(degC)'].idxmax())
mn_mx_dict = lewisctr_utils.find_mx_mn_avg_grd_loop(df, htg_season, clg_season, date_format, timezone)
aday_dfs = lewisctr_utils.sepr_into_days(df, start_yr, start_mth, start_day, end_yr, end_mth, end_day)

if not res_folderpath.exists():
    res_folderpath.mkdir()

# for cnt, aday_df in enumerate(aday_dfs):
#     aday_date_str = aday_df.index[0].to_pydatetime().strftime('%Y_%m_%d_%A')
#     graph_title = 'Lakeside Ground Loop ' + aday_date_str
#     res_path = Path.joinpath(res_folderpath, graph_title)
#     lewisctr_utils.viz_temps(aday_df, cols2viz, color_ls, linestyle_ls, res_path, graph_title)

    # viz_grd_loop(aday_df, res_path, graph_title)
    
#==========================================================================================================================================================
# endregion: Main
#==========================================================================================================================================================