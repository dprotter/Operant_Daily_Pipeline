

import analysis_functions as af
from lookup_classes import Operant_event_strings as oes
import pandas as pd
import numpy as np

#door shape and door test should have the same calculations but they should have diff files
def run_analysis(data_raw, head, by_round_fname, summary_fname):
    data = af.remove_duplicate_events(data_raw, event_str = ' Levers out')

    #get latency from levers out to door_2 lever presses
    event_1 = oes.lever_out
    event_2 = oes.door1_leverpress_prod
    
    col_name = 'door_1_lever_press_latency'
    
    
    new_col, new_data = af.latency_by_round(data, event_1, event_2, 
                                             new_col_name = col_name, 
                                             selected_by = event_2)
    
    new_df_blank = np.asarray([[r, np.nan] for r in data.Round.unique()])
    
    new_df = pd.DataFrame(data = new_df_blank, columns = ['Round',new_col])
    
    new_df = new_df.astype({'Round':int})
    new_df = af.roundwise_join(new_df, new_data, new_col)


    event_1 = oes.lever_out
    event_2 = oes.door2_leverpress_prod
    col_name = 'door_2_lever_press_latency'
    new_col, new_data = af.latency_by_round(data, event_1, event_2, new_col_name = col_name, selected_by = event_2)
    round_df = af.roundwise_join(new_df, new_data, new_col)
    
    beam_breaks = af.latency_to_beam_break(data)
    d1_by_round = beam_breaks['latency_beam_break_door1']
    d2_by_round = beam_breaks['latency_beam_break_door2']

    round_df = af.roundwise_join(round_df, d1_by_round, new_col_name='latency_beam_break_door1')
    round_df = af.roundwise_join(round_df, d2_by_round, new_col_name='latency_beam_break_door2')

    summary = []

    total_rounds = data.Round.max()
    summary += [['number of rounds in experiment', 'rounds', total_rounds]]

########## door leverpress section #############3

    '''calculate the values for the days summary'''
    #calculate number of presses
    total_presses = len(data.loc[data.Event == oes.door1_leverpress_prod]) + len(data.loc[data.Event == oes.door2_leverpress_prod])
    summary += [['total number of lever presses', 'total_lever_press', total_presses]]

###

    door_1_lever_press_count = af.count_event(data, oes.door1_leverpress_prod)
    summary += [['number of presses for door 1', 'door_1_lever_press_count', door_1_lever_press_count]]

    door_2_lever_press_count = af.count_event(data, oes.door2_leverpress_prod)
    summary += [['number of presses for door 2', 'door_2_lever_press_count', door_2_lever_press_count]]

 ###   
    door_1_lever_press_prop_of_rounds = door_1_lever_press_count / total_rounds
    summary += [['proportion of rounds on which door 1 was pressed', 
                'door_1_lever_press_round_proportion', 
                door_1_lever_press_prop_of_rounds]]

    door_2_lever_press_prop_of_rounds = door_2_lever_press_count / total_rounds
    summary += [['proportion of rounds on which door 2 was pressed', 
                'door_2_lever_press_round_proportion', 
                door_2_lever_press_prop_of_rounds]]

###    

    if total_presses > 0:
        door_1_lever_press_prop_of_presses = door_1_lever_press_count / total_presses
    else:
        door_1_lever_press_prop_of_presses = np.nan
    
    summary += [['proportion of all presses that were for door_1', 
                'door_1_lever_press_total_press_proportion', 
                door_1_lever_press_prop_of_presses]]

    if total_presses > 0:
        door_2_lever_press_prop_of_presses = door_2_lever_press_count / total_presses
    else:
        door_2_lever_press_prop_of_presses = np.nan    
        
    summary += [['proportion of all presses that were for door_2', 
                'door_2_lever_press_total_press_proportion', 
                door_2_lever_press_prop_of_presses]]

###

    summary+= [['mean door_1 lever press latency (excludes NaN)',
            'mean_door_1_lever_press_latency',
                round_df.door_1_lever_press_latency.mean()]]

    summary+= [['mean door_2 lever press latency (excludes NaN)',
            'mean_door_2_lever_press_latency',
                round_df.door_2_lever_press_latency.mean()]]

    #####beambreak section######

    d1_beambreaks = af.count_event(data, oes.beam_break_1)
    d2_beambreaks = af.count_event(data, oes.beam_break_2)

    summary+= [['number of door 1 beam breaks (max 1/round) (proxy for crossing, but could also be doorway investigation)',
        'door_1_beam_breaks',
            d1_beambreaks]]

    summary+= [['number of door 2 beam breaks (max 1/round) (proxy for crossing, but could also be doorway investigation)',
        'door_2_beam_breaks',
            d2_beambreaks]]

###

    d1_openings = af.count_event(data, oes.door1_open_start)
    summary+= [['proportion of door_1 opening on which the beam was subsequently broken',
        'prop_d1_beambreak_by_open',
            d1_beambreaks / d1_openings]]

    d2_openings = af.count_event(data, oes.door2_open_start)
    summary+= [['proportion of door_2 opening on which the beam was subsequently broken',
        'prop_d2_beambreak_by_open',
            d2_beambreaks / d2_openings]]

####
    d1_leverpress_beambreaks= af.count_contingent_events(data, oes.door1_leverpress_prod, oes.beam_break_1)
    if d1_leverpress_beambreaks[oes.door1_leverpress_prod] > 0:
        prop_d1_beambreak_by_press = d1_leverpress_beambreaks[oes.beam_break_1] / d1_leverpress_beambreaks[oes.door1_leverpress_prod]
    else:
        prop_d1_beambreak_by_press = np.nan

    summary+= [['proportion of door_1 lever presses on which the beam was subsequently broken',
        'prop_d1_beambreak_by_press',
            prop_d1_beambreak_by_press]]

    d2_leverpress_beambreak_events = af.count_contingent_events(data, oes.door2_leverpress_prod, oes.beam_break_2)
    
    d2_leverpress_beambreaks= af.count_contingent_events(data, oes.door2_leverpress_prod, oes.beam_break_2)
    if d2_leverpress_beambreaks[oes.door2_leverpress_prod] > 0:
        prop_d2_beambreak_by_press = d2_leverpress_beambreaks[oes.beam_break_2] / d1_leverpress_beambreaks[oes.door2_leverpress_prod]
    else:
        prop_d2_beambreak_by_press = np.nan
    
    summary+= [['proportion of door_2 lever presses on which the beam was subsequently broken',
        'prop_d2_beambreak_by_press',
            prop_d2_beambreak_by_press]]
    
    
    # proportion beam break after door opened automatically (bb) / (door_open - lever_press)
    auto_events1 =  af.count_event(data, oes.door1_open_start) - af.count_event(data, oes.door1_leverpress_prod) 
           
    prop_auto_d1_beambreak = af.count_event(data, oes.beam_break_1) / auto_events1 if auto_events1 > 0 else np.nan
    
    auto_events2 = af.count_event(data, oes.door2_open_start) - af.count_event(data, oes.door2_leverpress_prod) 
    prop_auto_d2_beambreak = af.count_event(data, oes.beam_break_2) / auto_events2 if auto_events2 > 0 else np.nan
    
    
    summary+= [['proportion auto-opening door_1 which the beam was subsequently broken',
        'prop_d1_beambreak_auto_open',
            prop_auto_d1_beambreak]]
    
    summary+= [['proportion auto-opening door_2 which the beam was subsequently broken',
        'prop_d2_beambreak_auto_open',
            prop_auto_d2_beambreak]]
    

###

    summary+= [['mean door_1 beambreak latency (max 1/round) (proxy for crossing, but could also be doorway investigation)',
        'mean_door_1_beam_break_latency',
            round_df.latency_beam_break_door1.mean()]]

    summary+= [['mean door_2 beambreak latency (max 1/round) (proxy for crossing, but could also be doorway investigation)',
        'mean_door_2_beam_break_latency',
            round_df.latency_beam_break_door2.mean()]]


    ##### general info section #####


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