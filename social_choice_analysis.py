import sys
sys.path.append('/home/pi/')

import analysis_functions as af
from lookup_classes import Operant_event_strings as oes
import pandas as pd
import numpy as np


def run_analysis(data_raw, head, by_round_fname, summary_fname):
    data = af.remove_duplicate_events(data_raw, event_str = ' Levers out')

    #get latency from levers out to door_2 lever presses
    event_1 = oes.lever_out
    event_2 = oes.door2_leverpress_prod
    
    col_name = 'door_2_lever_press_latency'
    
    
    new_col, new_data = af.latency_by_round(data, event_1, event_2, 
                                             new_col_name = col_name, 
                                             selected_by = event_2)
    
    new_df_blank = np.asarray([[r, np.nan] for r in data.Round.unique()])
    
    new_df = pd.DataFrame(data = new_df_blank, columns = ['Round',new_col])
    new_df.Round = new_df.Round.astype(int)
    new_df = af.roundwise_join(new_df, new_data, new_col)


    event_1 = oes.lever_out
    event_2 = oes.door1_leverpress_prod
    col_name = 'door_1_lever_press_latency'
    new_col, new_data = af.latency_by_round(data, event_1, event_2, new_col_name = col_name, selected_by = event_2)
    round_df = af.roundwise_join(new_df, new_data, new_col)


    summary = []

    total_rounds = data.Round.max()
    summary += [['number of rounds in experiment', 'rounds', total_rounds]]

    '''calculate the values for the days summary'''
    #calculate number of presses
    total_presses = len(data.loc[data.Event == oes.door1_leverpress_prod]) + len(data.loc[data.Event == oes.door2_leverpress_prod])
    summary += [['total number of lever presses', 'total_lever_press', total_presses]]

    door_1_lever_press_count = af.count_event(data, oes.door1_leverpress_prod)
    summary += [['number of presses for door 1', 'door_1_lever_press_count', door_1_lever_press_count]]

    door_2_lever_press_count = af.count_event(data, oes.door2_leverpress_prod)
    summary += [['number of presses for door 2', 'door_2_lever_press_count', door_2_lever_press_count]]

    door_1_lever_press_prop_of_rounds = door_1_lever_press_count / total_rounds
    summary += [['proportion of rounds on which door 1 was pressed', 
                'door_1_lever_press_round_proportion', 
                door_1_lever_press_prop_of_rounds]]

    door_2_lever_press_prop_of_rounds = door_2_lever_press_count / total_rounds
    summary += [['proportion of rounds on which door 2 was pressed', 
                'door_2_lever_press_round_proportion', 
                door_2_lever_press_prop_of_rounds]]

    door_1_lever_press_prop_of_presses = door_1_lever_press_count / total_presses
    summary += [['proportion of all presses that were for door_1', 
                'door_1_lever_press_total_press_proportion', 
                door_1_lever_press_prop_of_presses]]

    door_2_lever_press_prop_of_presses = door_2_lever_press_count / total_presses
    summary += [['proportion of all presses that were for door_2', 
                'door_2_lever_press_total_press_proportion', 
                door_2_lever_press_prop_of_presses]]


    summary+= [['mean door_1 lever press latency (excludes NaN)',
            'mean_door_1_lever_press_latency',
                round_df.door_1_lever_press_latency.mean()]]

    summary+= [['mean door_2 lever press latency (excludes NaN)',
            'mean_door_2_lever_press_latency',
                round_df.door_2_lever_press_latency.mean()]]
    summary+= [['animal ID',
            'animal_ID',
                head['vole']]]

    summary+= [['experiment day entered by experimenter',
            'day',
                head['day']]]
    summary+= [['experiment script name',
            'experiment',
                head['experiment']]]
    summary+= [['time of run',
            'date',
                head['run_time']]]


    summary_df = pd.DataFrame(data = summary, columns = ['var_desc','var_name','var'])
    summary_df = summary_df.transpose()
    
    
    round_df.to_csv(by_round_fname)
    header_string = af.create_header_string(head)
    af.line_prepender(by_round_fname, header_string)
    
    summary_df.to_csv(summary_fname)
    af.line_prepender(summary_fname, header_string)