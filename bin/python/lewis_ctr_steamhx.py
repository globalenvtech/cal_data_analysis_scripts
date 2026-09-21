import pytz
from pathlib import Path

import lewisctr_utils
#==========================================================================================================================================================
# region: Functions
#==========================================================================================================================================================

#==========================================================================================================================================================
# endregion: Functions
#==========================================================================================================================================================
#==========================================================================================================================================================
# region: Main
#==========================================================================================================================================================
#----------------------------------------------------------------------------------------------------------
vol_flw_path = Path(__file__).parent.parent.parent.joinpath(f'data/steam_heat_sys/HW Hx Volume FlowCSV/HW Hx Volume Flow.csv')
vol_flw_df = lewisctr_utils.read_clean_resample_csv(vol_flw_path)
vol_flw_df['Value'] = lewisctr_utils.gpm2lpm(vol_flw_df['Value']) # convert gallons per min to liter per min
vol_flw_df.rename(columns={'Value': 'VolumeFlow(lpm)'}, inplace=True)
df_overall = vol_flw_df
df_overall.dropna(inplace=True)
#----------------------------------------------------------------------------------------------------------
# process the datetime for visualization
data_dict_ls = []
dts = df_overall.index.to_pydatetime()

edt = pytz.timezone('America/New_York')
dts_edt = []
dts_nv = []
dur = []
for cnt, dt in enumerate(dts):
    dt_edt = dt.astimezone(edt)
    dt_nv = dt_edt.replace(tzinfo = None)
    dts_edt.append(dt_edt)
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

df_overall['Duration'] = dur
#----------------------------------------------------------------------------------------------------------
# check for the flow
#----------------------------------------------------------------------------------------------------------
vol_flw = df_overall['VolumeFlow(lpm)']
non_zero = vol_flw[vol_flw == 0]
print(len(vol_flw), len(non_zero))