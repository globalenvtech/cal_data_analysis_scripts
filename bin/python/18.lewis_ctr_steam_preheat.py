from pathlib import Path
import pandas as pd
import numpy as np
import geomie3d

import lewisctr_utils
#==========================================================================================================================================================
# region: Parameters
#==========================================================================================================================================================
proj_base_path = Path(__file__).parent.parent.parent
stm_preht_base_path = proj_base_path.joinpath('data/stm_preheat')
img_base_path = proj_base_path.joinpath('img')
yr_folder = '2025_2026_may'
#==========================================================================================================================================================
# endregion: Parameters
#==========================================================================================================================================================
#==========================================================================================================================================================
# region: Functions
#==========================================================================================================================================================
def calc_ahu_preheat(ret_cfm_path: str, ret_dmpr_path: str, oa_cfm_path: str, oa_dmpr_path: str, pht_vlv_path: str,
                      bef_pht_temp_path: str, aft_pht_temp_path: str, overall_path: str, sa_cfm_path: str):
    # get return cfm 
    ret_cfm_df = lewisctr_utils.read_clean_resample_csv(ret_cfm_path, fill_method='median')
    ret_cfm_df['Value'] = lewisctr_utils.cfm2cmm(ret_cfm_df['Value']) # convert cubic feet per min to cubic meter per min
    ret_cfm_df.rename(columns={'Value': 'ReturnAirFlow(cmm)'}, inplace=True)
    #----------------------------------------------------------------------------------------------------------
    # get the return damper
    ret_dmpr_df = lewisctr_utils.read_clean_resample_csv(ret_dmpr_path, fill_method='median')
    ret_dmpr_df['Value'] = 100 - ret_dmpr_df['Value']
    ret_dmpr_df.rename(columns={'Value': 'MixOpen(%)'}, inplace=True)
    #----------------------------------------------------------------------------------------------------------
    # get the oa cfm
    oa_cfm_df = lewisctr_utils.read_clean_resample_csv(oa_cfm_path, fill_method='median')
    oa_cfm_df['Value'] = lewisctr_utils.cfm2cmm(oa_cfm_df['Value']) # convert cubic feet per min to cubic meter per min
    oa_cfm_df.rename(columns={'Value': 'OutdoorAirFlow(cmm)'}, inplace=True)
    #----------------------------------------------------------------------------------------------------------
    # get the oa damper
    oa_dmpr_df = lewisctr_utils.read_clean_resample_csv(oa_dmpr_path, fill_method='median')
    oa_dmpr_df['Value'] = oa_dmpr_df['Value']
    oa_dmpr_df.rename(columns={'Value': 'OAOpen(%)'}, inplace=True)
    #----------------------------------------------------------------------------------------------------------
    # get the preheat valve %
    pht_vlv_df = lewisctr_utils.read_clean_resample_csv(pht_vlv_path, fill_method='median')
    pht_vlv_df['Value'] = pht_vlv_df['Value']
    pht_vlv_df.rename(columns={'Value': 'PhtValveOpen(%)'}, inplace=True)
    #----------------------------------------------------------------------------------------------------------
    # get the bef pht temperature
    bef_pht_temp_df = lewisctr_utils.read_clean_resample_csv(bef_pht_temp_path, fill_method='median')
    bef_pht_temp_df['Value'] = lewisctr_utils.degf2degc(bef_pht_temp_df['Value']) # convert degF to degC
    bef_pht_temp_df.rename(columns={'Value': 'BefPhtAirTemp(degC)'}, inplace=True)
    #----------------------------------------------------------------------------------------------------------
    # get the aft pht temperature
    aft_pht_temp_df = lewisctr_utils.read_clean_resample_csv(aft_pht_temp_path, fill_method='median')
    aft_pht_temp_df['Value'] = lewisctr_utils.degf2degc(aft_pht_temp_df['Value']) # convert degF to degC
    aft_pht_temp_df.rename(columns={'Value': 'AftPhtAirTemp(degC)'}, inplace=True)
    #----------------------------------------------------------------------------------------------------------
    # get the aft pht temperature
    if sa_cfm_path != None:
        sa_cfm_df = lewisctr_utils.read_clean_resample_csv(sa_cfm_path, fill_method='median')
        sa_cfm_df['Value'] = lewisctr_utils.cfm2cmm(sa_cfm_df['Value']) # convert cfm to cmm
        sa_cfm_df.rename(columns={'Value': 'SupplyAirFlow(cmm)'}, inplace=True)
        # concatenate all df into one
        df_overall = pd.concat([ret_cfm_df, ret_dmpr_df, oa_cfm_df, oa_dmpr_df, pht_vlv_df, bef_pht_temp_df, aft_pht_temp_df, sa_cfm_df], axis = 1)
    else:
        #----------------------------------------------------------------------------------------------------------
        # concatenate all df into one
        df_overall = pd.concat([ret_cfm_df, ret_dmpr_df, oa_cfm_df, oa_dmpr_df, pht_vlv_df, bef_pht_temp_df, aft_pht_temp_df], axis = 1)
    df_overall.dropna(inplace=True)
    #----------------------------------------------------------------------------------------------------------
    # process the datetime for visualization
    dts = df_overall.index.to_pydatetime()
    dur_dt_dict = lewisctr_utils.get_dur_naivedt(dts, orig_timezone_str='America/New_York')
    df_overall['Duration'] = dur_dt_dict['duration']
    #----------------------------------------------------------------------------------------------------------
    # calculate preheating
    #----------------------------------------------------------------------------------------------------------
    # get the total heating load volume of air
    ret_airflow = df_overall['ReturnAirFlow(cmm)']*(df_overall['MixOpen(%)']/100)
    oa_flow = df_overall['OutdoorAirFlow(cmm)']*(df_overall['OAOpen(%)']/100)
    ttl_flow = ret_airflow + oa_flow
    df_overall['TotalFlow(cmm)'] = ttl_flow
    if sa_cfm_path != None:
        ttl_flow = sa_cfm_df['SupplyAirFlow(cmm)']

    bef_pht = df_overall['BefPhtAirTemp(degC)']
    aft_pht = df_overall['AftPhtAirTemp(degC)']
    tdiff = aft_pht - bef_pht
    pht_vlv = df_overall['PhtValveOpen(%)']
    dur = df_overall['Duration']
    tdiff_index = tdiff.index
    ttl_flow_index = ttl_flow.index
    extra_indices = ttl_flow_index.difference(tdiff_index)
    print(extra_indices)
    ttl_flow = ttl_flow.drop(extra_indices)
    print(len(ttl_flow), len(tdiff), len(pht_vlv))
    phtg_loads = np.where(pht_vlv>0, ttl_flow*1.225*1004*tdiff, 0)
    phtg_loads = np.where(dur<=10, phtg_loads*10, phtg_loads*1)
    phtg_loads = np.where(phtg_loads < 0, 0, phtg_loads)
    df_overall['PhtLoads(J)'] = phtg_loads
    df_overall.to_csv(overall_path)
    #----------------------------------------------------------------------------------------------------------
    
    return df_overall

def calc_ahu3_6_8(ahu_name: str, yr_folder:str, oa_csv_path: str, oa_dmpr_csv_path: str) -> pd.DataFrame:
    ret_cfm_path = stm_preht_base_path.joinpath(f'{ahu_name}/{yr_folder}/RA CFMCSV/RA CFM.csv')
    ret_dmpr_path = stm_preht_base_path.joinpath(f'{ahu_name}/{yr_folder}/Exhaust Air DamperCSV/Exhaust Air Damper.csv')
    oa_cfm_path = stm_preht_base_path.joinpath(f'{ahu_name}/{yr_folder}/{oa_csv_path}')
    oa_dmpr_path = stm_preht_base_path.joinpath(f'{ahu_name}/{yr_folder}/{oa_dmpr_csv_path}')
    pht_vlv_path = stm_preht_base_path.joinpath(f'{ahu_name}/{yr_folder}/Preheat ValveCSV/Preheat Valve.csv')
    bef_pht_temp_path = stm_preht_base_path.joinpath(f'{ahu_name}/{yr_folder}/Mixed Air TempCSV/Mixed Air Temp.csv')
    aft_pht_temp_path = stm_preht_base_path.joinpath(f'{ahu_name}/{yr_folder}/PH Air TempCSV/PH Air Temp.csv')
    
    if yr_folder == '2024_2025_may':
        sa_cfm_path = None
    else:
        sa_cfm_path = stm_preht_base_path.joinpath(f'{ahu_name}/{yr_folder}/SA CFMCSV/SA CFM.csv')

    overall_path = stm_preht_base_path.joinpath(f'{ahu_name}/{yr_folder}/{ahu_name}_stm_pht_overall.csv')
    overall_df = calc_ahu_preheat(ret_cfm_path, ret_dmpr_path, oa_cfm_path, oa_dmpr_path, pht_vlv_path, 
                                  bef_pht_temp_path, aft_pht_temp_path, overall_path, sa_cfm_path)
    return overall_df

def calc_ahu10(sply_cfm_path: str, bef_pht_temp_path: str, aft_pht_temp_path: str, pht_vlv_path: str, overall_path: str) -> pd.DataFrame:
    #----------------------------------------------------------------------------------------------------------
    # get supply cfm 
    sply_cfm_df = lewisctr_utils.read_clean_resample_csv(sply_cfm_path)
    sply_cfm_df['Value'] = lewisctr_utils.cfm2cmm(sply_cfm_df['Value']) # convert cubic feet per min to cubic meter per min
    sply_cfm_df.rename(columns={'Value': 'TotalFlow(cmm)'}, inplace=True)
    #----------------------------------------------------------------------------------------------------------
    # get the bef pht temperature
    bef_pht_temp_df = lewisctr_utils.read_clean_resample_csv(bef_pht_temp_path)
    bef_pht_temp_df['Value'] = lewisctr_utils.degf2degc(bef_pht_temp_df['Value']) # convert degF to degC
    bef_pht_temp_df.rename(columns={'Value': 'BefPhtAirTemp(degC)'}, inplace=True)
    #----------------------------------------------------------------------------------------------------------
    # get the aft pht temperature
    aft_pht_temp_df = lewisctr_utils.read_clean_resample_csv(aft_pht_temp_path)
    aft_pht_temp_df['Value'] = lewisctr_utils.degf2degc(aft_pht_temp_df['Value']) # convert degF to degC
    aft_pht_temp_df.rename(columns={'Value': 'AftPhtAirTemp(degC)'}, inplace=True)
    #----------------------------------------------------------------------------------------------------------
    # get the preheat valve %
    pht_vlv_df = lewisctr_utils.read_clean_resample_csv(pht_vlv_path)
    pht_vlv_df['Value'] = pht_vlv_df['Value']
    pht_vlv_df.rename(columns={'Value': 'PhtValveOpen(%)'}, inplace=True)
    #----------------------------------------------------------------------------------------------------------
    # concatenate all df into one
    df_overall = pd.concat([sply_cfm_df, pht_vlv_df, bef_pht_temp_df, aft_pht_temp_df], axis = 1)
    df_overall.dropna(inplace=True)
    #----------------------------------------------------------------------------------------------------------
    # process the datetime for visualization
    dts = df_overall.index.to_pydatetime()
    dur_dt_dict = lewisctr_utils.get_dur_naivedt(dts, orig_timezone_str='America/New_York')
    df_overall['Duration'] = dur_dt_dict['duration']
    dts_nv = dur_dt_dict['dts_nv']
    #----------------------------------------------------------------------------------------------------------
    # calculate preheating
    #----------------------------------------------------------------------------------------------------------
    # get the total heating load volume of air 
    ttl_flow = df_overall['TotalFlow(cmm)']
    bef_pht = df_overall['BefPhtAirTemp(degC)']
    aft_pht = df_overall['AftPhtAirTemp(degC)']
    tdiff = aft_pht - bef_pht
    pht_vlv = df_overall['PhtValveOpen(%)']
    dur = df_overall['Duration']
    print(len(ttl_flow), len(tdiff))
    phtg_loads = np.where(pht_vlv>0, ttl_flow*1.225*1004*tdiff, 0)
    phtg_loads = np.where(dur<=10, phtg_loads*10, phtg_loads*1)
    phtg_loads = np.where(phtg_loads < 0, 0, phtg_loads)
    df_overall['PhtLoads(J)'] = phtg_loads
    df_overall.to_csv(overall_path)
    #----------------------------------------------------------------------------------------------------------
    return df_overall

#==========================================================================================================================================================
# endregion: Functions
#==========================================================================================================================================================
#==========================================================================================================================================================
# region: Main
#==========================================================================================================================================================
phtg_load_j_ls = []
phtg_load_btu_ls = []
# ahu 3 calculations
ahu_name = 'ahu3'
oa_csv_path = 'OA FlowCSV/OA Flow.csv'
oa_dmpr_path = 'Outside Air DamperCSV/Outside Air Damper.csv'
ahu3_overall_df = calc_ahu3_6_8(ahu_name, yr_folder, oa_csv_path, oa_dmpr_path)
ahu3_overall_df.to_csv()

ahu3_phtg_loads = ahu3_overall_df['PhtLoads(J)']
ttl_phtg_loads_j = ahu3_phtg_loads.sum() # joules
ttl_phtg_loads_btu = lewisctr_utils.joules2btu(ttl_phtg_loads_j)

phtg_load_j_ls.append(ttl_phtg_loads_j)
phtg_load_btu_ls.append(ttl_phtg_loads_btu)
print(f"The annual preheat loads for {ahu_name} is {ttl_phtg_loads_btu/1000} kBtu ({ttl_phtg_loads_j/1000000} MJ) ")
#----------------------------------------------------------------------------------------------------------
# ahu 6 calculations
ahu_name = 'ahu6'
oa_csv_path = 'OA CFMCSV/OA CFM.csv'
oa_dmpr_path = 'Outside Air DamperCSV/Outside Air Damper.csv'
ahu6_overall_df = calc_ahu3_6_8(ahu_name, yr_folder, oa_csv_path, oa_dmpr_path)

ahu6_phtg_loads = ahu6_overall_df['PhtLoads(J)']
ttl_phtg_loads_j = ahu6_phtg_loads.sum() # joules
ttl_phtg_loads_btu = lewisctr_utils.joules2btu(ttl_phtg_loads_j)

phtg_load_j_ls.append(ttl_phtg_loads_j)
phtg_load_btu_ls.append(ttl_phtg_loads_btu)
print(f"The annual preheat loads for {ahu_name} is {ttl_phtg_loads_btu/1000} kBtu ({ttl_phtg_loads_j/1000000} MJ) ")
#----------------------------------------------------------------------------------------------------------
# ahu 8 calculations
ahu_name = 'ahu8'
oa_csv_path = 'OA FlowCSV/OA Flow.csv'
oa_dmpr_path = 'EconomizerCSV/Economizer.csv'
ahu8_overall_df = calc_ahu3_6_8(ahu_name, yr_folder, oa_csv_path, oa_dmpr_path)

ahu8_phtg_loads = ahu8_overall_df['PhtLoads(J)']
ttl_phtg_loads_j = ahu8_phtg_loads.sum() # joules
ttl_phtg_loads_btu = lewisctr_utils.joules2btu(ttl_phtg_loads_j)

phtg_load_j_ls.append(ttl_phtg_loads_j)
phtg_load_btu_ls.append(ttl_phtg_loads_btu)
print(f"The annual preheat loads for {ahu_name} is {ttl_phtg_loads_btu/1000} kBtu ({ttl_phtg_loads_j/1000000} MJ) ")
#----------------------------------------------------------------------------------------------------------
# ahu 10 calculations

sply_cfm_path = stm_preht_base_path.joinpath(f'ahu10/{yr_folder}/SA CFMCSV/SA CFM.csv')
bef_pht_temp_path = stm_preht_base_path.joinpath(f'ahu10/{yr_folder}/temperature.csv')
aft_pht_temp_path = stm_preht_base_path.joinpath(f'ahu10/{yr_folder}/PH Air TempCSV/PH Air Temp.csv')
pht_vlv_path = stm_preht_base_path.joinpath(f'ahu10/{yr_folder}/Preheat ValveCSV/Preheat Valve.csv')
overall_path = stm_preht_base_path.joinpath(f'ahu10/{yr_folder}/ahu10_stm_pht_overall.csv')
ahu10_overall_df = calc_ahu10(sply_cfm_path, bef_pht_temp_path, aft_pht_temp_path, pht_vlv_path, overall_path)

ahu10_phtg_loads = ahu10_overall_df['PhtLoads(J)']
ttl_phtg_loads_j = ahu10_phtg_loads.sum() # joules
ttl_phtg_loads_btu = lewisctr_utils.joules2btu(ttl_phtg_loads_j)

phtg_load_j_ls.append(ttl_phtg_loads_j)
phtg_load_btu_ls.append(ttl_phtg_loads_btu)
print(f"The annual preheat loads for ahu10 is {ttl_phtg_loads_btu/1000} kBtu ({ttl_phtg_loads_j/1000000} MJ) ")
#----------------------------------------------------------------------------------------------------------
ttl_ahu_phtg_j = sum(phtg_load_j_ls)
ttl_ahu_phtg_btu = sum(phtg_load_btu_ls)

print(f"Total preheat loads for all AHUs is {ttl_ahu_phtg_btu/1000} kBtu ({ttl_ahu_phtg_j/1000000} MJ)")
#----------------------------------------------------------------------------------------------------------
# viz at the loads overall
xaxis_label = 'Time (Yr/Mth)'
yaxis_label1 = 'Loads (Mbh)'
yaxis_label2 = 'Loads (kW)'
dateformat = '%y/%m'
legend_loc = {'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.3), 'ncol':2}
ylim1 = None #[0,150]
ylim2 = None #[0,50]
#----------------------------------------------------------------------------------------------------------
# viz ahu3 loads
data_dict_ls1 = []
data_dict_ls2 = []
ahu_watts = ahu3_phtg_loads/600
ahu_kw = ahu_watts/1000
ahu_bh = lewisctr_utils.watts2btuh(ahu_watts)
ahu_mbh = ahu_bh/1000

dts = ahu3_phtg_loads.index.to_pydatetime()
dts_nv = lewisctr_utils.convert_dt2naive(dts, orig_timezone_str='America/New_York')

data_d = {'datax':dts_nv, 'datay':ahu_mbh, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'r', 'label': 'ahu3'}
data_dict_ls1.append(data_d)

data_d = {'datax':dts_nv, 'datay':ahu_kw, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'r', 'label': 'ahu3'}
data_dict_ls2.append(data_d)

res_path = img_base_path.joinpath(f'ahu3_preheat_{yr_folder}.png')
graph_title = f'AHU3 preheat {yr_folder}'

geomie3d.utility.viz2axis_timeseries(data_dict_ls1, data_dict_ls2, graph_title, xaxis_label, yaxis_label1, yaxis_label2, 
                                     res_path, dateformat=dateformat, legend_loc1=legend_loc, tight_layout=False, yaxis2_color='k',  
                                     yaxis1_lim=ylim1, yaxis2_lim=ylim2, viz=False)

#----------------------------------------------------------------------------------------------------------
# viz ahu6 loads
data_dict_ls1 = []
data_dict_ls2 = []
ahu_watts = ahu6_phtg_loads/600
ahu_kw = ahu_watts/1000
ahu_bh = lewisctr_utils.watts2btuh(ahu_watts)
ahu_mbh = ahu_bh/1000

dts = ahu6_phtg_loads.index.to_pydatetime()
dts_nv = lewisctr_utils.convert_dt2naive(dts, orig_timezone_str='America/New_York')

data_d = {'datax':dts_nv, 'datay':ahu_mbh, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'g', 'label': 'ahu6'}
data_dict_ls1.append(data_d)

data_d = {'datax':dts_nv, 'datay':ahu_kw, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'g', 'label': 'ahu6'}
data_dict_ls2.append(data_d)

res_path = img_base_path.joinpath(f'ahu6_preheat_{yr_folder}.png')
graph_title = f'AHU6 preheat {yr_folder}'

geomie3d.utility.viz2axis_timeseries(data_dict_ls1, data_dict_ls2, graph_title, xaxis_label, yaxis_label1, yaxis_label2, 
                                     res_path, dateformat=dateformat, legend_loc1=legend_loc, tight_layout=False, yaxis2_color='k',
                                     yaxis1_lim=ylim1, yaxis2_lim=ylim2, viz=False)
#----------------------------------------------------------------------------------------------------------
# viz ahu8 loads
data_dict_ls1 = []
data_dict_ls2 = []
ahu_watts = ahu8_phtg_loads/600
ahu_kw = ahu_watts/1000
ahu_bh = lewisctr_utils.watts2btuh(ahu_watts)
ahu_mbh = ahu_bh/1000

dts = ahu8_phtg_loads.index.to_pydatetime()
dts_nv = lewisctr_utils.convert_dt2naive(dts, orig_timezone_str='America/New_York')

data_d = {'datax':dts_nv, 'datay':ahu_mbh, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'b', 'label': 'ahu8'}
data_dict_ls1.append(data_d)

data_d = {'datax':dts_nv, 'datay':ahu_kw, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'b', 'label': 'ahu8'}
data_dict_ls2.append(data_d)

res_path = img_base_path.joinpath(f'ahu8_preheat_{yr_folder}.png')
graph_title = f'AHU8 preheat {yr_folder}'

geomie3d.utility.viz2axis_timeseries(data_dict_ls1, data_dict_ls2, graph_title, xaxis_label, yaxis_label1, yaxis_label2, 
                                     res_path, dateformat=dateformat, legend_loc1=legend_loc, tight_layout=False, yaxis2_color='k',
                                     yaxis1_lim=ylim1, yaxis2_lim=ylim2, viz=False)
#----------------------------------------------------------------------------------------------------------
# viz ahu10 loads
data_dict_ls1 = []
data_dict_ls2 = []
ahu_watts = ahu10_phtg_loads/600
ahu_kw = ahu_watts/1000
ahu_bh = lewisctr_utils.watts2btuh(ahu_watts)
ahu_mbh = ahu_bh/1000

dts = ahu10_phtg_loads.index.to_pydatetime()
dts_nv = lewisctr_utils.convert_dt2naive(dts, orig_timezone_str='America/New_York')

data_d = {'datax':dts_nv, 'datay':ahu_mbh, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'k', 'label': 'ahu10'}
data_dict_ls1.append(data_d)

data_d = {'datax':dts_nv, 'datay':ahu_kw, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'k', 'label': 'ahu10'}
data_dict_ls2.append(data_d)

res_path = img_base_path.joinpath(f'ahu10_preheat_{yr_folder}.png')
graph_title = f'AHU10 preheat {yr_folder}'

geomie3d.utility.viz2axis_timeseries(data_dict_ls1, data_dict_ls2, graph_title, xaxis_label, yaxis_label1, yaxis_label2, 
                                     res_path, dateformat=dateformat, legend_loc1=legend_loc, tight_layout=False, yaxis2_color='k',
                                     yaxis1_lim=ylim1, yaxis2_lim=ylim2, viz=False)