from pathlib import Path
import lewisctr_utils
#==========================================================================================================================================================
# region: Parameters
#==========================================================================================================================================================
base_path = Path(__file__).parent.parent.parent
data_path = Path.joinpath(base_path, 'data')
year_folder = '2025_2026_may'

chw_path = Path.joinpath(data_path, f'chw_loop/{year_folder}/Primary Chilled Water Supply TempCSV/Primary Chilled Water Supply Temp.csv')
hw_path = Path.joinpath(data_path, f'hw_loop/{year_folder}/HWS TempCSV/HWS Temp.csv')

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
chw_df = lewisctr_utils.read_clean_resample_csv(chw_path, fill_method='ffill')
hw_df = lewisctr_utils.read_clean_resample_csv(hw_path, fill_method='ffill')
chw_med = float(chw_df.median())
chw_min = float(chw_df.min())
chw_max = float(chw_df.max())
chw_avg = float(chw_df.mean())

hw_med = float(hw_df.median())
hw_min = float(hw_df.min())
hw_max = float(hw_df.max())
hw_avg = float(hw_df.mean())

print(f'The median chilled water temp is {chw_med}, avg is {chw_avg}, max is {chw_max} and min is {chw_min} degF')
print(f'The median hot water temp is {hw_med}, avg is {hw_avg}, max is {hw_max} and min is {hw_min} degF')

chw_med_c = round(lewisctr_utils.degf2degc(chw_med),2)
chw_min_c = round(lewisctr_utils.degf2degc(chw_min),2)
chw_max_c = round(lewisctr_utils.degf2degc(chw_max),2)
chw_avg_c = round(lewisctr_utils.degf2degc(chw_avg),2)

hw_med_c = round(lewisctr_utils.degf2degc(hw_med),2)
hw_min_c = round(lewisctr_utils.degf2degc(hw_min),2)
hw_max_c = round(lewisctr_utils.degf2degc(hw_max),2)
hw_avg_c = round(lewisctr_utils.degf2degc(hw_avg),2)

print(f'The median chilled water temp is {chw_med_c}, avg is {chw_avg_c}, max is {chw_max_c} and min is {chw_min_c} degC')
print(f'The median hot water temp is {hw_med_c}, avg is {hw_avg_c}, max is {hw_max_c} and min is {hw_min_c} degC')
#==========================================================================================================================================================
# endregion: Main
#==========================================================================================================================================================