from pathlib import Path
import pandas as pd

import lewisctr_utils
#==========================================================================================================================================================
# region: Parameters
#==========================================================================================================================================================
# merge all the csv files into a single file, each file becomes a column
base_path = Path(__file__).parent.parent.parent
data_path = Path.joinpath(base_path, 'data')
folder_name1 = 'ahu2_practice2_e315'
folder_name2 = '2025_2026_may'
folder_name3 = 'Radiant Heat Valve Status'
file_name = folder_name3
filepath = Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/{folder_name3}CSV/{file_name}.csv')
res_path = Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/{folder_name3}CSV/{file_name}_resample.csv')
#----------------------------------------------------------------------------------------------------------------
reindex2target_date = False
target_date = '2026-05-04T00:00:00+00:00'
#----------------------------------------------------------------------------------------------------------------
is_temp = False
onoff2pct = True
#==========================================================================================================================================================
# endregion: Parameters
#==========================================================================================================================================================
#==========================================================================================================================================================
# region: Main
#==========================================================================================================================================================
df = lewisctr_utils.read_clean_resample_csv(filepath, fill_method='ffill')
if reindex2target_date:
    start_date = df.index[0].to_pydatetime().isoformat()
    target_index = pd.date_range(start=start_date, end=target_date, freq='10min')
    df = df.reindex(target_index)
    df.index.name = 'Date'
    df = df.ffill()
if is_temp == True:
    df['Value'] = lewisctr_utils.degf2degc(df['Value']) # convert degF to degC
    df['Value'] = df['Value'].round(decimals=2)
if onoff2pct == True:
    df['Value'] = df['Value']*100 # convert on/off to %

print(df)
df.to_csv(res_path)
#==========================================================================================================================================================
# endregion: Main
#==========================================================================================================================================================