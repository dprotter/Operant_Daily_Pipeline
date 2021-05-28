

import analysis_functions as af
from lookup_classes import Operant_event_strings as oes
import pandas as pd
import numpy as np


def run_analysis(data_raw, head, by_round_fname, summary_fname):
    data = data_raw
    #calculations: food lever lat, pellet lat, percent press
    event_1 = oes.lever_out
    event_2 = oes.food_leverpress_prod
    
    col_name = 'food_lever_press_latency'
    
    new_col, new_data = af.latency_by_round(data, event_1, event_2, 
                                             new_col_name = col_name, 
                                             selected_by = event_2)

    new_df_blank = np.asarray([[r, np.nan] for r in data.Round.unique()])
    
    new_df = pd.DataFrame(data = new_df_blank, columns = ['Round',new_col])
    new_df = new_df.astype({'Round':int})
    new_df = af.roundwise_join(new_df, new_data, new_col)

    # pellet lat
    event_1 = oes.disp
    event_2 = oes.retr
    col_name = 'pellet_latency'
    new_col, new_data = af.latency_by_round(data, event_1, event_2, new_col_name = col_name)
    round_df = af.roundwise_join(new_df, new_data, new_col)


    summary = []

    total_rounds = data.Round.max()
    summary += [['number of rounds in experiment', 'rounds', total_rounds]]

    '''calculate the values for the days summary'''
    #calculate number of presses
    total_presses = len(data.loc[data.Event == oes.food_leverpress_prod])
    summary += [['total number of lever presses', 'total_lever_press', total_presses]]

    food_lever_press_prop_of_rounds = total_presses / total_rounds
    summary += [['proportion of rounds on which food lever was pressed', 
                'percent_food_presses', 
                food_lever_press_prop_of_rounds]]

    summary+= [['mean food lever press latency (excludes NaN)',
            'mean_food_lever_press_latency',
                round_df.food_lever_press_latency.mean()]]

    summary+= [['mean pellet retrieval latency (excludes NaN)',
            'mean_pellet_latency',
                round_df.pellet_latency.mean()]]
    
    pel_retrievals = af.count_event(data, oes.retr)
    summary+= [['number of times a pellet was retrieved',
            'num_pellet_retrieved',
                pel_retrievals]]
    
    summary+= [['proportion of rounds when a pellet was retrieved',
            'proportion_round_pellet_retrieved',
                pel_retrievals / total_rounds]]
    
    
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


    
