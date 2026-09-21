from pathlib import Path
from datetime import date
import pandas as pd
import numpy as np
import geomie3d

import lewisctr_utils
#==========================================================================================================================================================
# region: Parameters
#==========================================================================================================================================================
base_path = Path(__file__).parent.parent.parent
data_path = Path.joinpath(base_path, 'data')
folder_name = '2024_2025_may'
htw_tsup_path = Path.joinpath(data_path, f'hw_loop/{folder_name}/HWS TempCSV/HWS Temp.csv')
htw_tret_path = Path.joinpath(data_path, f'hw_loop/{folder_name}/RAD HWR TempCSV/RAD HWR Temp.csv')
htw_flw1_path = Path.joinpath(data_path, f'hw_loop/{folder_name}/HW Volume FlowCSV/HW Volume Flow.csv')
htw_flw2_path = Path.joinpath(data_path, f'hw_loop/{folder_name}/HW Volume Flow 2CSV/HW Volume Flow 2.csv')
overall_path = Path.joinpath(data_path, f'hw_loop/{folder_name}/overall.csv')
res_path = Path.joinpath(data_path, f'hw_loop/{folder_name}/htg_loads_hwtr_loop_{folder_name}.png')
graph_title = f'Cooling Load Chilled Water Loop {folder_name}'
# endregion: Parameters
#==========================================================================================================================================================
# region: Main
#==========================================================================================================================================================
htw_tsup_df = lewisctr_utils.read_clean_resample_csv(htw_tsup_path)
htw_tsup_df['Value'] = lewisctr_utils.degf2degc(htw_tsup_df['Value']) # convert degF to degC
htw_tsup_df['Value'] = htw_tsup_df['Value'].round(decimals=2)
htw_tsup_df.rename(columns={'Value': 'HtWaterTsup(degC)'}, inplace=True)
#----------------------------------------------------------------------------------------------------------
htw_tret_df = lewisctr_utils.read_clean_resample_csv(htw_tret_path)
htw_tret_df['Value'] = lewisctr_utils.degf2degc(htw_tret_df['Value']) # convert degF to degC
htw_tret_df['Value'] = htw_tret_df['Value'].round(decimals=2)
htw_tret_df.rename(columns={'Value': 'HtWaterTret(degC)'}, inplace=True)
#----------------------------------------------------------------------------------------------------------
htw_flw1_df = lewisctr_utils.read_clean_resample_csv(htw_flw1_path)
htw_flw1_df['Value'] = lewisctr_utils.gpm2lpm(htw_flw1_df['Value'])
htw_flw1_df['Value'] = htw_flw1_df['Value'].round(decimals=2)
htw_flw1_df.rename(columns={'Value': 'HtWaterFlow1(lpm)'}, inplace=True)
#----------------------------------------------------------------------------------------------------------
htw_flw2_df = lewisctr_utils.read_clean_resample_csv(htw_flw2_path)
htw_flw2_df['Value'] = lewisctr_utils.gpm2lpm(htw_flw2_df['Value'])
htw_flw2_df['Value'] = htw_flw2_df['Value'].round(decimals=2)
htw_flw2_df.rename(columns={'Value': 'HtWaterFlow2(lpm)'}, inplace=True)
#----------------------------------------------------------------------------------------------------------
df_overall = pd.concat([htw_tsup_df, htw_tret_df, htw_flw1_df, htw_flw2_df], axis = 1)
df_overall.dropna(inplace=True)
#----------------------------------------------------------------------------------------------------------
# process the datetime for visualization
dts = df_overall.index.to_pydatetime()
dt_dict = lewisctr_utils.get_dur_naivedt(dts)
df_overall['Duration'] = dt_dict['duration']
#----------------------------------------------------------------------------------------------------------
# calc the heat load
ttl_flow = df_overall['HtWaterFlow1(lpm)'] + df_overall['HtWaterFlow2(lpm)']
dur = df_overall['Duration']
water_mass = np.where(dur <= 10, ttl_flow * dur, ttl_flow)
tdiff = df_overall['HtWaterTsup(degC)'] - df_overall['HtWaterTret(degC)']

engy_j = np.where(tdiff>0, water_mass * 4184 * tdiff, 0)
engy_w = engy_j/600
engy_btu = lewisctr_utils.joules2btu(engy_j)
df_overall['Tsup-Tret(degC)'] = tdiff
df_overall['Energy(J)'] = engy_j
df_overall['HtgLoad(W)'] = engy_w
df_overall.to_csv(overall_path)

ttl_engy_j = engy_j.sum()
ttl_engy_btu = lewisctr_utils.joules2btu(ttl_engy_j)
print(f"Total Heating Energy {ttl_engy_btu/1000} kBTU ({ttl_engy_j/1000000} MJ)")
#----------------------------------------------------------------------------------------------------------
# region: viz at the overall 
#----------------------------------------------------------------------------------------------------------
data_dict_ls1 = []
data_dict_ls2 = []

engy_kw = engy_w/1000
engy_btuh = lewisctr_utils.watts2btuh(engy_w)
engy_mbh = engy_btuh/1000

dts_eng = df_overall.index.to_pydatetime()
dts_eng_nv = lewisctr_utils.convert_dt2naive(dts_eng)
data_d = {'datax':dts_eng_nv, 'datay':engy_mbh, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'r', 'label': 'htg'}
data_dict_ls1.append(data_d)

data_d = {'datax':dts_eng_nv, 'datay':engy_kw, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'r', 'label': 'htg'}
data_dict_ls2.append(data_d)

xaxis_label = 'Time (Yr/Mth)'
yaxis_label1 = 'Load (MBH)'
yaxis_label2 = 'Load (kW)'
dateformat = '%y/%m'
legend_loc = {'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.3), 'ncol':2}

graph_title = 'Heating Load Hot Water Loop 2024-05 to 2025-05'

geomie3d.utility.viz2axis_timeseries(data_dict_ls1, data_dict_ls2, graph_title, xaxis_label, yaxis_label1, yaxis_label2, 
                                     res_path, dateformat=dateformat, legend_loc1=legend_loc, tight_layout=False, yaxis2_color='k')

#----------------------------------------------------------------------------------------------------------
# endregion: viz at the overall 
#----------------------------------------------------------------------------------------------------------
#==========================================================================================================================================================
# endregion: Main
#==========================================================================================================================================================