from pathlib import Path
from datetime import datetime

import pytz
import pandas as pd
import lewisctr_utils
#==========================================================================================================================================================
# region: Parameters
#==========================================================================================================================================================
base_path = Path(__file__).parent.parent.parent
data_path = Path.joinpath(base_path, 'data')
folder_name = '2025_2026_may'
grd_loop_path = Path.joinpath(data_path, f'ground_loop/{folder_name}/grd_loop_overall.csv')
res_folderpath = Path.joinpath(data_path, f'ground_loop/{folder_name}/res_img')

cols2viz = ['Tamb(degC)', 'Tsup(degC)', 'Tret(degC)']
color_ls = ['g', 'b', 'r']
linestyle_ls = ['solid', 'solid', 'solid']

# cols2viz = ['Tsup(degC)', 'Tret(degC)']
# color_ls = ['c', 'm']
# linestyle_ls = ['solid', 'solid']

start_yr = 2025
start_mth = 5
start_day = 3
end_yr = 2026
end_mth = 5
end_day = 4
tneu = 10 #degC neutral temperature of the borehole
fall_sem = ['2025-09-01', '2025-12-22']
spring_sem = ['2026-01-25', '2026-05-25']
clg_season = ['2025-05-01', '2025-11-01']
htg_season = ['2025-11-01', '2026-05-01']
date_format = '%Y-%m-%d'
timezone = 'America/New_York'
#==========================================================================================================================================================
# endregion: Parameters
#==========================================================================================================================================================
#==========================================================================================================================================================
# region: Functions
#===============================timezone: str===========================================================================================================================
def find_hottest_coldest_day(df_ls: list[pd.DataFrame], res_folderpath: str, graph_title_base: str, cols2viz: list[str], color_ls: list[str], linestyle_ls: list[str], 
                             yaxis_lim_hottest: list[float] = None, yaxis_lim_coldest: list[float] = None):
    """
    Find the hottest and coldest day from the dataframe list.
    
    Parameters
    ----------
    df_ls: pd.DataFrame
        the list of dataframe to look through

    res_folderpath: str
        folder to save the graphs into

    graph_title_base: str
        base title of the graph

    yaxis_lim_hottest: list[float], optional
        limit of the y-axis for hottest day, default = None
    
    yaxis_lim_coldest: list[float], optional
            limit of the y-axis for coldest day, default = None

    Returns
    -------
    dict
        {'hot': pd.DataFrame, 'cold': pd.DataFrame}
    """
    mx_tambs = []
    mn_tambs = []
    for df in df_ls:
        max_day_tamb = df['Tamb(degC)'].max()
        min_day_tamb = df['Tamb(degC)'].min()
        mx_tambs.append(max_day_tamb)
        mn_tambs.append(min_day_tamb)

    mx_tamb = max(mx_tambs)
    mn_tamb = min(mn_tambs)
    mx_indx = mx_tambs.index(mx_tamb)
    mn_indx = mn_tambs.index(mn_tamb)

    # look at the hottest day
    hday_df = df_ls[mx_indx]
    hday_date_str = hday_df.index[0].to_pydatetime().strftime('%Y_%m_%d_%A')
    graph_title_date = f'{graph_title_base} Hottest {hday_date_str}' 
    res_path = Path.joinpath(res_folderpath, graph_title_date)
    lewisctr_utils.viz_temps(hday_df, cols2viz, color_ls, linestyle_ls, res_path, graph_title_date, yaxis_lim=yaxis_lim_hottest)

    # look at the coldest day
    cday_df = df_ls[mn_indx]
    cday_date_str = cday_df.index[0].to_pydatetime().strftime('%Y_%m_%d_%A')
    graph_title_date = f'{graph_title_base} Coldest {cday_date_str}'
    res_path = Path.joinpath(res_folderpath, graph_title_date)
    lewisctr_utils.viz_temps(cday_df, cols2viz, color_ls, linestyle_ls, res_path, graph_title_date, yaxis_lim=yaxis_lim_coldest)
    return {'hot': hday_df, 'cold': cday_df}

#==========================================================================================================================================================
# endregion: Functions
#==========================================================================================================================================================
#==========================================================================================================================================================
# region: Main
#==========================================================================================================================================================
df = pd.read_csv(grd_loop_path)
df['Date'] = pd.to_datetime(df['Date'], yearfirst=True)
df.set_index('Date', inplace=True)
avg_dicts = lewisctr_utils.find_mx_mn_avg_grd_loop(df, htg_season, clg_season, date_format, timezone)
print(avg_dicts)
aday_dfs = lewisctr_utils.sepr_into_days(df, start_yr, start_mth, start_day, end_yr, end_mth, end_day)

if not res_folderpath.exists():
    res_folderpath.mkdir()

spring_sem_dts = [datetime.strptime(spring_sem[0], date_format).replace(tzinfo=pytz.timezone(timezone)), datetime.strptime(spring_sem[1], date_format).replace(tzinfo=pytz.timezone(timezone))]
fall_sem_dts = [datetime.strptime(fall_sem[0], date_format).replace(tzinfo=pytz.timezone(timezone)), datetime.strptime(fall_sem[1], date_format).replace(tzinfo=pytz.timezone(timezone))]

mx_tambs_sem = []
mn_tambs_sem = []
sem_days = []
for aday_df in aday_dfs:
    aday_pydatetime = aday_df.index[0].to_pydatetime()
    if spring_sem_dts[0] <= aday_pydatetime <= spring_sem_dts[1] or fall_sem_dts[0] <= aday_pydatetime <= fall_sem_dts[1]:
        dow = aday_pydatetime.strftime('%A')
        dt_str = aday_pydatetime.strftime('%Y-%m-%d (%A)')
        if dow not in ['Saturday', 'Sunday']:
            sem_days.append(aday_df)

sem_ht_cld_dict = find_hottest_coldest_day(sem_days, res_folderpath, 'Grd Loop Sem', cols2viz, color_ls, linestyle_ls)
ht_cld_dict = find_hottest_coldest_day(aday_dfs, res_folderpath, 'Grd Loop', cols2viz, color_ls, linestyle_ls)

# get the max approach temp
hday_df = ht_cld_dict['hot']
hday_sup = hday_df['Tsup(degC)'].max()
hday_ret = hday_df['Tret(degC)'].max()
app_temp1 = (hday_sup + hday_ret)/2 
app_temp = app_temp1 - tneu
app_temp_f = lewisctr_utils.degc2degf(app_temp1) - lewisctr_utils.degc2degf(tneu)
print(f'The max supply temp is {hday_sup} degC and the max return temp is {hday_ret} degC')
print(f'The approach temperature is {app_temp} degC, the neutral temperature is {tneu} degC')
print(f'The approach temperature is {app_temp_f} degF, the neutral temperature is {lewisctr_utils.degc2degf(tneu)} degF')

# for cnt, aday_df in enumerate(aday_dfs):
#     aday_date_str = aday_df.index[0].to_pydatetime().strftime('%Y_%m_%d_%A')
#     graph_title = 'Ground Loop Temps ' + aday_date_str
#     res_path = Path.joinpath(res_folderpath, graph_title)
#     lewisctr_utils.viz_temps(aday_df, cols2viz, color_ls, linestyle_ls, res_path, graph_title)

#==========================================================================================================================================================
# endregion: Main
#==========================================================================================================================================================