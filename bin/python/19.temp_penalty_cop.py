import math
from pathlib import Path

import matplotlib.pyplot as plt
import lewisctr_utils
#==========================================================================================================================================================
# region: Parameters
#==========================================================================================================================================================
net_heat_j = 5385654539010.424 #J
heat_rej = 6.315284 # 1000,000 MJ
clg_delivered = 4.849593 # 1000,000 MJ
heat_ext = .929632 # 1000,000 MJ
htg_delivered = 1.926893 # 1000,000 MJ

chw_temp_target_k = 8.4+273.15
hw_temp_target_k = 50.4+273.15

sbore = 20 #ft
borefield_area = 3971.24 #m2
borefield_perimeter = 441.378 #m
abore_depth = 500 #ft
ttl_bores = 140
n_4 = 74
n_3 = 43
n_2 = 21
n_1 = 2
# thermal conductivity test
measured_conductivity = 4.11 # btu/hr.ft.degF
recommended_conductity = 1.75 # btu/hr.ft.degF
measured_diffusivity = 2.85 #ft2/day
recommended_diffusivity = 1.21 #ft2/day
undisturbed_temp = 57.4 #degF (report 57-57.8degF)

base_path = Path(__file__).parent.parent.parent
img_path = Path.joinpath(base_path, 'img')
res_folder = Path.joinpath(img_path, f'ground_heat_up')
if not res_folder.exists():
    Path.mkdir(res_folder)
#==========================================================================================================================================================
# endregion: Parameters
#==========================================================================================================================================================
#==========================================================================================================================================================
# region: Functions
#==========================================================================================================================================================
def calc_ix(dist_from_borehole_center: float, thermal_diffusivity: float, ndays: int) -> float:
    """
    calculate the I(X) value for calculating the temperature difference from the neutral temperature a distance from the center of the borehole .
    
    Parameters
    ----------
    dist_from_borehole_center: float
        the distance from the center of the borehole.

    thermal_diffusivity: float
        thermal diffusivitiy of the borefield SI = m2/day IP = ft2/day
    
    ndays: int
        the duration of the penalty.
    
    Returns
    -------
    float
        the I(X) value. 
    """
    denominator = math.sqrt(thermal_diffusivity*ndays) * 2
    x = dist_from_borehole_center/denominator
    ix = -0.969*math.log(x)-0.186
    return ix

def calc_temp_diff_from_center(avg_annual_heat_pulse: float, thermal_conductivity: float, ttl_borehole_depth: float, dist_from_borehole_center: float, thermal_diffusivity: float, ndays: int) -> float:
    """
    calculate the temperature difference from the neutral temperature a distance from the center of the borehole .
    
    Parameters
    ----------
    avg_annual_heat_pulse: float
        the average annual heat 0.55555556rejected or extracted from the borefield SI = watts IP = Btuh
    
    thermal_conductivity: float
        thermal conductivity of the borefield SI = W/mK IP = Btu/h.ft.defF

    ttl_borehole_depth: float
        total borehole depth SI = m IP = ft

    dist_from_borehole_center: float
        the distance from the center of the borehole.

    thermal_diffusivity: float
        thermal diffusivitiy of the borefield SI = m2/day IP = ft2/day
    
    ndays: int
        the duration of the heat pulse.
    
    Returns
    -------
    float
        the difference in temperature from the neutral temperature. 
    """
    ix = calc_ix(dist_from_borehole_center, thermal_diffusivity, ndays)
    tdiff = (avg_annual_heat_pulse*ix)/(2*math.pi*thermal_conductivity*ttl_borehole_depth)   
    return tdiff

def calc_pcp(thermal_conductivity: float, thermal_diffusivity: float, si_unit: bool = True) -> float:
    """
    calculate the density * specific heat using thermal conductivity and thermal diffusivity
    
    Parameters
    ----------
    thermal_conductivity: float
        thermal conductivity of the borefield SI = W/mK IP = Btu/h.ft.defF

    thermal_diffusivity: float
        thermal diffusivitiy of the borefield SI = m2/day IP = ft2/day
    
    si_unit: bool, optional
        if True means all the units is in SI, if False units in IP.
    
    Returns
    -------
    float
        the pcp that can be use in qstored_a_hollow_cylinder and calc_tp1_grid
    """
    if si_unit == True:
        pcp = thermal_conductivity/thermal_diffusivity*24*3600
    else:
        pcp = thermal_conductivity/thermal_diffusivity*24
    return pcp

def qstored_a_hollow_cylinder(thermal_conductivity: float, thermal_diffusivity: float, ttl_borehole_depth: float, radius_outer: float, radius_inner: float, temp_diff: float, si_unit: bool = True) -> float:
    """
    calculate the amount of energy stored in a hollow cylinder
    
    Parameters
    ----------
    thermal_conductivity: float
        thermal conductivity of the borefield SI = W/mK IP = Btu/h.ft.defF

    thermal_diffusivity: float
        thermal diffusivitiy of the borefield SI = m2/day IP = ft2/day

    ttl_borehole_depth: float
        total borehole depth SI = m IP = ft

    radius_outer: float
        the outer radius of the hollow cylinder.

    radius_inner: float
        the inner radius of the hollow cylinder.

    temp_diff: float
        the difference in temperature from the neutral temperature. Calculated from the function calc_temp_diff_from_center
    
    si_unit: bool, optional
        if True means all the units is in SI, if False units in IP.
    
    Returns
    -------
    float
        the heat stored in the hollow cylinder. SI = Joules IP = Btu 
    """
    pcp = calc_pcp(thermal_conductivity, thermal_diffusivity, si_unit=si_unit)
    q = pcp*math.pi*ttl_borehole_depth*((radius_outer**2)-(radius_inner**2))*temp_diff
    return q

def calc_tp1_grid(ttl_q: float, thermal_conductivity: float, thermal_diffusivity: float, ttl_borehole_depth: float, sbore: float, si_unit: bool = True) -> float:
    """
    calculate the temperature penalty of a borehole that is surrounded by 4 other boreholes in a grid formation. 
    
    Parameters
    ----------
    ttl_q: float
        heat stored or extracted from the borefield, calculated from calc_ttl_q_stored SI = Joules IP = Btu 
    
    thermal_conductivity: float
        thermal conductivity of the borefield SI = W/mK IP = Btu/h.ft.defF

    thermal_diffusivity: float
        thermal diffusivitiy of the borefield SI = m2/day IP = ft2/day

    ttl_borehole_depth: float
        total borehole depth SI = m IP = ft

    sbore: float
        spacing of boreholes.

    si_unit: bool, optional
        if True means all the units is in SI, if False units in IP.
    
    Returns
    -------
    float
        the temperature penalty if all boreholes are surrounded by 4 other boreholes in a grid.
    """
    pcp = calc_pcp(thermal_conductivity, thermal_diffusivity, si_unit=si_unit)
    tp1 = ttl_q/(pcp*(sbore**2)*ttl_borehole_depth)
    return tp1

def calc_cfhoriz(area_borefield: float, a_borehole_depth: float, perimeter_borefield: float) -> float:
    """
    calculate the bottom diffusion factor used in calculating the corrected temperature penalty. 
    
    Parameters
    ----------
    area_borefield: float
        area of the borefield 
    
    a_borehole_depth: float
        total borehole depth SI = m IP = ft

    perimeter_borefield: float
        perimeter of the borefield

    Returns
    -------
    float
        the bottom diffusion factor.
    """
    cfhoriz = 1 + (area_borefield/(a_borehole_depth*perimeter_borefield))
    return cfhoriz

def calc_tp(tp1: float, n_4: int, n_3: int, n_2: int, n_1: int, cfhoriz: float) -> float:
    """
    calculate the temperature penalty of a borefield. 
    
    Parameters
    ----------
    tp1: float
        the temperature penalty of a borehole that is surrounded by 4 other boreholes in a grid formation 
    
    n_4: int
        number of borehole surrounded by 4 other boreholes

    n_3: int
        number of borehole surrounded by 3 other boreholes

    n_2: int
        number of borehole surrounded by 2 other boreholes

    n_1: int
        number of borehole surrounded by 1 other boreholes

    cfhoriz: float
        bottom diffusion factor. Calculated from calc_cfhoriz
    
    Returns
    -------
    float
        the temperature penalty.
    """
    ttl_boreholes = n_4 + n_3 + n_2 + n_1
    tp = ((n_4 + (0.75*n_3) + (0.5*n_2) + (0.25*n_1))/(ttl_boreholes*cfhoriz)) * tp1
    return tp

def calc_ttl_q_stored(ttl_q: float, thermal_conductivity: float, thermal_diffusivity: float, ttl_borehole_depth: float, ndays: float, sbore: float, si_unit: bool = True) -> dict:
    """
    find the distance where the temperature increase becomes neglible < 0.5 degF (< 0.3 degC) and calculate the total heat stored/extracted from borefield.
    
    Parameters
    ----------
    ttl_q: float
        heat rejected or extracted from the borefield SI = Joules IP = Btu 
    
    thermal_conductivity: float
        thermal conductivity of the borefield SI = W/mK IP = Btu/h.ft.defF

    thermal_diffusivity: float
        thermal diffusivitiy of the borefield SI = m2/day IP = ft2/day

    ttl_borehole_depth: float
        total borehole depth SI = m IP = ft

    ndays: int
        the duration of the heat pulse.

    sbore: float
        spacing of boreholes.

    si_unit: bool, optional
        if True means all the units is in SI, if False units in IP.
    
    Returns
    -------
    dict
        - distance : [value of temp diff, q_stored]
    """
    res_d = {}
    tdiff = float('inf')
    if si_unit == True:
        tdiff_threshold = 0.3
        dist_incre = 1.5
    else:
        tdiff_threshold = 0.5
        dist_incre = 5

    rad_store = sbore/2
    mid_incre_dist = dist_incre/2
    dist = rad_store + mid_incre_dist # the mid point of the radiating hollow cylinder 
    while tdiff >= tdiff_threshold:
        tdiff = calc_temp_diff_from_center(ttl_q, thermal_conductivity, ttl_borehole_depth, dist, thermal_diffusivity, ndays)
        r_out = dist+mid_incre_dist
        r_in = dist-mid_incre_dist
        q_stored = qstored_a_hollow_cylinder(thermal_conductivity, thermal_diffusivity, ttl_borehole_depth, r_out, r_in, tdiff, si_unit=si_unit)
        res_d[dist] = [tdiff, q_stored]
        dist+=dist_incre

    return res_d

def calc_clg_cop(heat_rej, clg_delivered):
    qrat = heat_rej/clg_delivered
    cop = 1/(qrat-1)
    return cop

def calc_clg_cop_carnot(tc, th):
    """
    calculate carnot cooling cop, temps need to be in kelvin.
    """
    cop = tc/(th-tc)
    return cop

def calc_htg_cop(heat_ext, htg_delivered):
    qrat = heat_ext/htg_delivered
    cop = 1/((qrat*-1) + 1)
    return cop

def calc_htg_cop_carnot(tc, th):
    """
    calculate carnot heating cop, temps need to be in kelvin.
    """
    cop = th/(th-tc)
    return cop

def setup_graph_sgl_axis(xaxis_label: str, yaxis_label: str, graph_title: str) -> tuple:
    """
    setup the single axis matplotlib graph 
    
    Parameters
    ----------
    xaxis_label: str
        label of x-axis

    yaxis_label: str
        label of y-axis

    graph_title: str
        label of y-axis
    
    Returns
    -------
    tuple
        tuple containing the (fig, ax1)
    """
    fig, ax1 = plt.subplots()
    fsize = 16
    ax1.set_xlabel(xaxis_label, fontsize=fsize)
    ax1.set_ylabel(yaxis_label, color='k', fontsize=fsize)

    ax1.tick_params(axis='x', labelsize=fsize) 
    ax1.tick_params(axis='y', labelsize=fsize)
    
    ax1.grid(True, axis = 'y', linestyle='--', linewidth = 0.3)
    ax1.grid(True, axis = 'x', linestyle='--', linewidth = 0.3)

    plt.tight_layout() 
    ax1.set_title(graph_title, fontsize=16)
    return fig, ax1

def viz_all_lines_sgl_axis(x_datas: list[list[float|int]], y_datas:list[list[float|int]], graph_props: list[dict], legend_loc: dict, xaxis_label: str, 
                           yaxis_label: str, graph_title: str) -> tuple:
    """
    visualize the data as a graph with two axes
    
    Parameters
    ----------
    x_datas: list[list[float|int]]
        shape[n_dataset, n_data_points], x-axis data that corresponds to the data in y_datas

    y_datas: list[list[float|int]]
        shape[n_dataset, n_data_points], y-axis data that corresponds to the data in x_datas

    graph_props: list[dict]
        - list of dictionary specifying the style of the dataset in y_datas1
        - color: str b, k, r, g, marker: str e.g. ^, o, +, linestyle: str e.g. solid, dashed, label: str

    legend_loc: dict
        - description of the legend placement for dataset in y_datas1
        - loc, bbox_to_anchor, ncol
    
    xaxis_label: str
        label of x-axis

    yaxis_label: str
        label of y-axis1

    graph_title: str
        label of y-axis

    Returns
    -------
    tuple
        tuple containing the (fig, ax1)
    """
    fig, ax1= setup_graph_sgl_axis(xaxis_label, yaxis_label, graph_title)

    for cnt, y_data in enumerate(y_datas):
        x_data = x_datas[cnt]
        ax1.plot(x_data, y_data, color=graph_props[cnt]['color'], marker= graph_props[cnt]['marker'], label=graph_props[cnt]['label'], 
                 linestyle=graph_props[cnt]['linestyle'], markersize=8)

    ax1.legend(loc=legend_loc['loc'], bbox_to_anchor=legend_loc['bbox_to_anchor'],
            fancybox=True, ncol=legend_loc['ncol'], fontsize = 14)

    return fig, ax1                             
    
def setup_graph_dbl_axis(xaxis_label: str, yaxis_label1: str, yaxis_label2: str, graph_title: str) -> tuple:
    """
    setup the double axis matplotlib graph 
    
    Parameters
    ----------
    xaxis_label: str
        label of x-axis

    yaxis_label1: str
        label of y-axis1

    yaxis_label2: str
            label of y-axis2

    graph_title: str
        label of y-axis
 
    Returns
    -------
    tuple
        tuple containing the (fig, ax1, ax2)
    """
    fig, ax1 = plt.subplots()
    fsize = 14
    ax1.set_xlabel(xaxis_label, fontsize=fsize)
    ax1.set_ylabel(yaxis_label1, color='k', fontsize=fsize)
    ax2 = ax1.twinx() 
    ax2.set_ylabel(yaxis_label2, color='k', fontsize=fsize)
    ax1.tick_params(axis='x', labelsize=fsize) 
    ax1.tick_params(axis='y', labelsize=fsize)
    ax2.tick_params(axis='y', labelsize=fsize)

    ax1.grid(True, axis = 'y', linestyle='--', linewidth = 0.3)
    ax1.grid(True, axis = 'x', linestyle='--', linewidth = 0.3)

    plt.tight_layout() 
    ax1.set_title(graph_title, fontsize=16)
    return fig, ax1, ax2

def viz_all_lines_dbl_axis(x_datas1: list[list[float|int]], x_datas2: list[list[float|int]], y_datas1: list[list[float|int]], 
                           y_datas2: list[list[float|int]], graph_props1: list[dict], graph_props2: list[dict], legend_loc1 : dict, 
                           legend_loc2: dict, xaxis_label: str, yaxis_label1: str, yaxis_label2: str, graph_title: str) -> tuple:
    """
    visualize the data as a graph with two axes
    
    Parameters
    ----------
    x_datas1: list[list[float|int]]
        shape[n_dataset, n_data_points], x-axis data that corresponds to the data in y_datas1

    x_datas2: list[list[float|int]]
        shape[n_dataset, n_data_points], x-axis data that corresponds to the data in y_datas2

    y_datas1: list[list[float|int]]
        shape[n_dataset, n_data_points], y-axis data that corresponds to the data in x_datas1

    y_datas2: list[list[float|int]]
        shape[n_dataset, n_data_points], y-axis data that corresponds to the data in x_datas2

    graph_props1: list[dict]
        - list of dictionary specifying the style of the dataset in y_datas1
        - color: str b, k, r, g, marker: str e.g. ^, o, +, linestyle: str e.g. solid, dashed, label: str

    graph_props2: list[dict]
        - list of dictionary specifying the style of the dataset in y_datas2
        - color: str b, k, r, g, marker: str e.g. ^, o, +, linestyle: str e.g. solid, dashed, label: str

    legend_loc1 : dict
        - description of the legend placement for dataset in y_datas1
        - loc, bbox_to_anchor, ncol
    
    legend_loc2 : dict
        - description of the legend placement for dataset in y_datas2
        - loc, bbox_to_anchor, ncol

    xaxis_label: str
        label of x-axis

    yaxis_label1: str
        label of y-axis1

    yaxis_label2: str
            label of y-axis2

    graph_title: str
        label of y-axis
    
    Returns
    -------
    tuple
        tuple containing the (fig, ax1, ax2)
    """
    fig, ax1, ax2 = setup_graph_dbl_axis(xaxis_label, yaxis_label1, yaxis_label2, graph_title)
    for cnt, y1_data in enumerate(y_datas1):
        x_data1 = x_datas1[cnt]
        ax1.plot(x_data1, y1_data, color=graph_props1[cnt]['color'], marker= graph_props1[cnt]['marker'], label=graph_props1[cnt]['label'], 
                 linestyle=graph_props1[cnt]['linestyle'], markersize=8)

    for cnt, y2_data in enumerate(y_datas2):
        x_data2 = x_datas2[cnt]
        ax2.plot(x_data2, y2_data, color=graph_props2[cnt]['color'], marker= graph_props2[cnt]['marker'], label=graph_props2[cnt]['label'], 
                 linestyle=graph_props2[cnt]['linestyle'], markersize=8)
        
    ax1.legend(loc=legend_loc1['loc'], bbox_to_anchor=legend_loc1['bbox_to_anchor'],
               fancybox=True, ncol=legend_loc1['ncol'], fontsize = 14)

    ax2.legend(loc=legend_loc2['loc'], bbox_to_anchor=legend_loc2['bbox_to_anchor'],
               fancybox=True, ncol=legend_loc2['ncol'], fontsize = 14)

    return fig, ax1, ax2
    # fig.savefig(res_path, bbox_inches = "tight", dpi = 300, transparent=False)
    # plt.show()
    # plt.close(fig)

#==========================================================================================================================================================
# endregion: Functions
#==========================================================================================================================================================
#==========================================================================================================================================================
# region: Main
#==========================================================================================================================================================
# -------------------------------------------------------------------------------------------------------------
# region: calculate temperature penalty
# -------------------------------------------------------------------------------------------------------------
# convert all units to IP it is more convenient
net_heat_w = net_heat_j/(8670*3600)
net_heat_btuh = lewisctr_utils.watts2btuh(net_heat_w)
borefield_area_ft = lewisctr_utils.m2_day_to_ft2_day(borefield_area)
borefield_perimeter_ft = lewisctr_utils.meter2ft(borefield_perimeter)
print(borefield_area_ft, borefield_perimeter_ft)
ttl_boredepth = 500 * 140

cfhoriz = calc_cfhoriz(borefield_area_ft, abore_depth, borefield_perimeter_ft)
years = [10, 15, 20, 25, 30, 35, 40]
year_dates = [2017]
tps = [57.4]
for year in years:
    ndays = year*365+30 # the duration of the heat pulse in days
    year_date = year + 2017
    year_dates.append(year_date)
    # calc the temperature difference from neutral temp with distance from center of borehole
    dis_d = calc_ttl_q_stored(net_heat_btuh, recommended_conductity, recommended_diffusivity, ttl_boredepth, ndays, sbore, si_unit=False)
    q_stored_ls = []
    for val in dis_d.values():
        q_stored = val[1]
        q_stored_ls.append(q_stored)

    ttl_q_stored = sum(q_stored_ls)
    tp1 = calc_tp1_grid(ttl_q_stored, recommended_conductity, recommended_diffusivity, ttl_boredepth, sbore, si_unit=False)
    tp = calc_tp(tp1, n_4, n_3, n_2, n_1, cfhoriz)
    avg_grd_temp = tp + undisturbed_temp
    print(f'At the {year} year the supply water temp will be {avg_grd_temp}')
    tps.append(avg_grd_temp)

actual_temps = [57.4, 75, 75.5]
actual_years = [2017, 2025, 2026]
# -------------------------------------------------------------------------------------------------------------
# endregion: calculate temperature penalty
# -------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------
# region: calculate COP changes and HVAC energy consumption
# -------------------------------------------------------------------------------------------------------------
clg_cop = calc_clg_cop(heat_rej, clg_delivered)
print(f'Clg COP = {round(clg_cop,1)}')
htg_cop = calc_htg_cop(heat_ext, htg_delivered)
print(f'htg COP = {round(htg_cop,1)}')

carnot_clg_cop = calc_clg_cop_carnot(chw_temp_target_k, 24+273.15)
real_clg_htp_eff =  clg_cop / carnot_clg_cop 
print(f'The carnot clg cop is {round(carnot_clg_cop,1)} and the g coefficient is {round(real_clg_htp_eff,2)}')

carnot_htg_cop = calc_htg_cop_carnot(24+273.15, hw_temp_target_k)
real_htg_htp_eff =  htg_cop / carnot_htg_cop 
print(f'The carnot htg cop is {round(carnot_htg_cop,1)} and the g coefficient is {round(real_htg_htp_eff,2)}')

proj_clg_cops = []
proj_htg_cops = []
htg_years = []
clg_years = []
clg_enrgs = []
htg_enrgs = []
ttl_engys = []
prev_engy = None
for tcnt, tp in enumerate(tps):
    tp_c = lewisctr_utils.degf2degc(tp)
    a_carnot_clg_cop = calc_clg_cop_carnot(chw_temp_target_k, tp_c+273.15)
    a_carnot_htg_cop = calc_htg_cop_carnot(tp_c+273.15, hw_temp_target_k)
    a_clg_cop = a_carnot_clg_cop*real_clg_htp_eff
    a_htg_cop = a_carnot_htg_cop*real_htg_htp_eff
    clg_enrg = clg_delivered/a_clg_cop
    htg_enrg = htg_delivered/a_htg_cop
    
    if htg_enrg > 0:
        ttl_engy = clg_enrg + htg_enrg
    else:
        ttl_engy = clg_enrg

    ayear = year_dates[tcnt]
    if prev_engy != None:
        engy_diff = ttl_engy - prev_engy
        engy_diff_ptg = engy_diff/prev_engy * 100
        # print(f'the prev engy is {prev_engy} the current ttl engy is {ttl_engy}')
        print(f'the increase in HVAC energy is {round(engy_diff_ptg)}% in year {ayear}')

    if ayear != 2017:
        ttl_engys.append(ttl_engy)
        clg_years.append(ayear)
        proj_clg_cops.append(a_clg_cop)
        clg_enrgs.append(clg_enrg)
        if tp_c <= 50:
            htg_years.append(ayear)
            proj_htg_cops.append(a_htg_cop)
            htg_enrgs.append(htg_enrg)

    prev_engy = ttl_engy
    # print(f'{ayear}: projected COP clg {round(a_clg_cop,1)}, COP htg {round(a_htg_cop,1)}, grd water supply: {round(tp)} degF, ({round(tp_c)} degC)')
    # print(f'{ayear}: projected clg energy {round(clg_enrg,1)} Million MJ, htg energy {round(htg_enrg,1)} Million MJ, grd water supply: {round(tp)} degF, ({round(tp_c)} degC)')

clg_consumed_measured = clg_delivered/clg_cop 
htg_consumed_measured = htg_delivered/htg_cop
ttl_consumed_measured = clg_consumed_measured + htg_consumed_measured
# -------------------------------------------------------------------------------------------------------------
# endregion: calculate COP changes and HVAC energy consumption
# -------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------------------------------
# region:Viz ground temperature penalty and cop
# ---------------------------------------------------------------------------------------------------------------------------------------------------
res_path = Path.joinpath(res_folder, f'perm_heatup.svg')
xaxis_label = 'Year'
yaxis_label1 = 'Penalized Ground Temp (degF (degC))'
yaxis_label2 = 'COP'
legend_loc1 = {'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.2), 'ncol':2}
legend_loc2 = {'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.3), 'ncol':2}
graph_title = 'Penalized Ground Loop Temperature VS COP'

graph_props1 = [{'color': 'k', 'marker': 'o', 'linestyle':'solid', 'label': 'Grd Supply Temp Projected'},
               {'color': 'k', 'marker': 'x', 'linestyle':'solid', 'label': 'Grd Supply Temp Measured'}]

graph_props2 = [{'color': 'b', 'marker': 'o', 'linestyle':'dashed', 'label': 'clg COP Projected'},
               {'color': 'r', 'marker': 'o', 'linestyle':'dashed', 'label': 'htg COP Projected'},
               {'color': 'b', 'marker': 'x', 'linestyle':'dashed', 'label': 'clg COP Measured'},
               {'color': 'r', 'marker': 'x', 'linestyle':'dashed', 'label': 'htg COP Measured'}]

fig, ax1, ax2 = viz_all_lines_dbl_axis([year_dates,actual_years], [clg_years, htg_years, [2026], [2026]], [tps, actual_temps], 
                                       [proj_clg_cops, proj_htg_cops, [clg_cop], [htg_cop]], graph_props1, graph_props2, legend_loc1, legend_loc2, 
                                       xaxis_label, yaxis_label1, yaxis_label2, graph_title)

ytick_vals = tps
new_ylabels = []
for val in ytick_vals:
    val_degc = round(lewisctr_utils.degf2degc(val),1)
    ylabel = f'{round(val, 1)}\n({val_degc})'
    new_ylabels.append(ylabel)

ax1.set_yticks(ytick_vals)
ax1.set_yticklabels(new_ylabels)
ax1.tick_params(axis='y', labelsize=10)
ax2.set_ylim(1, 5)
ax1.set_xticks(year_dates)
ax1.set_xticklabels(year_dates)
for label in ax1.get_xticklabels():
    label.set_rotation(45)

fig.savefig(res_path, bbox_inches = "tight", dpi = 300, transparent=False)
# plt.show()
plt.close(fig)
# ---------------------------------------------------------------------------------------------------------------------------------------------------
# endregion: Viz ground temperature penalty and cop
# ---------------------------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------------------------------
# region: Viz HVAC energy consumption
# ---------------------------------------------------------------------------------------------------------------------------------------------------
res_path = Path.joinpath(res_folder, f'htg_clg_engy.svg')
xaxis_label = 'Year'
yaxis_label = 'HVAC Energy (x1000,000 MJ (kWh))'
legend_loc = {'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.23), 'ncol':2}
graph_title = ' HVAC Energy Consumption'

graph_props2 = [{'color': 'b', 'marker': '^', 'linestyle':'dashed', 'label': 'clg engy Projected'},
               {'color': 'r', 'marker': '^', 'linestyle':'dashed', 'label': 'htg engy Projected'},
               {'color': 'b', 'marker': '+', 'linestyle':'dashed', 'label': 'clg engy Measured'},
               {'color': 'r', 'marker': '+', 'linestyle':'dashed', 'label': 'htg engy Measured'},
               {'color': 'g', 'marker': '^', 'linestyle':'dashed', 'label': 'ttl engy Projected'},
               {'color': 'g', 'marker': '+', 'linestyle':'dashed', 'label': 'ttl engy Measured'}]

fig, ax1 = viz_all_lines_sgl_axis([clg_years, htg_years, [2026], [2026], clg_years, [2026]], 
                                  [clg_enrgs, htg_enrgs, [clg_delivered/clg_cop], [htg_delivered/htg_cop], ttl_engys, [ttl_consumed_measured]], 
                                  graph_props2, legend_loc, xaxis_label, yaxis_label, graph_title)

ytick_vals = ax1.get_yticks()
new_ylabels = []
for val in ytick_vals:
    val_kwh = round(lewisctr_utils.mjoules2kwh(val),1)
    ylabel = f'{val}\n({val_kwh})'
    new_ylabels.append(ylabel)

ax1.set_yticks(ytick_vals)
ax1.set_yticklabels(new_ylabels)
ax1.set_ylim(0,5)

ax1.set_xticks(year_dates)
ax1.set_xticklabels(year_dates)
for label in ax1.get_xticklabels():
    label.set_rotation(45)
        
fig.savefig(res_path, bbox_inches = "tight", dpi = 300, transparent=False)
# plt.show()
plt.close(fig)
# ---------------------------------------------------------------------------------------------------------------------------------------------------
# endregion: Viz HVAC energy consumption
# ---------------------------------------------------------------------------------------------------------------------------------------------------
#==========================================================================================================================================================
# endregion: Main
#==========================================================================================================================================================