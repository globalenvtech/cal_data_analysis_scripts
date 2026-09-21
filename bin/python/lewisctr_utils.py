import datetime
from pathlib import Path

import matplotlib.axes
import pytz
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

import geomie3d

def read_dt_csv2df(csv_path: str) -> pd.DataFrame:
    """
    Read and convert csv to dataframe with proper datetime index. The datetime is converted to utc timezone
 
    Parameters
    ----------
    csv_path: str
        csv path.
        
    Returns
    -------
    csv_df : pd.DataFrame
        correctly datetime df
    """
    df = pd.read_csv(csv_path, sep = ',', skiprows=1)
    df['TimeZone'] = df['Date'].str.slice(start=-3)
    # df['TimeZone'] = df['Date'].apply(lambda x: x[-3:])
    df['TimeZone'] = np.where(df['TimeZone'] == 'EDT', '-04:00', '-05:00') # EDT == -4:00, EST == -5:00
    df['Date'] = df['Date'].str.slice(start=0, stop=-3)
    df['Date'] = df['Date'].astype('datetime64[ms]').dt.strftime('%Y/%m/%d %H:%M:%S')
    df['Date'] = df['Date'] + df['TimeZone']
    df['OrigDate'] = df['Date']
    df['Date'] = pd.to_datetime(df['Date'], utc=True, format='ISO8601')
    df = df.drop_duplicates(subset='Date')
    df.set_index('Date', inplace=True)
    df.drop('TimeZone', axis = 1, inplace=True)
    return df

def read_clean_resample_csv(csv_path: str, resample: str = '10min', fill_method: str = 'median') -> pd.DataFrame:
    """
    Read, clean up and resample the Lewis Center BAS csv.
 
    Parameters
    ----------
    csv_path: str
        csv path.

    resample: str, optional
        default == '10min'
    
    fill_method: str, optional
        default is median, other option include 'ffill'
    
    Returns
    -------
    csv_df : pd.DataFrame
        correctly datetime, cleaned and resample df
    """
    df = read_dt_csv2df(csv_path)
    df.drop('Notes', axis=1, inplace=True)
    df.drop('Excel Time', axis=1, inplace=True)
    df.drop('OrigDate', axis=1, inplace=True)
    if fill_method == 'median':
        df = df.resample(resample).median()
    elif fill_method == 'ffill':
        df = df.resample(resample).ffill()
    elif fill_method == 'max':
            df = df.resample(resample).max()
    elif fill_method == 'min':
                df = df.resample(resample).min()
    df.dropna(inplace=True)
    return df

def get_dur_naivedt(dts: list[datetime.datetime], orig_timezone_str: str = 'America/New_York') -> dict:
    """
    convert datetime obj to naive datetime obj and find the duration between each datetime row.
 
    Parameters
    ----------
    dts: list[datetime.datetime]
        list of python datetime object

    orig_timezone_str: str, optional
        timezone list (https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568)
        
    Returns
    -------
    res_dict: dict
        'duration': list[float], 'dts_nv': list[naive datetime.datetime].
    """
    edt = pytz.timezone(orig_timezone_str)
    dts_nv = []
    dur = []
    for cnt, dt in enumerate(dts):
        dt_edt = dt.astimezone(edt)
        dt_nv = dt_edt.replace(tzinfo = None)
        dts_nv.append(dt_nv)
        if cnt != len(dts)-1:
            dt2 = dts[cnt+1]
            td = dt2 - dt
            td_mins = round(td.total_seconds()/60.0, 1)
            # if td_mins != 10:
            #     print(dt2, dt, td_mins)
            dur.append(td_mins)
        else:
            dur.append(1)

    return {'duration': dur, 'dts_nv': dts_nv}

def convert_dt2naive(dts: list[datetime.datetime], orig_timezone_str: str = 'America/New_York') -> list[datetime.datetime]:
    """
    convert datetime obj to naive datetime obj for viz with geomie3d.utils.
 
    Parameters
    ----------
    dts: list[datetime.datetime]
        list of python datetime object

    orig_timezone_str: str, optional
        timezone list (https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568)
        
    Returns
    -------
    dts_nv : list[datetime.datetime]
        naive datetime objects.
    """
    edt = pytz.timezone(orig_timezone_str)
    dts_nv = []
    for dt in dts:
        dt_edt = dt.astimezone(edt)
        dt_nv = dt_edt.replace(tzinfo = None)
        dts_nv.append(dt_nv)
    return dts_nv

def merge_ahu_files(filepaths: list[str], merge_path: str, col_names: list[str], processed_cnts: list[int], temp_cnt: int, cfm_cnt: int) -> pd.DataFrame:
    """
    merge files into an overall file.
 
    Parameters
    ----------
    filepaths: list[str]
        path of all the files to merge
    
    merge_path: str
        save the merge file to this path

    processed_cnts: list[int]
        the index in the filepaths where the file is already processed and does not need to be clean and resample, put an empty list [] if you do not have this file
    
    temp_cnt: int
        the index in the filepaths where below and equal this index all the files are temperatures

    cfm_cnt: int
        the index in the filepaths where above and equal this index all the files are cfm

    Returns
    -------
    pd.DataFrame
        merge dataframe
    """
    dfs = []
    for cnt, filepath in enumerate(filepaths):
        if cnt not in processed_cnts:
            df = read_clean_resample_csv(filepath)    
            if cnt <= temp_cnt:
                df['Value'] = degf2degc(df['Value']) # convert degF to degC
                df['Value'] = df['Value'].round(decimals=2)
            elif cnt >= cfm_cnt: 
                df['Value'] = cfm2cmm(df['Value']) # convert cfm to cmm
                df['Value'] = df['Value'].round(decimals=2)
        else:
            print(filepath)
            df = pd.read_csv(filepath)
            df['Date'] = pd.to_datetime(df['Date'], yearfirst=True)
            df.set_index('Date', inplace=True)
        df.rename(columns={'Value': col_names[cnt]}, inplace=True)
        dfs.append(df)

    df_overall = pd.concat(dfs, axis = 1)
    df_overall.dropna(inplace=True)

    # process the datetime to get the duration
    dts = df_overall.index.to_pydatetime()
    dur_dt_dict = get_dur_naivedt(dts, orig_timezone_str='America/New_York')
    df_overall['Duration'] = dur_dt_dict['duration']
    df_overall.to_csv(merge_path)
    return df_overall

def gen_days(start_yr: int, start_mth: int, start_day:int, end_yr: int, end_mth: int, end_day:int) -> list[pd.Timestamp]:
    """
    start_yr: int
        start yr
    
    start_mth: int
        start month

    start_day: int
        start day

    end_yr: int
        end yr
    
    end_mth: int
        end month

    end_day: int
        end day
 
    Parameters
    ----------
    csv_path: str
        csv path.
        
    Returns
    -------
    list[pd.Timestamp]
        list of days timestamp
    """
    start_date = datetime.datetime(start_yr, start_mth, start_day)
    end_date = datetime.datetime(end_yr, end_mth, end_day)
    delta = datetime.timedelta(days=1)

    date_list = []
    current_date = start_date
    while current_date <= end_date:
        pd_datetime = pd.to_datetime(current_date)
        date_list.append(pd_datetime)
        current_date += delta
    return date_list

def find_mx_mn_avg_grd_loop(df: pd.DataFrame, htg_season: list[str], clg_season: list[str], date_format: str, timezone = str) -> dict:
    """
    Find the max, min and average supply temperatures.
    
    Parameters
    ----------
    df: pd.DataFrame
        dataframe to look through

    htg_season: list[str]
        the dates of the heating season in string

    clg_season: list[str]
        the dates of the cooling season in string

    date_format: str
        format of the string, e.g. %Y-%m-%d %H:%M:%S
    
    timezone: str
        timezone of the date string e.g. 'America/New_York'

    Returns
    -------
    dict
        {'overall': dict, 'htg_season': dict, 'clg_season': dict}
    """
    mn_mx_dict = find_mn_mx_avg_col(df, 'Tsup(degC)')
    print_mn_mx_grd_loop(mn_mx_dict)
    # for heating season
    htg_pddts = datestr2pddt(htg_season, date_format, timezone)
    htg_df = df.loc[htg_pddts[0]:htg_pddts[1]]
    htg_mn_mx_dict = find_mn_mx_avg_col(htg_df, 'Tsup(degC)')
    print('Heating season')
    print_mn_mx_grd_loop(htg_mn_mx_dict)
    # for clg season 
    clg_pddts = datestr2pddt(clg_season, date_format, timezone)
    clg_df = df.loc[clg_pddts[0]:clg_pddts[1]]
    clg_mn_mx_dict = find_mn_mx_avg_col(clg_df, 'Tsup(degC)')
    print('Cooling season')
    print_mn_mx_grd_loop(clg_mn_mx_dict)
    return {'overall': mn_mx_dict, 'htg_season': htg_mn_mx_dict, 'clg_season': clg_mn_mx_dict}

def print_mn_mx_grd_loop(mn_mx_dict: dict):
    print('------------------------------------------------------------------------------------------------------------------------------------------------------------')
    mn = mn_mx_dict['min']
    mx = mn_mx_dict['max']
    avg = mn_mx_dict['avg']
    med = mn_mx_dict['med']
    print(f'Min Tsup (degF): {degc2degf(mn)}, Max Tsup (degF):{degc2degf(mx)}, Avg Tsup (degF): {degc2degf(avg)}, Med Tsup (degF): {degc2degf(med)}')
    print(f'Min Tsup (degC): {mn}, Max Tsup (degC):{mx}, Avg Tsup (degC): {avg}, Med Tsup (degC): {med}')
    print('------------------------------------------------------------------------------------------------------------------------------------------------------------')

def find_mn_mx_avg_col(df: pd.DataFrame, col_name: str) -> dict:
    """
    Find the max, min of a column.
    
    Parameters
    ----------
    df: pd.DataFrame
        dataframe to look through

    col_name: str
        name of the column

    Returns
    -------
    dict
        {'max': float, 'min': float, 'avg': float}
    """
    vals = df[col_name]
    mn = vals.min()
    mx = vals.max()
    avg = vals.mean()
    med = vals.median()
    return {'max': mx, 'min':mn, 'avg': avg, 'med': med}

def datestr2pddt(date_strs: list[str], date_format: str, timezone: str) -> pd.DatetimeIndex:
    """
    Find the max, min and average supply temperatures.
    
    Parameters
    ----------
    date_str: list[str]
        list of string of the date

    date_format: str
        format of the string, e.g. %Y-%m-%d %H:%M:%S

    timezone: str
        timezone of the date string e.g. 'America/New_York'

    Returns
    -------
    pd.DatetimeIndex
        pandas datetime objects
    """
    dts = []
    for date_str in date_strs:
        dt = datetime.datetime.strptime(date_str, date_format).replace(tzinfo=pytz.timezone(timezone))
        dts.append(dt)
    pddts = pd.to_datetime(dts)
    return pddts

def sepr_into_days(df:pd.DataFrame, start_yr: int, start_mth: int, start_day:int, end_yr: int, end_mth: int, end_day:int) -> list[pd.DataFrame]:
    """
    Separate dataframe into days.
 
    Parameters
    ----------
    df: pd.DataFrame
        panda dataframe.
    
    start_yr: int
        start yr
    
    start_mth: int
        start month

    start_day: int
        start day

    end_yr: int
        end yr
    
    end_mth: int
        end month

    end_day: int
        end day
    
    Returns
    -------
    list[pd.DataFrame]
        the separated list of data frames
    """
    pd_dts = gen_days(start_yr, start_mth, start_day, end_yr, end_mth, end_day)
    ndays = len(pd_dts)-1
    aday_dfs = []
    for i in range(ndays):
        if i != ndays - 1:
            pd_dt_start = pd_dts[i].tz_localize(pytz.timezone('America/New_York'))
            pd_dt_end = pd_dts[i+1].tz_localize(pytz.timezone('America/New_York'))
            aday_df = df.loc[pd_dt_start:pd_dt_end]
            aday_dfs.append(aday_df)
            
    return aday_dfs

def viz_temps(df:pd.DataFrame, cols2viz: list[str], color_ls: list[str], linestyle_ls: list[str], res_path: str, graph_title: str, 
              yaxis_lim: list[int | float] = None) -> None:
    """
    viz dataframe.
 
    Parameters
    ----------
    df: pd.DataFrame
        dataframe.
    
    cols2viz: list[str]
        the columns from the df to viz

    color_ls: list[str]
        the colors of each column from the df to viz

    linestyle_ls: list[str]
        the linestyle of each column from the df to viz, solid', 'dotted', 'dashed', 'dashdot'
    
    res_path: str
        file path

    graph_tile: str
        graph title

    yaxis_lim: list[int | float], optional
        limit of yaxis 1, default None
    
    """
    # process the datetime for visualization
    dts = df.index.to_pydatetime()
    dur_dt_dict = get_dur_naivedt(dts, orig_timezone_str='America/New_York')
    dts_nv = dur_dt_dict['dts_nv'] # this is use for visualization

    data_dict_ls1 = []
    for col_cnt, col in enumerate(cols2viz):
        valc = df[col]
        label =  col.split('(')[0].strip()
        valf = degc2degf(valc)
        data_d = {'datax':dts_nv, 'datay':valf, 'linestyle':linestyle_ls[col_cnt], 'linewidth': 1, 'marker':'', 'marker_size':2, 'color': color_ls[col_cnt], 'label': label}
        data_dict_ls1.append(data_d)

    xaxis_label = 'Time (H)'
    yaxis_label1 = 'Temp (degF(C))'
    dateformat = '%H'
    legend_loc = {'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.23), 'ncol':2}
    
    fig, ax1 = geomie3d.utility.viz1axis_timeseries(data_dict_ls1, graph_title, xaxis_label, yaxis_label1, yaxis_lim=yaxis_lim, 
                                                    dateformat=dateformat, legend_loc=legend_loc, tight_layout=False, viz=False, 
                                                    return_fig_ax=True)
    
    ytick_vals = ax1.get_yticks()
    new_ylabels = []
    for val in ytick_vals:
        val_degc = round(degf2degc(val),1)
        ylabel = f'{val}\n({val_degc})'
        new_ylabels.append(ylabel)

    ax1.set_yticks(ytick_vals)
    ax1.set_yticklabels(new_ylabels)
    fig.savefig(res_path, bbox_inches = "tight", dpi = 300, transparent=False)                                
    plt.close(fig) 

def viz_temps_others(df: pd.DataFrame, cols2viz: list[str], color_ls: list[str], linestyle_ls: list[str], 
                     cols2viz2: list[str], color_ls2: list[str], linestyle_ls2: list[str], 
                     res_path: str, graph_title: str, yaxis1_lim: list[int | float] = None, yaxis2_lim: list[int | float] = None):
    """
    viz dataframe on a 2 axis graph. cols2viz should be all temperatures variables, and cols2viz2 should be all the other variables.
 
    Parameters
    ----------
    df: pd.DataFrame
        chilled water dataframe.
    
    cols2viz: list[str]
        the columns from the df to viz

    color_ls: list[str]
        the colors of each column from the df to viz

    linestyle_ls: list[str]
        the linestyle of each column from the df to viz, solid', 'dotted', 'dashed', 'dashdot'
    
    cols2viz2: list[str]
        the columns from the df to viz

    color_ls2: list[str]
        the colors of each column from the df to viz

    linestyle_ls2: list[str]
        the linestyle of each column from the df to viz, solid', 'dotted', 'dashed', 'dashdot'

    res_path: str
        file path

    graph_tile: str
        graph title

    yaxis1_lim: list[int | float], optional
        limit of yaxis 1, default None
    
    yaxis2_lim: list[int | float], optional
        limit of yaxis 1, default None

    """       

    data_dict_ls1 = extract_cols(df, cols2viz, color_ls, linestyle_ls, True)
    data_dict_ls2 = extract_cols(df, cols2viz2, color_ls2, linestyle_ls2, False)
    
    xaxis_label = 'Time (H)'
    yaxis_label1 = 'Temp (degF(C))'
    yaxis_label2 = '%/(on/off)'
    dateformat = '%H'
    legend_loc = {'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.18), 'ncol':3}
    legend_loc2 = {'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.45), 'ncol':3}
    fig, ax1, ax2 = geomie3d.utility.viz2axis_timeseries(data_dict_ls1, data_dict_ls2, graph_title, xaxis_label, yaxis_label1, yaxis_label2, 
                                                         yaxis1_lim=yaxis1_lim, yaxis2_lim=yaxis2_lim, dateformat=dateformat, label_fontsize=14, 
                                                         tick_fontsize=12, legend_loc1=legend_loc, legend_loc2=legend_loc2, tight_layout=False, viz=False, 
                                                         return_fig_ax=True)
    
    ytick_vals = ax1.get_yticks()
    new_ylabels = []
    for val in ytick_vals:
        val_degc = round(degf2degc(val),1)
        ylabel = f'{val}\n({val_degc})'
        new_ylabels.append(ylabel)

    ax1.set_yticks(ytick_vals)
    ax1.set_yticklabels(new_ylabels)
    fig.savefig(res_path, bbox_inches = "tight", dpi = 300, transparent=False)
    plt.close(fig)

def viz_temps_others_seq(df: pd.DataFrame, cols2viz: list[str], color_ls: list[str], linestyle_ls: list[str], 
                         cols2viz2: list[str], color_ls2: list[str], linestyle_ls2: list[str], 
                         res_folder: str, graph_title: str, yaxis1_lim: list[int | float], yaxis2_lim: list[int | float]):
    """
    viz dataframe on a 2 axis graph. cols2viz should be all temperatures variables, and cols2viz2 should be all the other variables. 
    This function will produce multiple graph, each graph only with a single variable, this is helpful for presetnations when you need to show data sequentially
 
    Parameters
    ----------
    df: pd.DataFrame
        chilled water dataframe.
    
    cols2viz: list[str]
        the columns from the df to viz

    color_ls: list[str]
        the colors of each column from the df to viz

    linestyle_ls: list[str]
        the linestyle of each column from the df to viz, solid', 'dotted', 'dashed', 'dashdot'
    
    cols2viz2: list[str]
        the columns from the df to viz

    color_ls2: list[str]
        the colors of each column from the df to viz

    linestyle_ls2: list[str]
        the linestyle of each column from the df to viz, solid', 'dotted', 'dashed', 'dashdot'

    res_folder: str
        file path

    graph_tile: str
        graph title

    yaxis1_lim: list[int | float]
        limit of yaxis 1, [lwr, uppr]
    
    yaxis2_lim: list[int | float]
        limit of yaxis 1, [lwr, uppr]

    """       
    data_dict_ls1 = extract_cols(df, cols2viz, color_ls, linestyle_ls, True)
    data_dict_ls2 = extract_cols(df, cols2viz2, color_ls2, linestyle_ls2, False)
    
    xaxis_label = 'Time (H)'
    yaxis_label1 = 'Temp (degF(C))'
    yaxis_label2 = '%/(on/off)'
    dateformat = '%H'

    for cnt,data_dict1 in enumerate(data_dict_ls1):
        fig, ax1, ax2 = geomie3d.utility.viz2axis_timeseries([data_dict1], [], graph_title, xaxis_label, yaxis_label1, yaxis_label2, 
                                                                     yaxis1_lim=yaxis1_lim, yaxis2_lim=yaxis2_lim, dateformat=dateformat, label_fontsize=14, 
                                                                     tick_fontsize=12, tight_layout=False, viz=False, 
                                                                     return_fig_ax=True)
        ytick_vals = ax1.get_yticks()
        new_ylabels = []
        for val in ytick_vals:
            val_degc = round(degf2degc(val),1)
            ylabel = f'{val}\n({val_degc})'
            new_ylabels.append(ylabel)

        ax1.set_yticks(ytick_vals)
        ax1.set_yticklabels(new_ylabels)
        res_path = Path.joinpath(res_folder, f'{graph_title}_ax1_{cnt}')
        print(type(ax1))
        if cnt > 0:
            clean_axes(ax1, ax2)
            fig.savefig(res_path, bbox_inches = "tight", dpi = 300, transparent=True)
        else:
            fig.savefig(res_path, bbox_inches = "tight", dpi = 300, transparent=False)
        plt.close(fig)

    for cnt,data_dict2 in enumerate(data_dict_ls2):
        fig, ax1, ax2 = geomie3d.utility.viz2axis_timeseries([], [data_dict2], graph_title, xaxis_label, yaxis_label1, yaxis_label2, 
                                                             yaxis1_lim=yaxis1_lim, yaxis2_lim=yaxis2_lim, dateformat=dateformat, label_fontsize=14, 
                                                             tick_fontsize=12, tight_layout=False, viz=False, return_fig_ax=True)
        
        res_path = Path.joinpath(res_folder, f'{graph_title}_ax2_{cnt}')
        clean_axes(ax1, ax2)
        fig.savefig(res_path, bbox_inches = "tight", dpi = 300, transparent=True)
        plt.close(fig)
    
def clean_axes(ax1: matplotlib.axes.Axes, ax2: matplotlib.axes.Axes):
    '''
    clean the matplotlib axes of titles, ticks and labels
    Parameters
    ----------
    ax1: matplotlib.axes.Axes
        the matplotlib axes to clean
    
    ax2: matplotlib.axes.Axes
        the matplotlib axes to clean
    '''
    ax1.title.set_visible(False)
    ax1.set_xticks([])
    ax1.set_xticklabels([])
    ax1.set_xlabel("")
    ax1.set_yticks([])
    ax1.set_yticklabels([])
    ax1.set_ylabel("")
    ax2.set_yticks([])
    ax2.set_yticklabels([])
    ax2.set_ylabel("")

def extract_cols(df: pd.DataFrame, cols2viz: list[str], color_ls: list[str], linestyle_ls: list[str], is_temp: bool, timezone_str: str = 'America/New_York'):
    """
    Separate dataframe into days.
    
    Parameters
    ----------
    df: pd.DataFrame
        chilled water dataframe.
    
    cols2viz: list[str]
        the columns from the df to viz

    color_ls: list[str]
        the colors of each column from the df to viz

    linestyle_ls: list[str]
        the linestyle of each column from the df to viz, solid', 'dotted', 'dashed', 'dashdot'
    
    is_temp: bool
        true or false the data to viz are temperatures
    
    Returns
    -------
    list[dict]
        the data ready for plotting
    """
    # process the datetime for visualization
    dts = df.index.to_pydatetime()
    dur_dt_dict = get_dur_naivedt(dts, orig_timezone_str=timezone_str)
    dts_nv = dur_dt_dict['dts_nv'] # this is use for visualization
    data_dict_ls = []
    for col_cnt, col in enumerate(cols2viz):
        val = df[col]
        label =  col.split('(')[0].strip()
        if is_temp:
            valf = degc2degf(val)
            data_d = {'datax':dts_nv, 'datay':valf, 'linestyle':linestyle_ls[col_cnt], 'linewidth': 1, 'marker':'', 'marker_size':2, 
                        'color': color_ls[col_cnt], 'label': label}
        else:
            data_d = {'datax':dts_nv, 'datay':val, 'linestyle':linestyle_ls[col_cnt], 'linewidth': 1, 'marker':'', 'marker_size':2, 
                        'color': color_ls[col_cnt], 'label': label}
        data_dict_ls.append(data_d)
    return data_dict_ls

def degc2degf(degc: float | int | pd.DataFrame) -> int | float | pd.DataFrame:
    degf = degc*9/5+32
    return degf

def degf2degc(degf: float | int | pd.DataFrame) -> int | float | pd.DataFrame:
    degc = (degf-32)/1.8
    return degc

def gpm2lpm(gpm: float | int | pd.DataFrame) -> int | float | pd.DataFrame:
    lpm = gpm * 3.785412
    return lpm

def joules2btu(joules: float | int | pd.DataFrame) -> int | float | pd.DataFrame:
    btu = joules * 0.00094781712
    return btu

def btu2joules(btu: float | int | pd.DataFrame) -> int | float | pd.DataFrame:
    joules = btu/0.00094781712
    return joules 

def watts2btuh(watts: float | int | pd.DataFrame) -> float | int | pd.DataFrame:
    btuh = watts * 3.412142
    return btuh

def btuh2watts(btuh: float | int | pd.DataFrame) -> float | int | pd.DataFrame:
    watts = btuh/3.412142
    return watts

def cfm2cmm(cfm: float | int | pd.DataFrame) -> float | int | pd.DataFrame:
    cmm = cfm * 0.0283168466
    return cmm

def cmm2cfm(cmm: float | int | pd.DataFrame) -> float | int | pd.DataFrame:
    cfm = cmm/0.0283168466
    return cfm

def ton2btuh(ton: float | int | pd.DataFrame) -> float | int | pd.DataFrame:
    btuh = ton*12000
    return btuh