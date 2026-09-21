from pathlib import Path
import pandas as pd
import geomie3d

import lewisctr_utils
#==========================================================================================================================================================
# region: Parameters
#==========================================================================================================================================================
base_path = Path(__file__).parent.parent.parent
data_path = Path.joinpath(base_path, 'data')
folder_name = '2025_2026_may'
grd_loop_path = Path.joinpath(data_path, f'ground_loop/{folder_name}/grd_loop_enrg.csv')
clw_ld_path = Path.joinpath(data_path, f'chw_loop/{folder_name}/overall.csv')
hw_ld_path = Path.joinpath(data_path, f'hw_loop/{folder_name}/overall.csv')
res_folderpath = Path.joinpath(data_path, f'ground_loop/{folder_name}/loads_grd_chw_res_img')
overall_path = Path.joinpath(data_path, f'chw_loop/{folder_name}/overall.csv')
graph_title = f'Loads of Chilled & Hot Water Loop {folder_name}'
start_yr = 2025
start_mth = 5
start_day = 3
end_yr = 2026
end_mth = 5
end_day = 4
# endregion: Parameters
#==========================================================================================================================================================
# region: Function
#==========================================================================================================================================================
def viz_load_grd_chw_loop(chw_df:pd.DataFrame, hw_df:pd.DataFrame, grd_df:pd.DataFrame, res_path: str, graph_title: str, yaxis1_lim: list[int | float] = None, 
                          yaxis2_lim: list[int | float] = None):
    """
    viz dataframe.
 
    Parameters
    ----------
    chw_df: pd.DataFrame
        chilled water dataframe.
    
    hw_df: pd.DataFrame
        hot water dataframe.

    grd_df: pd.DataFrame
        ground loop dataframe.

    res_path: str
        file path

    graph_tile: str
        graph title

    yaxis1_lim: list[int | float], optional
        limit of yaxis 1, default None
    
    yaxis2_lim: list[int | float], optional
        limit of yaxis 1, default None

    Returns
    -------
    list[float]
        sum of net load and grd load [net_load, grd_load] 
    """
    data_dict_ls1 = []
    data_dict_ls2 = []

    grd_load_j = grd_df['Energy(J)']
    grd_load_btu = lewisctr_utils.joules2btu(grd_load_j)    
    grd_load_kbtu = grd_load_btu/1000

    dts_grd = grd_df.index.to_pydatetime()
    dts_grd_nv = lewisctr_utils.convert_dt2naive(dts_grd)

    clg_load_j = chw_df['Energy(J)']
    clg_load_btu = lewisctr_utils.joules2btu(clg_load_j)
    clg_load_kbtu = clg_load_btu/1000

    dts_clg = chw_df.index.to_pydatetime()
    dts_clg_nv = lewisctr_utils.convert_dt2naive(dts_clg)

    htg_load_j = hw_df['Energy(J)']
    htg_load_btu = lewisctr_utils.joules2btu(htg_load_j)
    htg_load_kbtu = htg_load_btu/1000

    dts_htg = hw_df.index.to_pydatetime()
    dts_htg_nv = lewisctr_utils.convert_dt2naive(dts_htg)

    net_load_j =  htg_load_j - clg_load_j
    net_load_btu = htg_load_btu - clg_load_btu 
    net_load_kbtu = net_load_btu/1000

    data_d = {'datax':dts_clg_nv, 'datay':clg_load_kbtu, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'b', 
              'label': 'clg heat trsf plant loop'}
    data_dict_ls1.append(data_d)

    data_d = {'datax':dts_htg_nv, 'datay':htg_load_kbtu, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'r', 
              'label': 'htg heat trsf plant loop'}
    data_dict_ls1.append(data_d)

    data_d = {'datax':dts_clg_nv, 'datay':clg_load_j/1000000, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'b', 
              'label': 'clg heat trsf plant loop'}
    data_dict_ls2.append(data_d)

    data_d = {'datax':dts_htg_nv, 'datay':htg_load_j/1000000, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'r', 
              'label': 'htg heat trsf plant loop'}
    data_dict_ls2.append(data_d)


    data_d = {'datax':dts_clg_nv, 'datay':net_load_kbtu, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'g', 
              'label': 'htg-clg heat trsf plant loop'}
    data_dict_ls1.append(data_d)

    data_d = {'datax':dts_grd_nv, 'datay':grd_load_kbtu, 'linestyle':'dotted', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'g', 
              'label': 'grd loop heat trsf'}
    data_dict_ls1.append(data_d)

    data_d = {'datax':dts_clg_nv, 'datay':net_load_j/1000000, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'g', 
              'label': 'htg-clg heat trsf plant loop'}
    data_dict_ls2.append(data_d)

    data_d = {'datax':dts_grd_nv, 'datay':grd_load_j/1000000, 'linestyle':'dotted', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'g', 
              'label': 'grd loop heat trsf'}
    data_dict_ls2.append(data_d)
    
    xaxis_label = 'Time (H)'
    yaxis_label1 = 'Energy (kBtu)'
    yaxis_label2 = 'Energy (MJ)'
    dateformat = '%H'
    legend_loc = {'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.3), 'ncol':2}

    geomie3d.utility.viz2axis_timeseries(data_dict_ls1, data_dict_ls2, graph_title, xaxis_label, yaxis_label1, yaxis_label2, 
                                        res_path, dateformat=dateformat, legend_loc1=legend_loc, tight_layout=False, yaxis2_color='k')

    net_enrg_j_sum = net_load_j.sum()
    grd_enrg_j_sum = grd_load_j.sum()
    return [net_enrg_j_sum, grd_enrg_j_sum]

# endregion: Function
#==========================================================================================================================================================
# region: Main
#==========================================================================================================================================================
if not res_folderpath.exists():
    res_folderpath.mkdir()

df_grd = pd.read_csv(grd_loop_path)
df_grd['Date'] = pd.to_datetime(df_grd['Date'], yearfirst=True)
df_grd.set_index('Date', inplace=True)
aday_grd_dfs = lewisctr_utils.sepr_into_days(df_grd, start_yr, start_mth, start_day, end_yr, end_mth, end_day)

df_chw = pd.read_csv(clw_ld_path)
df_chw['Date'] = pd.to_datetime(df_chw['Date'], yearfirst=True)
df_chw.set_index('Date', inplace=True)
aday_chw_dfs = lewisctr_utils.sepr_into_days(df_chw, start_yr, start_mth, start_day, end_yr, end_mth, end_day)

df_hw = pd.read_csv(hw_ld_path)
df_hw['Date'] = pd.to_datetime(df_hw['Date'], yearfirst=True)
df_hw.set_index('Date', inplace=True)
aday_hw_dfs = lewisctr_utils.sepr_into_days(df_hw, start_yr, start_mth, start_day, end_yr, end_mth, end_day)

nchw_dfs = len(aday_chw_dfs)
nhw_dfs = len(aday_hw_dfs)
ngrd_dfs = len(aday_grd_dfs)
ttl_enrg_data = [['date', 'PlantLoopNetHeat(J)', 'GroundLoop(J)']]
if nchw_dfs == nhw_dfs and nhw_dfs == ngrd_dfs:    
    for cnt in range(nchw_dfs):
        aday_chw_df = aday_chw_dfs[cnt]
        aday_hw_df = aday_hw_dfs[cnt]
        aday_grd_df = aday_grd_dfs[cnt]
        aday_chw_date_str = aday_chw_df.index[0].to_pydatetime().strftime('%Y_%m_%d')
        graph_title = 'Heat Transfer Ground & Plant Loop ' + aday_chw_date_str
        res_path = Path.joinpath(res_folderpath, graph_title)
        heat_trsfs = viz_load_grd_chw_loop(aday_chw_df, aday_hw_df, aday_grd_df, res_path, graph_title)
        ttl_enrg_data.append([aday_chw_date_str, heat_trsfs[0], heat_trsfs[1]])

res_path = Path.joinpath(res_folderpath, 'plant_grd_energy_data.csv')
geomie3d.utility.write2csv(ttl_enrg_data, res_path)
#==========================================================================================================================================================
# endregion: Main
#==========================================================================================================================================================
