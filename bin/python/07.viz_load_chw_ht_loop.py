from pathlib import Path
from datetime import datetime

import pytz
import pandas as pd
import geomie3d

import lewisctr_utils
#==========================================================================================================================================================
# region: Parameters
#==========================================================================================================================================================
base_path = Path(__file__).parent.parent.parent
data_path = Path.joinpath(base_path, 'data')
folder_name = '2025_2026_may'
clw_ld_path = Path.joinpath(data_path, f'chw_loop/{folder_name}/overall.csv')
hw_ld_path = Path.joinpath(data_path, f'hw_loop/{folder_name}/overall.csv')
res_folderpath = Path.joinpath(data_path, f'ground_loop/{folder_name}/loads_chw_hw_loop_res_img')
overall_path = Path.joinpath(data_path, f'chw_loop/{folder_name}/overall.csv')
graph_title = f'Loads of Chilled & Hot Water Loop {folder_name}'

start_end_date = ['2025-05-01', '2026-05-01']
date_format = '%Y-%m-%d'
timezone = 'America/New_York'

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
def viz_load_chw_hw_loop(chw_df:pd.DataFrame, hw_df:pd.DataFrame, res_path: str, graph_title: str, date_format: str, xaxis_labl: str, yaxis1_lim: list[int | float] = None, 
                         yaxis2_lim: list[int | float] = None):
    """
    viz dataframe.
 
    Parameters
    ----------
    chw_df: pd.DataFrame
        chilled water dataframe.
    
    hw_df: pd.DataFrame
        hot water dataframe.

    res_path: str
        file path

    graph_tile: str
        graph title

    date_format: str
        string illustrating the date format, e.g. %Y-%m-$d %H:%M:%S 

    xaxis_labl: str
        label for xaxis
    
    yaxis1_lim: list[int | float], optional
        limit of yaxis 1, default None
    
    yaxis2_lim: list[int | float], optional
        limit of yaxis 1, default None

    """
    data_dict_ls1 = []
    data_dict_ls2 = []

    # clg_load_j = chw_df['Energy(J)']
    # clg_load_btu = lewisctr_utils.joules2btu(clg_load_j)
    clg_load_w = chw_df['ClgLoad(W)']
    clg_load_btuh = lewisctr_utils.watts2btuh(clg_load_w)
    dts_clg = chw_df.index.to_pydatetime()
    dts_clg_nv = lewisctr_utils.convert_dt2naive(dts_clg)

    # htg_load_j = hw_df['Energy(J)']
    # htg_load_btu = lewisctr_utils.joules2btu(htg_load_j)
    htg_load_w = hw_df['HtgLoad(W)']
    htg_load_btuh = lewisctr_utils.watts2btuh(htg_load_w)
    dts_htg = hw_df.index.to_pydatetime()
    dts_htg_nv = lewisctr_utils.convert_dt2naive(dts_htg)

    # net_load_w =  htg_load_w - clg_load_w
    # net_load_btuh = htg_load_btuh - clg_load_btuh
    # data_d = {'datax':dts_clg_nv, 'datay':net_load_btuh/1000, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'b', 
    #           'label': 'htg load-clg load'}
    # data_dict_ls1.append(data_d)
    # data_d = {'datax':dts_clg_nv, 'datay':net_load_w/1000, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'b', 
    #           'label': 'htg load-clg load'}
    # data_dict_ls2.append(data_d)

    data_d = {'datax':dts_clg_nv, 'datay':clg_load_btuh/1000*-1, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'b', 'label': 'clg'}
    data_dict_ls1.append(data_d)

    data_d = {'datax':dts_htg_nv, 'datay':htg_load_btuh/1000, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'r', 'label': 'htg'}
    data_dict_ls1.append(data_d)

    data_d = {'datax':dts_clg_nv, 'datay':clg_load_w/1000*-1, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'b', 'label': 'clg'}
    data_dict_ls2.append(data_d)

    data_d = {'datax':dts_htg_nv, 'datay':htg_load_w/1000, 'linestyle':'solid', 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': 'r', 'label': 'htg'}
    data_dict_ls2.append(data_d)

    xaxis_label = xaxis_labl
    yaxis_label1 = 'Load (MBH)'
    yaxis_label2 = 'Load (kW)'
    legend_loc = {'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.3), 'ncol':2}

    geomie3d.utility.viz2axis_timeseries(data_dict_ls1, data_dict_ls2, graph_title, xaxis_label, yaxis_label1, yaxis_label2, 
                                        res_path, yaxis1_lim=yaxis1_lim, yaxis2_lim=yaxis2_lim, dateformat=date_format, legend_loc1=legend_loc, 
                                        tight_layout=False, yaxis2_color='k')

# endregion: Function
#==========================================================================================================================================================
# region: Main
#==========================================================================================================================================================
if not res_folderpath.exists():
    res_folderpath.mkdir()

df_chw = pd.read_csv(clw_ld_path)
df_chw['Date'] = pd.to_datetime(df_chw['Date'], yearfirst=True)
df_chw.set_index('Date', inplace=True)
# aday_chw_dfs = lewisctr_utils.sepr_into_days(df_chw, start_yr, start_mth, start_day, end_yr, end_mth, end_day)

df_hw = pd.read_csv(hw_ld_path)
df_hw['Date'] = pd.to_datetime(df_hw['Date'], yearfirst=True)
df_hw.set_index('Date', inplace=True)
# aday_hw_dfs = lewisctr_utils.sepr_into_days(df_hw, start_yr, start_mth, start_day, end_yr, end_mth, end_day)

# plot graph for the whole year
res_path = Path.joinpath(res_folderpath, graph_title)
start_end_dts = [datetime.strptime(start_end_date[0], date_format).replace(tzinfo=pytz.timezone(timezone)), datetime.strptime(start_end_date[1], date_format).replace(tzinfo=pytz.timezone(timezone))]
pddts = pd.to_datetime(start_end_dts)
df_chw = df_chw.loc[pddts[0]:pddts[1]]
df_hw = df_hw.loc[pddts[0]:pddts[1]]
date_format = '%y/%m'
viz_load_chw_hw_loop(df_chw, df_hw, res_path, graph_title, date_format, 'Yr-Mth')

# yaxis1_lim = [0, 3500]
# yaxis2_lim = [0, lewisctr_utils.btuh2watts(3500)]
# nchw_dfs = len(aday_chw_dfs)
# nhw_dfs = len(aday_hw_dfs)
# if nchw_dfs == nhw_dfs:
#     for cnt in range(nchw_dfs):
#         aday_chw_df = aday_chw_dfs[cnt]
#         aday_hw_df = aday_hw_dfs[cnt]
#         aday_chw_date_str = aday_chw_df.index[0].to_pydatetime().strftime('%Y_%m_%d')
#         graph_title = 'Loads Chilled & Hot Water Loop ' + aday_chw_date_str
#         res_path = Path.joinpath(res_folderpath, graph_title)
#         date_format = '%H'
#         viz_load_chw_hw_loop(aday_chw_df, aday_hw_df, res_path, graph_title, date_format,'Time (H)')
#         # viz_load_chw_hw_loop(aday_chw_df, aday_hw_df, res_path, graph_title, date_format,'Time (H)', yaxis1_lim=yaxis1_lim, yaxis2_lim=yaxis2_lim)
#==========================================================================================================================================================
# endregion: Main
#==========================================================================================================================================================
