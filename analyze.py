import pandas as pd
import traceback
import sys
import os

import analysis_script_lookup as asl
import analysis_functions as af

def run_analysis_script(filepath, custom_script = None, output_loc = None):
    '''fpath of csv output from operant experiment. Can direct to a custom 
    analysis script by passing its full path.'''
    header = af.get_header(filepath)
    
    #
    fname_sum, fname_by_round, df = prep_for_analysis(filepath, 
                                                      output_override_loc = output_loc)
    if not custom_script:
        try:
            exp = header['experiment']
        except KeyError:
            print('error getting header key "experiment"')
            print(header)
            print(f'file: {filepath}')
            pass
        except:
            traceback.print_exc()
        
        print(f'exp is {exp}')
        try:
            analysis_module = asl.script_lookup(exp)
        except:
            traceback.print_exc()
            print(f'couldnt lookup {exp}')
            
    else:
        analysis_module = asl.load_custom_script(custom_script)

    analysis_module.run_analysis(data_raw = df,
                                       head = header,
                                       by_round_fname = fname_by_round,
                                       summary_fname = fname_sum)

def prep_for_analysis(filepath, output_override_loc = None):
    
    if output_override_loc:
        if os.path.isdir(output_override_loc):
            filepath_out = os.path.join(output_override_loc, 
                                    filepath.split('/')[-1])
        else:
            print(f'{output_override_loc} does not exist, falling back to file location directory:')
            filepath_out = filepath
    else:
        filepath_out = filepath
            
    fname_summary = append_name_general(filepath_out, 'summary')
    fname_by_round = append_name_general(filepath_out, 'analysis_by_round')
        
    df = pd.read_csv(filepath, skiprows = 2)
    df.dropna(axis = 1, inplace = True)
    return fname_summary, fname_by_round, df
       


def append_name_general(input_name, append_str, sep = '_'):
        vals = input_name.split('.')
        return vals[0] + sep + append_str + '.' + vals[1]


    
