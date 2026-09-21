from pathlib import Path

import pandas as pd
import lewisctr_utils
#==========================================================================================================================================================
# region: Parameters
#==========================================================================================================================================================
base_path = Path(__file__).parent.parent.parent
data_path = Path.joinpath(base_path, 'data')
folder_name1 = 'ahu2_practice2_e315'
folder_name2 = '2025_2026_may'
overwrite_merge = False # if set to True even if merge path exists will overwrite the existing merge file 
merge_path = Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/practice2_e315_overall.csv')
filepaths = [Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Zone DewpointCSV/Zone Dewpoint.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Setpoint _ Effective Cooling SetpointCSV/Effective Cooling Setpoint_resample.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Setpoint _ Effective Heating SetpointCSV/Effective Heating Setpoint_resample.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Zone TempCSV/Zone Temp.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Supply Air TempCSV/Supply Air Temp.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Slab TemperatureCSV/Slab Temperature.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Swirl DiffuserCSV/Swirl Diffuser.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Zone HumidityCSV/Zone Humidity.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Occupancy SensorCSV/Occupancy Sensor_resample.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Cool ModeCSV/Cool Mode_resample.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Heat ModeCSV/Heat Mode_resample.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Radiant Cooling ValveCSV/Radiant Cooling Valve_resample.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Radiant Cooling Valve StatusCSV/Radiant Cooling Valve Status_resample.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Radiant Heat ValveCSV/Radiant Heat Valve_resample.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Radiant Heat Valve StatusCSV/Radiant Heat Valve Status_resample.csv')
             ]
col_names = ['ZoneDewpoint(degC)', 'ClgSetpt(degC)', 'HtgSetpt(degC)', 'ZoneAir(degC)', 'SupplyAir(degC)', 'SlabTemp(degC)', 
             'SwirlDiff(%)', 'ZoneHumid(%)',
             'Occupancy(on/off)', 'CoolMode(on/off)', 'HeatMode(on/off)',
             'RadClgVlvCmd(on/off)', 'RadClgVlvSts(on/off)', 'RadHtgVlvCmd(on/off)', 'RadHtgVlvSts(on/off)']

resampled_cnts = [1,2,8,9,10,11,12,13,14]
temp_cnt = 5
cfm_cnt = 15

cols2viz = ['ClgSetpt(degC)', 'HtgSetpt(degC)', 'ZoneAir(degC)', 'SupplyAir(degC)', 'SlabTemp(degC)']
color_ls = ['b', 'r', 'c', 'm', 'k']
linestyle_ls = ['solid', 'solid', 'solid', 'solid', 'solid']

cols2viz2 = ['SwirlDiff(%)', 'Occupancy(on/off)','RadClgVlvSts(on/off)', 'RadHtgVlvSts(on/off)']
color_ls2 = ['c', 'k', 'b', 'r']
linestyle_ls2 = ['dotted', 'dotted', 'dotted', 'dotted', 'dotted']

res_folderpath = Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/res_img')
res_folderpath2 = Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/res_img_ppt')
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
#    
#==========================================================================================================================================================
# endregion: Functions
#==========================================================================================================================================================
#==========================================================================================================================================================
# region: Main
#==========================================================================================================================================================
if not res_folderpath.exists():
    res_folderpath.mkdir()

if not res_folderpath2.exists():
    res_folderpath2.mkdir()

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
    aday_date_str2 = aday_df.index[0].to_pydatetime().strftime('%Y_%m_%d')
    graph_title = f'{folder_name1} {aday_date_str}'

    if aday_date_str2 == '2026_01_30' :
        lewisctr_utils.viz_temps_others_seq(aday_df, cols2viz, color_ls, linestyle_ls, cols2viz2, color_ls2, linestyle_ls2, res_folderpath2, graph_title, [45,75], [-5,110])
    if aday_date_str2 == '2026_04_15':
        lewisctr_utils.viz_temps_others_seq(aday_df, cols2viz, color_ls, linestyle_ls, cols2viz2, color_ls2, linestyle_ls2, res_folderpath2, graph_title, [50,80], [-5,110])

    # res_path = Path.joinpath(res_folderpath, graph_title)
    # # lewisctr_utils.viz_temps(aday_df, cols2viz, color_ls, linestyle_ls, res_path, graph_title)
    # lewisctr_utils.viz_temps_others(aday_df, cols2viz, color_ls, linestyle_ls, cols2viz2, color_ls2, linestyle_ls2, res_path, graph_title)
    
#==========================================================================================================================================================
# endregion: Main
#==========================================================================================================================================================