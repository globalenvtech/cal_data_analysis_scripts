from pathlib import Path

import pandas as pd
import numpy as np
import datetime

import lewisctr_utils
#==========================================================================================================================================================
# region: Parameters
#==========================================================================================================================================================
base_path = Path(__file__).parent.parent.parent
data_path = Path.joinpath(base_path, 'data')
folder_name = '2025_2026_may'
grd_temps_path = Path.joinpath(data_path, f'ground_loop/{folder_name}/grd_loop_overall.csv')
vol_flw_path = Path.joinpath(data_path, f'ground_loop/{folder_name}/GWS FlowCSV/GWS Flow.csv')
res_path = Path.joinpath(data_path, f'ground_loop/{folder_name}/grd_loop_enrg.csv')
# endregion: Parameters
#==========================================================================================================================================================
# region: Functions
#==========================================================================================================================================================
def replace_dt_yr(dts: list[datetime.datetime], new_year: int) -> list[datetime.datetime]:
    new_dts = []
    for dt in dts:
        new_dt = dt.replace(year=new_year)
        new_dts.append(new_dt)
    return new_dts

# endregion: Functions
#==========================================================================================================================================================
# region: Main
#==========================================================================================================================================================
#----------------------------------------------------------------------------------------------------------
vol_flw_df = lewisctr_utils.read_clean_resample_csv(vol_flw_path)
vol_flw_df['Value'] = lewisctr_utils.gpm2lpm(vol_flw_df['Value']) # convert gallons per min to liter per min
vol_flw_df.rename(columns={'Value': 'VolumeFlow(lpm)'}, inplace=True)
#----------------------------------------------------------------------------------------------------------
df_grd_temps = pd.read_csv(grd_temps_path)
df_grd_temps['Date'] = pd.to_datetime(df_grd_temps['Date'], yearfirst=True)
df_grd_temps.set_index('Date', inplace=True)
#----------------------------------------------------------------------------------------------------------
df_overall = pd.concat([vol_flw_df, df_grd_temps], axis = 1)
df_overall.dropna(inplace=True)
#----------------------------------------------------------------------------------------------------------
# calculate heating and cooling load using mct
#----------------------------------------------------------------------------------------------------------
# look at the thermal energy from the geothermal source
water_mass = df_overall['VolumeFlow(lpm)']
dur = df_overall['Duration']
water_mass = np.where(dur <= 10, water_mass * dur, water_mass)
tdiff = df_overall['Tsup(degC)'] - df_overall['Tret(degC)']
engy_j = (water_mass * 4184 * tdiff) # joules
engy_btu = lewisctr_utils.joules2btu(engy_j)
df_overall['Tsup-Tret(degC)'] = tdiff
df_overall['Energy(J)'] = engy_j
df_overall.to_csv(res_path)

ttl_engy_j = engy_j.sum()
ttl_engy_btu = lewisctr_utils.joules2btu(ttl_engy_j)
print(f"Net energy into the borefields {ttl_engy_btu/1000} kBTU ({ttl_engy_j/1000000} MJ)")

htg_engy_j = engy_j[engy_j > 0]
ttl_htg_engy_j = htg_engy_j.sum()
ttl_htg_engy_btu = lewisctr_utils.joules2btu(ttl_htg_engy_j)
print(f"Total energy extracted from the borefields {ttl_htg_engy_btu/1000} kBtu ({ttl_htg_engy_j/1000000} MJ)")

clg_engy_j = engy_j[engy_j < 0]
ttl_clg_engy_j = clg_engy_j.sum()
ttl_clg_engy_btu = lewisctr_utils.joules2btu(ttl_clg_engy_j)
print(f"Total energy rejected into the borefields {ttl_clg_engy_btu/1000} kBtu ({ttl_clg_engy_j/1000000} MJ)")

zero_engy_j = engy_j[engy_j == 0]

htg_ld_watts = htg_engy_j/600
clg_ld_watts = clg_engy_j/600
htg_ld_kwatts = htg_ld_watts/1000
clg_ld_kwatts = clg_ld_watts/1000
clg_ld_kwatts_mx = clg_ld_kwatts.min()

htg_ld_btuh = lewisctr_utils.watts2btuh(htg_ld_watts)
clg_ld_btuh = lewisctr_utils.watts2btuh(clg_ld_watts)
htg_ld_mbh = htg_ld_btuh/1000
clg_ld_mbh = clg_ld_btuh/1000
clg_ld_mbh_mx = clg_ld_mbh.min()
print(f"Max clg load {clg_ld_mbh_mx} MBh")
print(f"Max clg load {clg_ld_kwatts_mx} kW")
# endregion: Main
#==========================================================================================================================================================