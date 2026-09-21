from pathlib import Path

import pandas as pd
import lewisctr_utils
#==========================================================================================================================================================
# region: Parameters
#==========================================================================================================================================================
base_path = Path(__file__).parent.parent.parent
data_path = Path.joinpath(base_path, 'data')
folder_name1 = 'ahu5_dance_studio_2_w302'
folder_name2 = '2025_2026_may'
overwrite_merge = True # if set to True even if merge path exists will overwrite the existing merge file 
merge_path = Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/ahu5_dance_studio_2_w302_overall.csv')
filepaths = [Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Setpoint _ Effective Cooling SetpointCSV/Effective Cooling Setpoint.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Setpoint _ Effective Heating SetpointCSV/Effective Heating Setpoint.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Zone TempCSV/Zone Temp.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/AHU SATCSV/AHU SAT.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Discharge TempCSV/Discharge Temp.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Zone RHCSV/Zone RH.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Dmpr PosCSV/Dmpr Pos.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/HW ValveCSV/HW Valve.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Per HW ValveCSV/Per HW Valve.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Occupancy SensorCSV/Occupancy Sensor_resample.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Flow Control _ Flow InputCSV/Flow Input.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Flow StptCSV/Flow Stpt.csv')
             ]
col_names = ['ClgSetpt(degC)', 'HtgSetpt(degC)', 'ZoneAir(degC)', 'SupplyAir(degC)', 'DischargeAir(degC)', 
             'ZoneHumid(%)', 'DmprPos(%)', 'Reheat(%)', 'PmterHeat(%)', 'Occupancy(on/off)',
             'VAVFlow(cmm)', 'VAVFlowSetpt(cmm)']

res_folderpath = Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/res_img')
start_yr = 2025
start_mth = 5
start_day = 3
end_yr = 2026
end_mth = 5
end_day = 4

resampled_cnts = [9]
temp_cnt = 4
cfm_cnt = 10

cols2viz = ['ClgSetpt(degC)', 'HtgSetpt(degC)', 'ZoneAir(degC)', 'SupplyAir(degC)', 'DischargeAir(degC)']
cols2viz2 = ['DmprPos(%)', 'Reheat(%)', 'PmterHeat(%)', 'Occupancy(on/off)']
color_ls = ['b', 'r', 'c', 'm', 'k']
color_ls2 = ['c', 'r', 'y', 'k']
linestyle_ls = ['solid', 'solid', 'solid', 'solid', 'solid']
linestyle_ls2 = ['dotted', 'dotted', 'dotted', 'dotted']
#==========================================================================================================================================================
# endregion: Parameters
#==========================================================================================================================================================
#==========================================================================================================================================================
# region: Functions
#==========================================================================================================================================================   

#==========================================================================================================================================================
# endregion: Functions
#==========================================================================================================================================================
#==========================================================================================================================================================
# region: Main
#==========================================================================================================================================================
if not res_folderpath.exists():
    res_folderpath.mkdir()

if Path(merge_path).exists():
    if overwrite_merge:
        df = lewisctr_utils.merge_ahu_files(filepaths, merge_path, col_names, resampled_cnts, temp_cnt, cfm_cnt)
    else:
        df = pd.read_csv(merge_path)
        df['Date'] = pd.to_datetime(df['Date'], yearfirst=True)
        df.set_index('Date', inplace=True)
else:
    df = lewisctr_utils.merge_ahu_files(filepaths, merge_path, col_names, resampled_cnts, temp_cnt, cfm_cnt)

aday_dfs = lewisctr_utils.sepr_into_days(df, start_yr, start_mth, start_day, end_yr, end_mth, end_day)

for cnt, aday_df in enumerate(aday_dfs):
    aday_date_str = aday_df.index[0].to_pydatetime().strftime('%Y_%m_%d_%A')
    graph_title = f'{folder_name1} {aday_date_str}'
    res_path = Path.joinpath(res_folderpath, graph_title)
    # lewisctr_utils.viz_temps(aday_df, cols2viz, color_ls, linestyle_ls, res_path, graph_title)
    lewisctr_utils.viz_temps_others(aday_df, cols2viz, color_ls, linestyle_ls, cols2viz2, color_ls2, linestyle_ls2, res_path, graph_title)
    
#==========================================================================================================================================================
# endregion: Main
#==========================================================================================================================================================