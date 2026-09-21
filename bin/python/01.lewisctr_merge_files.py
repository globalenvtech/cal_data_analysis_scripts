from pathlib import Path
import pandas as pd

import lewisctr_utils
#==========================================================================================================================================================
# region: Parameters
#==========================================================================================================================================================
# merge all the csv files into a single file, each file becomes a column
base_path = Path(__file__).parent.parent.parent
data_path = Path.joinpath(base_path, 'data')
folder_name1 = 'ahu2_music_glass'
folder_name2 = '2025_2026_may'
filepaths = [Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/CWS TempCSV/CWS Temp.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/CWR TempCSV/CWR Temp.csv')]
col_names = ['Tsup(degC)', 'Tret(degC)']
merge_path = Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/grd_loop_overall.csv')
#==========================================================================================================================================================
# endregion: Parameters
#==========================================================================================================================================================
#==========================================================================================================================================================
# region: Main
#==========================================================================================================================================================
dfs = []
for cnt, filepath in enumerate(filepaths):
    df = lewisctr_utils.read_clean_resample_csv(filepath)
    df['Value'] = lewisctr_utils.degf2degc(df['Value']) # convert degF to degC
    df['Value'] = df['Value'].round(decimals=2)
    df.rename(columns={'Value': col_names[cnt]}, inplace=True)
    dfs.append(df)

df_overall = pd.concat(dfs, axis = 1)
df_overall.dropna(inplace=True)

# process the datetime to get the duration
dts = df_overall.index.to_pydatetime()
dur_dt_dict = lewisctr_utils.get_dur_naivedt(dts, orig_timezone_str='America/New_York')
df_overall['Duration'] = dur_dt_dict['duration']
df_overall.to_csv(merge_path)
#==========================================================================================================================================================
# endregion: Main
#==========================================================================================================================================================