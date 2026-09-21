from pathlib import Path

import pandas as pd
import lewisctr_utils
#==========================================================================================================================================================
# region: Parameters
#==========================================================================================================================================================
base_path = Path(__file__).parent.parent.parent
data_path = Path.joinpath(base_path, 'data')
folder_name1 = 'ahu7_offices'
folder_name2 = '2025_2026_may'
overwrite_merge = False # if set to True even if merge path exists will overwrite the existing merge file 
merge_path = Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/ahu_overall.csv')
filepaths = [Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Mixed Air TempCSV/Mixed Air Temp.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Leaving Cooling Coil Air TempCSV/Leaving Cooling Coil Air Temp.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Supply Air TempCSV/Supply Air Temp.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Return Air TempCSV/Return Air Temp.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/SA HumidityCSV/SA Humidity.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/RA HumidityCSV/RA Humidity.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/EconomizerCSV/Economizer.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Exhaust Air DamperCSV/Exhaust Air Damper.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Cooling ValveCSV/Cooling Valve.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/Heating ValveCSV/Heating Valve.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/OA CFMCSV/OA CFM.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/SA CFMCSV/SA CFM.csv'),
             Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/RA CFMCSV/RA CFM.csv')
             ]
col_names = ['MixedAir(degC)', 'ClgCoilAir(degC)', 'SupplyAir(degC)', 'RetAir(degC)', 
             'SupplyHumid(%)', 'ReturnHumid(%)',
             'Economizer(%)', 'ExhAirDamper(%)',
             'ClgValve(%)', 'HtgValve(%)', 
             'OutdoorAirFlow(cmm)', 'SupplyAirFlow(cmm)', 'ReturnAirFlow(cmm)']

resampled_cnts = []
temp_cnt = 3
cfm_cnt = 10

cols2viz = ['MixedAir(degC)', 'ClgCoilAir(degC)', 'SupplyAir(degC)', 'RetAir(degC)']
color_ls = ['b', 'c', 'm', 'k']
linestyle_ls = ['solid', 'solid', 'solid', 'solid']

cols2viz2 = ['ClgValve(%)', 'HtgValve(%)']
color_ls2 = ['b', 'r']
linestyle_ls2 = ['dotted', 'dotted']

res_folderpath = Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/res_img')
res_folderpath2 = Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/res_img_valve')
res_folderpath3 = Path.joinpath(data_path, f'{folder_name1}/{folder_name2}/res_img_ppt')
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

if not res_folderpath3.exists():
    res_folderpath3.mkdir()

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
    aday_date_str2 = aday_df.index[0].to_pydatetime().strftime('%Y_%m_%d')
    if aday_date_str2 == '2026_01_30':
        lewisctr_utils.viz_temps_others_seq(aday_df, cols2viz, color_ls, linestyle_ls, cols2viz2, color_ls2, linestyle_ls2, res_folderpath3, graph_title, [45,90], [-5,110])
    if aday_date_str2 == '2026_04_15':
        lewisctr_utils.viz_temps_others_seq(aday_df, cols2viz, color_ls, linestyle_ls, cols2viz2, color_ls2, linestyle_ls2, res_folderpath3, graph_title, [45,85], [-5,110])
        
    res_path = Path.joinpath(res_folderpath, graph_title)
    # lewisctr_utils.viz_temps(aday_df, cols2viz, color_ls, linestyle_ls, res_path, graph_title)
    res_path2 = Path.joinpath(res_folderpath2, graph_title)
    lewisctr_utils.viz_temps_others(aday_df, cols2viz, color_ls, linestyle_ls, cols2viz2, color_ls2, linestyle_ls2, res_path2, graph_title)
    
#==========================================================================================================================================================
# endregion: Main
#==========================================================================================================================================================