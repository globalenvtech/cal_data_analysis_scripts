from pathlib import Path

import pandas as pd
import lewisctr_utils
#==========================================================================================================================================================
# region: Parameters
#==========================================================================================================================================================
base_path = Path(__file__).parent.parent.parent
data_path = Path.joinpath(base_path, 'data')
folder_name1 = 'ahu8_forum_amphitheatre'
folder_name2 = '2025_2026_may'
folder_name3 = 'vav'
overwrite_merge = False # if set to True even if merge path exists will overwrite the existing merge file 
merge_path = Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/{folder_name1}_{folder_name3}_overall.csv')
filepaths = [Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/{folder_name3}/Zone 1 Dewpoint TrendCSV/Zone 1 Dewpoint Trend.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/{folder_name3}/Zone 2 Dewpoint TrendCSV/Zone 2 Dewpoint Trend.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/{folder_name3}/Zone 3 Dewpoint TrendCSV/Zone 3 Dewpoint Trend.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/{folder_name3}/Setpoint _ Effective Cooling SetpointCSV/Effective Cooling Setpoint_resample.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/{folder_name3}/Setpoint _ Effective Heating SetpointCSV/Effective Heating Setpoint_resample.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/{folder_name3}/Zone 1 TempCSV/Zone 1 Temp.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/{folder_name3}/Zone Temp 2 TrendCSV/Zone Temp 2 Trend.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/{folder_name3}/Zone Temp 3 TrendCSV/Zone Temp 3 Trend.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/{folder_name3}/AHU SATCSV/AHU SAT.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/{folder_name3}/Discharge TempCSV/Discharge Temp.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/{folder_name3}/Zone 1 RHCSV/Zone 1 RH.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/{folder_name3}/Dmpr PosCSV/Dmpr Pos.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/{folder_name3}/HW ValveCSV/HW Valve.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/{folder_name3}/Sensed OccupancyCSV/Sensed Occupancy_resample.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/{folder_name3}/Flow Control _ Flow InputCSV/Flow Input.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/{folder_name3}/Flow StptCSV/Flow Stpt.csv')
             ]
col_names = ['Zone1Dewpoint(degC)', 'Zone2Dewpoint(degC)', 'Zone3Dewpoint(degC)', 'ClgSetpt(degC)', 'HtgSetpt(degC)', 
             'Zone1Air(degC)', 'Zone2Air(degC)', 'Zone3Air(degC)', 'SupplyAir(degC)', 'DischargeAir(degC)',
             'ZoneHumid(%)', 'DmprPos(%)', 'Reheat(%)', 'Occupancy(on/off)',
             'VAVFlow(cmm)', 'VAVFlowSetpt(cmm)']

resampled_cnts = [3,4,13]
temp_cnt = 9
cfm_cnt = 14

cols2viz = ['ClgSetpt(degC)', 'HtgSetpt(degC)', 'Zone1Air(degC)', 'Zone2Air(degC)', 'Zone3Air(degC)', 'SupplyAir(degC)', 'DischargeAir(degC)']
color_ls = ['b', 'r', 'c', 'g', 'tab:orange', 'm', 'y']
linestyle_ls = ['solid', 'solid', 'solid', 'solid', 'solid', 'solid', 'solid']
cols2viz2 = ['DmprPos(%)', 'Reheat(%)', 'Occupancy(on/off)']
color_ls2 = ['c', 'm', 'k']
linestyle_ls2 = ['dotted', 'dotted', 'dotted']

res_folderpath = Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/{folder_name3}/res_img')
start_yr = 2025
start_mth = 5
start_day = 3
end_yr = 2026
end_mth = 5
end_day = 4
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
    if not aday_df.empty:
        aday_date_str = aday_df.index[0].to_pydatetime().strftime('%Y_%m_%d_%A')
        graph_title = f'{folder_name1} {aday_date_str}'
        res_path = Path.joinpath(res_folderpath, graph_title)
        # lewisctr_utils.viz_temps(aday_df, cols2viz, color_ls, linestyle_ls, res_path, graph_title)
        lewisctr_utils.viz_temps_others(aday_df, cols2viz, color_ls, linestyle_ls, cols2viz2, color_ls2, linestyle_ls2, res_path, graph_title)
        
#==========================================================================================================================================================
# endregion: Main
#==========================================================================================================================================================