from pathlib import Path
import pandas as pd
import numpy as np
import geomie3d

import lewisctr_utils
#==========================================================================================================================================================
# region: Parameters
#==========================================================================================================================================================
base_path = Path(__file__).parent.parent.parent
data_path = Path.joinpath(base_path, 'data')
folder_name = '2025_2026_may'
clw_ld_path = Path.joinpath(data_path, f'chw_loop/{folder_name}/CHW Building Load TrendCSV/CHW Building Load Trend.csv')
res_path = Path.joinpath(data_path, f'chw_loop/{folder_name}/clg_loads_chwtr_loop_{folder_name}.png')
overall_path = Path.joinpath(data_path, f'chw_loop/{folder_name}/overall.csv')
graph_title = f'Cooling Load Chilled Water Loop {folder_name}'
# endregion: Parameters
#==========================================================================================================================================================
# region: Main
#==========================================================================================================================================================
clw_ld_df = lewisctr_utils.read_clean_resample_csv(clw_ld_path)
clw_ld_df['Value'] = lewisctr_utils.ton2btuh(clw_ld_df['Value'])
clw_ld_df['Value'] = lewisctr_utils.btuh2watts(clw_ld_df['Value'])
clw_ld_df['Value'] = clw_ld_df['Value'].round(decimals=2)
clw_ld_df.rename(columns={'Value': 'ClgLoad(W)'}, inplace=True)
#----------------------------------------------------------------------------------------------------------
df_overall = pd.concat([clw_ld_df], axis = 1)
df_overall.dropna(inplace=True)
#----------------------------------------------------------------------------------------------------------
# process the datetime for visualization
dts = df_overall.index.to_pydatetime()
dt_dict = lewisctr_utils.get_dur_naivedt(dts)
df_overall['Duration'] = dt_dict['duration']
#----------------------------------------------------------------------------------------------------------
# calc the heat load
dur = df_overall['Duration']
clg_watts = df_overall['ClgLoad(W)']
engy_j = np.where(dur <= 10, clg_watts * dur*60, clg_watts)
df_overall['Energy(J)'] = engy_j
ttl_engy_j = engy_j.sum()
ttl_engy_btu = lewisctr_utils.joules2btu(ttl_engy_j)
print(f"Total cooling load {ttl_engy_btu/1000} kBTU ({ttl_engy_j/1000000} MJ)")

df_overall.to_csv(overall_path)
#----------------------------------------------------------------------------------------------------------
data_dict_ls1 = []
data_dict_ls2 = []

engy_w = engy_j/600
engy_kw = engy_w/1000
engy_btuh = lewisctr_utils.watts2btuh(engy_w)
engy_mbh = engy_btuh/1000

dts_eng = df_overall.index.to_pydatetime()
dts_eng_nv = lewisctr_utils.convert_dt2naive(dts_eng)
data_d = {'datax':dts_eng_nv, 'datay':engy_mbh, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'b', 'label': 'clg'}
data_dict_ls1.append(data_d)

data_d = {'datax':dts_eng_nv, 'datay':engy_kw, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'b', 'label': 'clg'}
data_dict_ls2.append(data_d)

xaxis_label = 'Time (Yr/Mth)'
yaxis_label1 = 'Load (MBH)'
yaxis_label2 = 'Load (kW)'
dateformat = '%y/%m'
legend_loc = {'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.3), 'ncol':2}

geomie3d.utility.viz2axis_timeseries(data_dict_ls1, data_dict_ls2, graph_title, xaxis_label, yaxis_label1, yaxis_label2, 
                                    res_path, dateformat=dateformat, legend_loc1=legend_loc, tight_layout=False, yaxis2_color='k')

#==========================================================================================================================================================
# endregion: Main
#==========================================================================================================================================================
