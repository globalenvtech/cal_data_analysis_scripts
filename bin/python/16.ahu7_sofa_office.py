from pathlib import Path

import pandas as pd
import lewisctr_utils
#==========================================================================================================================================================
# region: Parameters
#==========================================================================================================================================================
base_path = Path(__file__).parent.parent.parent
data_path = Path.joinpath(base_path, 'data')
folder_name1 = 'ahu7_sofa_asst_dir_n304'
folder_name2 = '2025_2026_may'
overwrite_merge = False # if set to True even if merge path exists will overwrite the existing merge file 
merge_path = Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/{folder_name1}_overall.csv')
filepaths = [Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Zone Dewpoint TrendCSV/Zone Dewpoint Trend.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Setpoint _ Effective Cooling SetpointCSV/Effective Cooling Setpoint_resample.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Setpoint _ Effective Heating SetpointCSV/Effective Heating Setpoint_resample.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Zone TempCSV/Zone Temp.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/AHU SATCSV/AHU SAT.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Discharge TempCSV/Discharge Temp.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Slab TempCSV/Slab Temp.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Zone RHCSV/Zone RH.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Dmpr PosCSV/Dmpr Pos.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/HW ValveCSV/HW Valve.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Per HW ValveCSV/Per HW Valve.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Occupancy SensorCSV/Occupancy Sensor_resample.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Cooling Valve CommandCSV/Cooling Valve Command_resample.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Cooling Valve StatusCSV/Cooling Valve Status_resample.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Heating Valve CommandCSV/Heating Valve Command_resample.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Heating Valve StatusCSV/Heating Valve Status_resample.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Flow Control _ Flow InputCSV/Flow Input.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Flow StptCSV/Flow Stpt.csv')
             ]
col_names = ['ZoneDewpoint(degC)', 'ClgSetpt(degC)', 'HtgSetpt(degC)', 'ZoneAir(degC)', 'SupplyAir(degC)', 'DischargeAir(degC)', 'SlabTemp(degC)',
             'ZoneHumid(%)', 'DmprPos(%)', 'Reheat(%)', 'PmterHeat(%)', 'Occupancy(on/off)',
             'RadClgVlvCmd(on/off)', 'RadClgVlvSts(on/off)', 'RadHtgVlvCmd(on/off)', 'RadHtgVlvSts(on/off)',
             'VAVFlow(cmm)', 'VAVFlowSetpt(cmm)']

resampled_cnts = [1,2,11,12,13,14,15]
temp_cnt = 6
cfm_cnt = 16

cols2viz = ['ClgSetpt(degC)', 'HtgSetpt(degC)', 'ZoneAir(degC)', 'SupplyAir(degC)', 'DischargeAir(degC)', 'SlabTemp(degC)']
color_ls = ['b', 'r', 'c', 'm', 'y', 'k']
linestyle_ls = ['solid', 'solid', 'solid', 'solid', 'solid', 'solid']
cols2viz2 = ['DmprPos(%)', 'Reheat(%)', 'PmterHeat(%)', 'Occupancy(on/off)', 'RadClgVlvSts(on/off)', 'RadHtgVlvSts(on/off)']
color_ls2 = ['c', 'm', 'y', 'k', 'b', 'r']
linestyle_ls2 = ['dotted', 'dotted', 'dotted', 'dotted', 'dotted', 'dotted']

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
    if not aday_df.empty:
        aday_date_str = aday_df.index[0].to_pydatetime().strftime('%Y_%m_%d_%A')
        graph_title = f'{folder_name1} {aday_date_str}'
        aday_date_str2 = aday_df.index[0].to_pydatetime().strftime('%Y_%m_%d')
        if aday_date_str2 == '2026_01_30':
            lewisctr_utils.viz_temps_others_seq(aday_df, cols2viz, color_ls, linestyle_ls, cols2viz2, color_ls2, linestyle_ls2, res_folderpath2, graph_title, [50,100], [-5,110])
        if aday_date_str2 == '2026_04_15':
            lewisctr_utils.viz_temps_others_seq(aday_df, cols2viz, color_ls, linestyle_ls, cols2viz2, color_ls2, linestyle_ls2, res_folderpath2, graph_title, [50,80], [-5,110])
            
        res_path = Path.joinpath(res_folderpath, graph_title)
        # lewisctr_utils.viz_temps(aday_df, cols2viz, color_ls, linestyle_ls, res_path, graph_title)
        # lewisctr_utils.viz_temps_others(aday_df, cols2viz, color_ls, linestyle_ls, cols2viz2, color_ls2, linestyle_ls2, res_path, graph_title)
        
#==========================================================================================================================================================
# endregion: Main
#==========================================================================================================================================================