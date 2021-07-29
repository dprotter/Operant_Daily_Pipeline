import pandas as pd
import numpy as np
import sys
import os

from lookup_classes import Operant_event_strings as oes

def assemble_names(directory):
    '''return a list of paths to files to parse'''
    os.chdir(directory)

    #create an empty 2d list
    out_names = []

    #this will assemble a list of ALL filenames for images, sorted by timestamp of acquisition


    for root, dirs, files in os.walk(directory):
        out = [os.path.join(root, f) for f in sorted(files) if
            f.endswith('.csv') if not f.startswith('.')]
        out_names += out
    return out_names

def latency_by_round(df, event_1, event_2,  
                    new_col_name = None, 
                    include_missing_data_as_nan = False, 
                    selected_by = None,
                    get_rounds_from = 'first'
                ):
    '''get the latency from event_1 to event_2. event_1 should be whatever occurred first. If 
    there is a length mismatch of 1 this will assume the latency of the last index of event_1
    is missing. For example, a pellet was not retrieved before the end of the experiment. This
    event will be trimmed unless include_missing_data_as_nan is set to True. 
    
    This function assumes each round can have at most 1 latency to calculate.
    
    round number indicates round in which event_1 happened
    
    include_missing_data_as_nan = True --> final value of returned array will be np.nan selected_by 
                                           should be a list of events to select your desired rounds by. 
                                           For example, if we want to choose lever press latency we 
                                           should only select rounds on which a lever was pressed, 
                                           and will pass that as [<lever_press_event_string>]. 
    
    in contrast, if we want to get the pellet retrieval we should ignore this, as retrievals
    can happen on different rounds than when the pellet was dispensed. (Pellet dispensed on round 2,
    retrieved on round 5, for example)
    
    get_rounds_from : str, 'first' or 'second'. Which event to get the round numbers from. For example,
                      if a pellet is dispensed in round 1 and retrieved in round 4, we can use 'first'
                      to assign the round in the output to 1, or use 'second' to assign the round in
                      the output to 4.
                      
    selected_by : event_string. If you want to limit the rounds analyzed to rounds on which an event occurred. For example, 
                  if we want to limit lever_press analysis to only rounds on which a lever was pressed, ignoring
                  rounds on which a lever wasnt pressed, we can use "selected_by = <door_2 leverpress string>"  

    '''
    
    if get_rounds_from not in ('first', 'second'):
        raise TypeError('get_rounds_from tells this function which event to use when noting the round corresponding to latency. Must be "first" or "second"')
    
    if not new_col_name:
        new_col = f'latency_from_|{event_1}|_to_|{event_2}|'
    else:
        new_col = new_col_name
    
    '''new_df_blank = np.asarray([[r, np.nan] for r in df.Round.unique()])
    new_df = pd.DataFrame(data = new_df_blank, columns = ['Round',new_col_name])'''
    
    if selected_by:
        #choose the rounds where selected_by occurs
        rounds = df.loc[df.Event == selected_by, 'Round'].unique()
        
        #only get rounds where selected_by has occured. dont use for events
        #whose latencies cross a change in round!
        sli_1 = df.loc[(df.Event == event_1)&(df.Round.isin(rounds))].copy()
        sli_2 = df.loc[(df.Event == event_2)&(df.Round.isin(rounds))].copy()
    else:
        sli_1 = df.loc[(df.Event == event_1)].copy()
        sli_2 = df.loc[(df.Event == event_2)].copy()
    
        
    if len(sli_1) == len(sli_2):
        #length of slices match, so we can simply take the difference
        
        #which event should be the one from which the round labels are taken?
        #for example, for pellet latencies, we usually want the round on which the 
        #pellet was dispensed. But it could be useful to instead use the round
        #on which the pellet was retrieved. 
        if get_rounds_from == 'first':
            sli_1.loc[:, new_col] = sli_2.Time.values - sli_1.Time.values
            return new_col, sli_1
        else:
            #use the slice for the second event to get rounds
            sli_2.loc[:,new_col] = sli_2.Time.values - sli_1.Time.values
            return new_col, sli_2
        
    elif len(sli_1) == len(sli_2) + 1:
        if get_rounds_from == 'first':
            sli_1.loc[:, new_col] = np.nan
            lat = sli_2.Time.values - sli_1.Time.values[:-1]
            sli_1.iloc[:-1].loc[:, new_col] = lat
            return new_col, sli_1
        else:
            sli_2.loc[:,new_col] = np.nan
            lat = sli_2.Time.values - sli_1.Time.values[:-1]
            sli_2.iloc[:-1].loc[:, new_col] = lat
            return new_col, sli_2
    else:
        raise IndexError(f'these two events, "{event_1}" and "{event_2}" have an unequal number of recordings (diff > 1).\n e1: {len(sli_1)} e2: {len(sli_2)}')

def latency_by_round_expect_unequal(df, event_1, event_2,  
                    new_col_name = None, 
                    include_missing_data_as_nan = False, 
                    selected_by = None,
                    get_rounds_from = 'first'
                ):
    '''get the latency from event_1 to event_2. event_1 should be whatever occurred first. If 
    there is a length mismatch of 1 this will assume the latency of the last index of event_1
    is missing. For example, a pellet was not retrieved before the end of the experiment. This
    event will be trimmed unless include_missing_data_as_nan is set to True. 
    
    This function assumes each round can have at most 1 latency to calculate.
    
    round number indicates round in which event_1 happened
    
    include_missing_data_as_nan = True --> final value of returned array will be np.nan selected_by 
                                           should be a list of events to select your desired rounds by. 
                                           For example, if we want to choose lever press latency we 
                                           should only select rounds on which a lever was pressed, 
                                           and will pass that as [<lever_press_event_string>]. 
    
    in contrast, if we want to get the pellet retrieval we should ignore this, as retrievals
    can happen on different rounds than when the pellet was dispensed. (Pellet dispensed on round 2,
    retrieved on round 5, for example)
    
    get_rounds_from : str, 'first' or 'second'. Which event to get the round numbers from. For example,
                      if a pellet is dispensed in round 1 and retrieved in round 4, we can use 'first'
                      to assign the round in the output to 1, or use 'second' to assign the round in
                      the output to 4.
                      
    selected_by : event_string. If you want to limit the rounds analyzed to rounds on which an event occurred. For example, 
                  if we want to limit lever_press analysis to only rounds on which a lever was pressed, ignoring
                  rounds on which a lever wasnt pressed, we can use "selected_by = <door_2 leverpress string>"  


    might be able to replace all this with pd.merge functionality:
    https://pandas.pydata.org/pandas-docs/version/0.20/merging.html

    '''
    
    if get_rounds_from not in ('first', 'second'):
        raise TypeError('get_rounds_from tells this function which event to use when noting the round corresponding to latency. Must be "first" or "second"')
    
    if not new_col_name:
        new_col = f'latency_from_|{event_1}|_to_|{event_2}|'
    else:
        new_col = new_col_name
    
    '''new_df_blank = np.asarray([[r, np.nan] for r in df.Round.unique()])
    new_df = pd.DataFrame(data = new_df_blank, columns = ['Round',new_col_name])'''
    
    if selected_by:
        #choose the rounds where selected_by occurs
        rounds = df.loc[df.Event == selected_by, 'Round'].unique()
        
        #only get rounds where selected_by has occured. dont use for events
        #whose latencies cross a change in round!
        sli_1 = df.loc[(df.Event == event_1)&(df.Round.isin(rounds))].copy()
        sli_2 = df.loc[(df.Event == event_2)&(df.Round.isin(rounds))].copy()
    else:
        sli_1 = df.loc[(df.Event == event_1)].copy()
        sli_2 = df.loc[(df.Event == event_2)].copy()
    
        
    if len(sli_1) == len(sli_2):
        #length of slices match, so we can simply take the difference
        
        #which event should be the one from which the round labels are taken?
        #for example, for pellet latencies, we usually want the round on which the 
        #pellet was dispensed. But it could be useful to instead use the round
        #on which the pellet was retrieved. 
        if get_rounds_from == 'first':
            sli_1.loc[:, new_col] = sli_2.Time.values - sli_1.Time.values
            return new_col, sli_1
        else:
            #use the slice for the second event to get rounds
            sli_2.loc[:,new_col] = sli_2.Time.values - sli_1.Time.values
            return new_col, sli_2
        
    elif len(sli_1) == len(sli_2) + 1:
        if get_rounds_from == 'first':
            sli_1.loc[:, new_col] = np.nan
            lat = sli_2.Time.values - sli_1.Time.values[:-1]
            sli_1.iloc[:-1].loc[:, new_col] = lat
            return new_col, sli_1
        else:
            sli_2.loc[:,new_col] = np.nan
            lat = sli_2.Time.values - sli_1.Time.values[:-1]
            sli_2.iloc[:-1].loc[:, new_col] = lat
            return new_col, sli_2
    else:
        
        sli_1.rename(columns = {"Time":event_1}, inplace = True)
        sli_2.rename(columns = {"Time":event_2}, inplace = True)
        print(sli_1.head())
        new_df = pd.merge(sli_1, sli_2, on = 'Round')
        print(new_df.head())
        new_df[new_col] = new_df[event_2] - new_df[event_1]

        return new_col, new_df

def latency_by_round_v2(df, event_1, event_2,  
                    new_col_name = None, 
                    include_missing_data_as_nan = False, 
                    selected_by = None,
                    get_rounds_from = 'first'
                ):

    '''want to try and rewrite using pandas merge function'''




def latency_to_beam_break(df):

    #use 'selected_by' to reset the latency check for each round. that way
    #some rounds will have NaN if the animal didnt break the beam after the door
    #opened on that round

    d1_col_name, round_df_d1 = latency_by_round_expect_unequal(df, 
                                              event_1 = oes.door1_open_start, 
                                              event_2 = oes.beam_break_1,
                                              selected_by = oes.beam_break_1, 
                                              new_col_name = 'latency_beam_break_door1')

    d2_col_name, round_df_d2 = latency_by_round_expect_unequal(df, 
                                              event_1 = oes.door2_open_start, 
                                              event_2 = oes.beam_break_2,
                                              selected_by = oes.beam_break_2, 
                                              new_col_name = 'latency_beam_break_door2')
    
    return {d1_col_name:round_df_d1, d2_col_name:round_df_d2}

def count_event(df, event):
    return len(df.loc[df.Event == event])

def count_contingent_events(df, event_1, event_2):
    '''counttimes event_2 occured after event_1 within the same round. 
    eg # of rounds in which beam break occured after lever press'''
    
    rounds = df.loc[df.Event == event_1, 'Round'].unique()
    e1_count = 0
    e2_count = 0
    
    for r in rounds:
        e1_count += len(df.loc[(df.Event == event_1) & ('Round'==r)])
        e2_count += len(df.loc[(df.Event == event_2) & ('Round'==r)])
        
    return {event_1:e1_count, event_2:e2_count}


def roundwise_join(df1, df2, new_col_name):
    new_df = df1.copy()
    new_df[new_col_name] = np.nan
    if len(df2.Round.unique()) != len(df2):
        raise IndexError(f'impossible to match on Round, as there are duplicate rounds. \n{df2.Round.value_counts()}')
    for index, row in df2.iterrows():
        r = int(row.Round)
        val = row[new_col_name]
        new_df.loc[new_df.Round == r, new_col_name] = val
    
    return new_df

def remove_duplicate_events(df, event_str):
    df_out = df.copy()
    for r in df.Round.unique():
        if len(df.loc[(df.Round ==r)&(df.Event == event_str)]) > 1:
            indices = df.index[(df.Round ==r)&(df.Event == event_str)].tolist()
            
            df_out.drop(axis = 0, index = indices[1:], inplace = True)
            
    return df_out

def create_header_string(header_dict):
        '''make a file header from a header_dict'''
        heading_string = ''
        for key in header_dict.keys():
            heading_string+=f'{key}:{header_dict[key]}|'
        return heading_string

def get_header(fname, skiplines = 1):
    """header looks like:
    
    vole:3558.0|day:4.0|experiment:Door_shape|user:protter|output_directory:/home/pi/Documents/operant_experiment|partner:door_1|novel_num:000|completed_rounds:nan|done:False|expected_date:10_2_20|experiment_status:nan|num_rounds:20.0|rounds_completed:nan|run_time:nan|script:Door_shape|
    """
    with open(fname) as f:
        for _ in range(skiplines):
            f.readline()
        header_vals = f.readline().split('|')
        header_dict = {}
        for val in header_vals:
            unpacked = val.split(':')
            if len(unpacked) == 2:
                header_dict[unpacked[0]] = unpacked[1]
            if len(unpacked) > 2:
                print(f'hmm, theres something weird going on in the header. Heres the value:{val}')
                
    return header_dict

def line_prepender(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)
        


