#%% import modules
import os
import pandas as pd
#from sep_util import read_file
import numpy as np
import statsmodels.api as sm

import matplotlib
import matplotlib.pyplot as plt

import sys
sys.path.append('../')
from utility.general import mkdir
from utility.processing import filter_event_first_order
from utility.regression import predict_magnitude, get_mean_magnitude
from utility.plotting import plot_magnitude_seaborn

# set plotting parameters 
params = {
    'image.interpolation': 'nearest',
    'image.cmap': 'gray',
    'savefig.dpi': 100,  # to adjust notebook inline plot size
    'axes.labelsize': 18, # fontsize for x and y labels (was 10)
    'axes.titlesize': 18,
    'font.size': 18,
    'legend.fontsize': 18,
    'xtick.labelsize': 18,
    'ytick.labelsize': 18,
    'text.usetex':False,
    'axes.facecolor': 'white',
    'savefig.facecolor': 'white', 
    'pdf.fonttype': 42 # Turn off text conversion to outlines
}

matplotlib.rcParams.update(params)

#%%
# some parameters
min_channel = 100 # do regression only on events recorded by at least 100 channels
M_threshold = [2, 10]
weighted = 'wls' # 'ols' or 'wls'
if weighted == 'ols':
    weight_text = '' 
elif weighted == 'wls':
    weight_text = '_weighted' 
else:
    raise

random_test = False # whether to plot the random test for transfered scaling

results_output_dir_list = []
regression_results_dir_list = []
peak_file_name_list = []
result_label_list = []
M_threshold_list = []
snr_threshold_list = []
vmax_list = []
region_text_list = []
plot_type_list = []

#%% # Set result directory
if not random_test:
    # ================== multiple arrays ================== 
    results_output_dir = '../iter_results'
    peak_file_name = '../data_files/peak_amplitude/peak_amplitude_multiple_arrays.csv'
    result_label = 'iter'
    snr_threshold = 10
    M_threshold = [2, 10]
    vmax = [120, 180] # for P and S
    region_text = 'California arrays'
    plot_type = 'histplot'

    M_threshold_list.append(M_threshold)
    results_output_dir_list.append(results_output_dir)
    regression_results_dir_list.append(results_output_dir)
    peak_file_name_list.append(peak_file_name)
    result_label_list.append(result_label)
    snr_threshold_list.append(snr_threshold)
    vmax_list.append(vmax)
    region_text_list.append(region_text)
    plot_type_list.append(plot_type)

    # single arrays
    #  ================== Ridgecrest ================== 
    results_output_dir = '../iter_results_Ridgecrest'
    peak_file_name = '../data_files/peak_amplitude/peak_amplitude_Ridgecrest.csv'
    result_label = 'iter'
    snr_threshold = 10
    M_threshold = [2, 10]
    vmax = [70, 100] # for P and S
    region_text = 'Ridgecrest'
    plot_type = 'histplot'

    M_threshold_list.append(M_threshold)
    results_output_dir_list.append(results_output_dir)
    regression_results_dir_list.append(results_output_dir)
    peak_file_name_list.append(peak_file_name)
    result_label_list.append(result_label)
    snr_threshold_list.append(snr_threshold)
    vmax_list.append(vmax)
    region_text_list.append(region_text)
    plot_type_list.append(plot_type)

    #  ================== Long Valley N ================== 
    results_output_dir = '../iter_results_LongValley_N'
    peak_file_name = '../data_files/peak_amplitude/peak_amplitude_LongValley_N.csv'
    result_label = 'iter'
    snr_threshold = 10
    M_threshold = [2, 10]
    vmax = [35, 50] # for P and S
    region_text = 'Long Valley North'
    plot_type = 'histplot'

    M_threshold_list.append(M_threshold)
    results_output_dir_list.append(results_output_dir)
    regression_results_dir_list.append(results_output_dir)
    peak_file_name_list.append(peak_file_name)
    result_label_list.append(result_label)
    snr_threshold_list.append(snr_threshold)
    vmax_list.append(vmax)
    region_text_list.append(region_text)
    plot_type_list.append(plot_type)

    #  ================== Long Valley S ================== 
    results_output_dir = '../iter_results_LongValley_S'
    peak_file_name = '../data_files/peak_amplitude/peak_amplitude_LongValley_S.csv'
    result_label = 'iter'
    snr_threshold = 10
    M_threshold = [2, 10]
    vmax = [20, 30] # for P and S
    region_text = 'Long Valley South'
    plot_type = 'histplot'

    M_threshold_list.append(M_threshold)
    results_output_dir_list.append(results_output_dir)
    regression_results_dir_list.append(results_output_dir)
    peak_file_name_list.append(peak_file_name)
    result_label_list.append(result_label)
    snr_threshold_list.append(snr_threshold)
    vmax_list.append(vmax)
    region_text_list.append(region_text)
    plot_type_list.append(plot_type)

    #  ================== Sanriku fittd ================== 
    results_output_dir = '../iter_results_Sanriku'
    peak_file_name = '../data_files/peak_amplitude/peak_amplitude_Sanriku.csv'
    result_label = 'iter'
    snr_threshold = 5
    M_threshold = [2, 10]
    vmax = [2, 2] # for P and S
    region_text = 'Sanriku'
    plot_type = 'scatterplot'

    M_threshold_list.append(M_threshold)
    results_output_dir_list.append(results_output_dir)
    regression_results_dir_list.append(results_output_dir)
    peak_file_name_list.append(peak_file_name)
    result_label_list.append(result_label)
    snr_threshold_list.append(snr_threshold)
    vmax_list.append(vmax)
    region_text_list.append(region_text)
    plot_type_list.append(plot_type)

else:
    #  ================== Sanriku transfered test ================== 
    N_event_fit_list = [5]
    N_test = 5
    for N_event_fit in N_event_fit_list:
        for i_test in range(N_test):

            results_output_dir = '../transfered_results'
            peak_file_name = '../data_files/peak_amplitude/peak_amplitude_Sanriku.csv'
            result_label = 'transfer'
            regression_results_dir = results_output_dir + f'/{N_event_fit}_fit_events_{i_test}th_test'
            snr_threshold = 5
            vmax = 50
            M_threshold = [0, 10]
            vmax = [2, 2] # for P and S
            region_text = 'Transfered scaling for Sanriku'
            plot_type = 'scatterplot'

            M_threshold_list.append(M_threshold)
            results_output_dir_list.append(results_output_dir)
            regression_results_dir_list.append(regression_results_dir)
            peak_file_name_list.append(peak_file_name)
            result_label_list.append(result_label)
            snr_threshold_list.append(snr_threshold)
            vmax_list.append(vmax)
            region_text_list.append(region_text) 
            plot_type_list.append(plot_type)

#%%
for ii in range(len(peak_file_name_list)):
    
    peak_file_name = peak_file_name_list[ii]
    regression_results_dir = regression_results_dir_list[ii]
    results_output_dir = results_output_dir_list[ii]
    result_label = result_label_list[ii]
    snr_threshold = snr_threshold_list[ii]
    M_threshold = M_threshold_list[ii]
    vmax = vmax_list[ii]
    region_text = region_text_list[ii]
    plot_type = plot_type_list[ii]

    print(regression_results_dir)

    # load results
    peak_amplitude_df = pd.read_csv(peak_file_name)
    peak_amplitude_df['distance_in_km'] = peak_amplitude_df['calibrated_distance_in_km']
    peak_amplitude_df = filter_event_first_order(peak_amplitude_df, M_threshold=M_threshold, snr_threshold=snr_threshold, min_channel=min_channel)

    if 'Sanriku' in results_output_dir: # some special processing for Sanriku data
        peak_amplitude_df = peak_amplitude_df[peak_amplitude_df.QA == 'Yes']
        peak_amplitude_df = peak_amplitude_df.drop(index=peak_amplitude_df[peak_amplitude_df.event_id == 4130].index)
        #peak_amplitude_df = peak_amplitude_df.drop(index=peak_amplitude_df[peak_amplitude_df.event_id == 1580].index)


    site_term_df = pd.read_csv(regression_results_dir + f'/site_terms_{result_label}.csv')

    try:
        regP = sm.load(regression_results_dir + f"/P_regression_combined_site_terms_{result_label}.pickle")
        magnitude_P, peak_amplitude_df_temp = predict_magnitude(peak_amplitude_df, regP, site_term_df, wavetype='P')
        final_magnitude_P = get_mean_magnitude(peak_amplitude_df_temp, magnitude_P)
    except:
        print('No P regression results, skip...')
        regP, magnitude_P, peak_amplitude_df_temp, final_magnitude_P = None, None, None, None

    try:
        regS = sm.load(regression_results_dir + f"/S_regression_combined_site_terms_{result_label}.pickle")
        magnitude_S, peak_amplitude_df_temp = predict_magnitude(peak_amplitude_df, regS, site_term_df, wavetype='S')
        final_magnitude_S = get_mean_magnitude(peak_amplitude_df_temp, magnitude_S)
    except:
        print('No S regression results, skip...')
        regS, magnitude_S, peak_amplitude_df_temp, final_magnitude_S = None, None, None, None

    # plot figures of strain rate validation
    fig_dir = regression_results_dir + '/figures'
    mkdir(fig_dir)

    xy_lim, height, space = [-1, 8], 8, 0.3

    if result_label == 'iter': 
        try:
            gP = plot_magnitude_seaborn(final_magnitude_P, xlim=xy_lim, ylim=xy_lim, vmax=vmax[0], height=height, space=space, type=plot_type)
            gP.ax_joint.text(0, 7, region_text + f', P wave\n{len(final_magnitude_P.dropna())} events')
            gP.savefig(fig_dir + f'/P_magnitude_prediction_rate_{result_label}_seaborn.png')
            gP.savefig(fig_dir + f'/P_magnitude_prediction_rate_{result_label}_seaborn.pdf')
        except:
            print('No P regression results, skip...')

        try:
            gS = plot_magnitude_seaborn(final_magnitude_S, xlim=xy_lim, ylim=xy_lim, vmax=vmax[1], height=height, space=space, type=plot_type)
            gS.ax_joint.text(0, 7, region_text + f', S wave\n{len(final_magnitude_S.dropna())} events')
            gS.savefig(fig_dir + f'/S_magnitude_prediction_rate_{result_label}_seaborn.png')
            gS.savefig(fig_dir + f'/S_magnitude_prediction_rate_{result_label}_seaborn.pdf')
        except:
            print('No S regression results, skip...')    

    elif result_label == 'transfer':
        temp = np.load(regression_results_dir + '/transfer_event_list.npz')
        event_id_fit_P = temp['event_id_fit_P']
        event_id_fit_S = temp['event_id_fit_S']
        event_id_predict = temp['event_id_predict']

        try:
            final_magnitude_P_fit = final_magnitude_P[final_magnitude_P.event_id.isin(event_id_fit_P)]
            final_magnitude_P_predict = final_magnitude_P[final_magnitude_P.event_id.isin(event_id_predict)]

            gP = plot_magnitude_seaborn(final_magnitude_P_predict, xlim=xy_lim, ylim=xy_lim, vmax=vmax[0], height=height, space=space, type=plot_type)
            gP.ax_joint.plot(final_magnitude_P_fit.magnitude, final_magnitude_P_fit.predicted_M, 'ro')
            # gP.ax_joint.plot(final_magnitude_P_predict.magnitude, final_magnitude_P_predict.predicted_M, 'bo')
            gP.ax_joint.text(-0.5, 7, region_text + f', P wave\n{len(final_magnitude_P_fit.dropna())} events to fit, {len(final_magnitude_P_predict.dropna())} events to predict', fontsize=16)
            gP.savefig(fig_dir + f'/P_magnitude_prediction_rate_{result_label}_seaborn.png')
            gP.savefig(fig_dir + f'/P_magnitude_prediction_rate_{result_label}_seaborn.pdf')
        except:
            print('No valid P wave regression results, skip ...')
            pass

        try:
            final_magnitude_S_fit = final_magnitude_S[final_magnitude_S.event_id.isin(event_id_fit_S)]
            final_magnitude_S_predict = final_magnitude_S[final_magnitude_S.event_id.isin(event_id_predict)]

            gS = plot_magnitude_seaborn(final_magnitude_S_predict, xlim=xy_lim, ylim=xy_lim, vmax=vmax[1], height=height, space=space, type=plot_type)
            gS.ax_joint.plot(final_magnitude_S_fit.magnitude, final_magnitude_S_fit.predicted_M, 'ro')
            # gS.ax_joint.plot(final_magnitude_S_predict.magnitude, final_magnitude_S_predict.predicted_M, 'bo')
            gS.ax_joint.text(-0.5, 7, region_text + f', S wave\n{len(final_magnitude_S_fit.dropna())} events to fit, {len(final_magnitude_S_predict.dropna())} events to predict', fontsize=16)
            gS.savefig(fig_dir + f'/S_magnitude_prediction_rate_{result_label}_seaborn.png')
            gS.savefig(fig_dir + f'/S_magnitude_prediction_rate_{result_label}_seaborn.pdf')
        except:
            print('No valid S wave regression results, skip ...')
            pass

    plt.close('all')


# %%
