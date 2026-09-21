from pathlib import Path

import matplotlib.pyplot as plt
import lewisctr_utils
#==========================================================================================================================================================
# region: Parameters
#==========================================================================================================================================================
x_data = ['2018-19', '2024-25', '2025-26']
# x_data = [1, 2, 3]
y1_datas = [[6.020801, 6.329212, 5.985735], [3.611841, .920525, .881121], 
            [4.816641, 4.235888, 4.596528], [4.514801, 1.560805, 1.826342],
            [2.408960, 5.408687, 5.104613]]
y2_datas = [[6.352281, 6.677673, 6.315284], [3.810693, .971205, .929632], 
            [5.081825, 4.469098, 4.849593], [4.763367, 1.646736, 1.926893],
            [2.541587, 5.706467, 5.385652]]

graph_props = [{'color': 'b', 'marker': 'o', 'linestyle':'solid', 'label': 'heat rej'},
               {'color': 'r', 'marker': 'x', 'linestyle':'solid', 'label': 'heat ext'},
               {'color': 'b', 'marker': 'o', 'linestyle':'dotted', 'label': 'clg in bldg'},
               {'color': 'r', 'marker': 'x', 'linestyle':'dotted', 'label': 'htg in bldg'},
               {'color': 'g', 'marker': '^', 'linestyle':'dotted', 'label': 'net heat rej'},]

base_path = Path(__file__).parent.parent.parent
data_path = Path.joinpath(base_path, 'data')
res_folder = Path.joinpath(data_path, f'ground_loop/res_img')
res_path = Path.joinpath(res_folder, f'ground_loop_loads.png')
xaxis_label = 'Year'
yaxis_label1 = 'Heat x1,000,000 (kBtu)'
yaxis_label2 = 'Heat x1,000,000 (MJ)'
legend_loc = {'loc': 'upper center', 'bbox_to_anchor': (0.5, -0.18), 'ncol':3}
graph_title = 'Heat Rejected and Extracted from Borefield'
yaxis_lim1 = [0.60871645,6.60161655]
yaxis_lim2 = [0.6422299499999999, 6.96507505]
# endregion: Parameters
#==========================================================================================================================================================
# region: Functions
#==========================================================================================================================================================
def setup_graph():
    fig, ax1 = plt.subplots()
    ax1.set_xlabel(xaxis_label, fontsize=16)
    ax1.set_ylabel(yaxis_label1, color='k', fontsize=16)
    ax2 = ax1.twinx() 
    ax2.set_ylabel(yaxis_label2, color='k', fontsize=16)
    ax1.tick_params(axis='x', labelsize=16) 
    ax1.tick_params(axis='y', labelsize=16)
    ax2.tick_params(axis='y', labelsize=16)

    ax1.grid(True, axis = 'y', linestyle='--', linewidth = 0.3)
    ax1.grid(True, axis = 'x', linestyle='--', linewidth = 0.3)

    ax1.set_ylim(yaxis_lim1[0],yaxis_lim1[1])
    ax2.set_ylim(yaxis_lim2[0],yaxis_lim2[1])

    plt.tight_layout() 
    ax1.set_title(graph_title, fontsize=16)
    return fig, ax1, ax2

def viz_all_lines(y1_datas, y2_datas, graph_props, res_path):
    fig, ax1, ax2 = setup_graph()
    for cnt, y1_data in enumerate(y1_datas):
        y2_data = y2_datas[cnt]

        ax1.plot(x_data, y1_data, color=graph_props[cnt]['color'], marker= graph_props[cnt]['marker'], label=graph_props[cnt]['label'], 
                 linestyle=graph_props[cnt]['linestyle'], markersize=8)
        ax2.plot(x_data, y2_data, color=graph_props[cnt]['color'], marker= graph_props[cnt]['marker'], label=graph_props[cnt]['label'], 
                 linestyle=graph_props[cnt]['linestyle'], markersize=8)

    ax1.legend(loc=legend_loc['loc'], bbox_to_anchor=legend_loc['bbox_to_anchor'],
            fancybox=True, ncol=legend_loc['ncol'], fontsize = 14)

    # ytick_lim1 = ax1.get_ylim()
    # ytick_lim2 = ax2.get_ylim()
    fig.savefig(res_path, bbox_inches = "tight", dpi = 300, transparent=True)
    plt.show()
    plt.close(fig)

def viz_line_seq(y1_datas, y2_datas, graph_props, res_folder):
    
    for cnt, y1_data in enumerate(y1_datas):
        fig, ax1, ax2 = setup_graph()
        if cnt > 0:
            lewisctr_utils.clean_axes(ax1, ax2)
                        
        y2_data = y2_datas[cnt]

        ax1.plot(x_data, y1_data, color=graph_props[cnt]['color'], marker= graph_props[cnt]['marker'], label=graph_props[cnt]['label'], 
                 linestyle=graph_props[cnt]['linestyle'], markersize=8)
        ax2.plot(x_data, y2_data, color=graph_props[cnt]['color'], marker= graph_props[cnt]['marker'], label=graph_props[cnt]['label'],
                 linestyle=graph_props[cnt]['linestyle'], markersize=8)

        # ax1.legend(loc=legend_loc['loc'], bbox_to_anchor=legend_loc['bbox_to_anchor'],
        #         fancybox=True, ncol=legend_loc['ncol'], fontsize = 14)

        # ytick_lim1 = ax1.get_ylim()
        # ytick_lim2 = ax2.get_ylim()
        res_path = Path.joinpath(res_folder, f'{graph_title}_{cnt}.png')
        fig.savefig(res_path, bbox_inches = "tight", dpi = 300, transparent=True)
        plt.show()
        plt.close(fig)

#==========================================================================================================================================================
# endregion: Functions
#==========================================================================================================================================================
#==========================================================================================================================================================
# region: Main
#==========================================================================================================================================================
if not res_folder.exists():
    res_folder.mkdir()

viz_all_lines(y1_datas, y2_datas, graph_props, res_path)
viz_line_seq(y1_datas, y2_datas, graph_props, res_folder)
#==========================================================================================================================================================
# endregion: Main
#==========================================================================================================================================================
