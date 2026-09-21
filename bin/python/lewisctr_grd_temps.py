from pathlib import Path

import pandas as pd
import geomie3d
import pytz

import lewisctr_utils

#==========================================================================================================================================================
# region: Parameters
#==========================================================================================================================================================
proj_base_path = Path(__file__).parent.parent.parent
data_path = proj_base_path.joinpath('data')
img_path = proj_base_path.joinpath('img')
yr_folder = '2025_2026_may'
#==========================================================================================================================================================
# endregion: Parameters
#==========================================================================================================================================================
#==========================================================================================================================================================
# region: Functions
#==========================================================================================================================================================
def get_mn_mx(df: pd.DataFrame):
    tsup = df['Tsup(degC)']
    tsup_mn = tsup.min()
    tsup_mx = tsup.max()
    tsup_avg = tsup.mean()
    tsup_med = tsup.median()
    print(f"tsup_mn: {tsup_mn}, tsup_mx: {tsup_mx}, tsup_avg: {tsup_avg}, tsup_median: {tsup_med}")
    print(f"tsup_mn: {lewisctr_utils.degc2degf(tsup_mn)}, tsup_mx: {lewisctr_utils.degc2degf(tsup_mx)}, tsup_avg: {lewisctr_utils.degc2degf(tsup_avg)}")
#==========================================================================================================================================================
# endregion: Functions
#==========================================================================================================================================================
#==========================================================================================================================================================
# region: Main
#==========================================================================================================================================================
#----------------------------------------------------------------------------------------------------------
tamb_path = data_path.joinpath(f'ground_loop/{yr_folder}/temperature.csv')
tamb_df = lewisctr_utils.read_clean_resample_csv(tamb_path)
tamb_df['Value'] = lewisctr_utils.degf2degc(tamb_df['Value']) # convert degF to degC
tamb_df['Value'] = tamb_df['Value'].round(decimals=2)
tamb_df.rename(columns={'Value': 'Tamb(degC)'}, inplace=True)
#----------------------------------------------------------------------------------------------------------
tsup_path = data_path.joinpath(f'ground_loop/{yr_folder}/Ground Water Supply TempCSV/Ground Water Supply Temp.csv')
tsup_df = lewisctr_utils.read_clean_resample_csv(tsup_path)
tsup_df['Value'] = lewisctr_utils.degf2degc(tsup_df['Value']) # convert degF to degC
tsup_df['Value'] = tsup_df['Value'].round(decimals=2)
tsup_df.rename(columns={'Value': 'Tsup(degC)'}, inplace=True)
#----------------------------------------------------------------------------------------------------------
tret_path = data_path.joinpath(f'ground_loop/{yr_folder}/Ground Water Return TempCSV/Ground Water Return Temp.csv')
tret_df = lewisctr_utils.read_clean_resample_csv(tret_path)
tret_df['Value'] = lewisctr_utils.degf2degc(tret_df['Value']) # convert degF to degC
tret_df['Value'] = tret_df['Value'].round(decimals=2)
tret_df.rename(columns={'Value': 'Tret(degC)'}, inplace=True)
#----------------------------------------------------------------------------------------------------------
df_overall = pd.concat([tsup_df, tret_df, tamb_df], axis = 1)
df_overall.dropna(inplace=True)
#----------------------------------------------------------------------------------------------------------
# process the datetime for visualization
dts = df_overall.index.to_pydatetime()
dur_dt_dict = lewisctr_utils.get_dur_naivedt(dts, orig_timezone_str='America/New_York')
df_overall['Duration'] = dur_dt_dict['duration']
dts_nv = dur_dt_dict['dts_nv']
overall_path = data_path.joinpath(f'ground_loop/{yr_folder}/overall.csv')
df_overall.to_csv(overall_path)
#----------------------------------------------------------------------------------------------------------
# min, max and avg temps
print('------------------------------------------------------')
print('overall') 
get_mn_mx(df_overall)
#----------------------------------------------------------------------------------------------------------
# separate the temperatures based on dates
start_time_str = ['01-05-2024 00:00:00', '31-10-2024 23:59:00']
se_time_dt1 = pd.to_datetime(start_time_str, dayfirst =True).tz_localize(pytz.timezone('America/New_York'))

start_time_str = ['01-11-2024 00:00:00', '04-05-2025 00:00:00']
se_time_dt2 = pd.to_datetime(start_time_str, dayfirst =True).tz_localize(pytz.timezone('America/New_York'))

clg_season = df_overall.loc[se_time_dt1[0]:se_time_dt1[1]]
htg_season = df_overall.loc[se_time_dt2[0]:se_time_dt2[1]]

print('------------------------------------------------------')
print('heating from Nov to May')
get_mn_mx(htg_season)
print('------------------------------------------------------')
print('cooling from May to Oct')
get_mn_mx(clg_season)

#----------------------------------------------------------------------------------------------------------
# separate the temperatures using a temp threshold
temp_threshold = 10
htg_mins = df_overall[df_overall['Tamb(degC)']<=temp_threshold]
clg_mins = df_overall[df_overall['Tamb(degC)']>temp_threshold]
print('------------------------------------------------------')
print(f"heating below {temp_threshold} degC")
get_mn_mx(htg_mins)
print('------------------------------------------------------')
print(f"cooling above {temp_threshold} degC")
get_mn_mx(clg_mins)
#----------------------------------------------------------------------------------------------------------
# region: viz at the temps overall

data_dict_ls1 = []
data_dict_ls2 = []
tsup = df_overall['Tsup(degC)']
tret = df_overall['Tret(degC)']
tamb = df_overall['Tamb(degC)']

tsupf = lewisctr_utils.degc2degf(df_overall['Tsup(degC)']) 
tretf = lewisctr_utils.degc2degf(df_overall['Tret(degC)'])
tambf = lewisctr_utils.degc2degf(df_overall['Tamb(degC)'])

data_d = {'datax':dts_nv, 'datay':tretf, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'm', 'label': 'return geothermal'}
data_dict_ls1.append(data_d)

data_d = {'datax':dts_nv, 'datay':tambf, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'g', 'label': 'ambient air'}
data_dict_ls1.append(data_d)

data_d = {'datax':dts_nv, 'datay':tsupf, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'k', 'label': 'supply geothermal'}
data_dict_ls1.append(data_d)

data_d = {'datax':dts_nv, 'datay':tret, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'm', 'label': 'return geothermal'}
data_dict_ls2.append(data_d)

data_d = {'datax':dts_nv, 'datay':tamb, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'g', 'label': 'ambient air'}
data_dict_ls2.append(data_d)

data_d = {'datax':dts_nv, 'datay':tsup, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'k', 'label': 'supply geothermal'}
data_dict_ls2.append(data_d)

res_path = img_path.joinpath(f'temperatures_{yr_folder}.png')
xaxis_label = 'Time (Yr/Mth)'
yaxis_label1 = 'Temp (degF)'
yaxis_label2 = 'Temp (degC)'
dateformat = '%y/%m'
legend_loc = {'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.3), 'ncol':2}

graph_title = 'Temperatures 2024-05 to 2025-05'

geomie3d.utility.viz2axis_timeseries(data_dict_ls1, data_dict_ls2, graph_title, xaxis_label, yaxis_label1, yaxis_label2, 
                                     res_path, dateformat=dateformat, legend_loc1=legend_loc, tight_layout=False, yaxis2_color='k')

# endregion: viz at the temps overall  
#----------------------------------------------------------------------------------------------------------
#==========================================================================================================================================================
# endregion: Main
#==========================================================================================================================================================