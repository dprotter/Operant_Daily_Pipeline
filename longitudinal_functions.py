import pandas as pd
import numpy as np
import os
import analysis_functions as af

def read_summary_csv(filepath):
    head = af.get_header(filepath, skiplines = 0)
    df = pd.read_csv(filepath, header = 1)
    df.set_index('Unnamed: 0', inplace = True)
    return head, df.transpose()
    
    
def read_round_csv(filepath):
    head = af.get_header(filepath, skiplines = 0)
    df = pd.read_csv(filepath, header = 1)
    
    return head, df

def get_data(metric: str, experiment: str, dataset, days:list = None):
        
        
        if not metric in dataset.metrics:
            print(f'metric: {metric} not found in dataset')
            return None
        met = dataset.metrics[metric].data
        data = met.loc[met.experiment == experiment]
        
        anis = dataset.animal_order if dataset.animal_order else sorted(data.animal.unique() )
        
        if days == None:
            days = sorted(data.day.unique() )

        out = np.empty((len(anis), len(days)))
        out[:,:] = np.nan

        for i, ani in enumerate(anis):

            ani_slice = data.loc[data.animal == ani]
            
            
            for j, d in enumerate(days):
                if d in ani_slice.day.unique():
                    val = ani_slice.loc[ani_slice.day == d, 'value'].values[0]
                    
                    out[i,j] = val
                    
        return anis, days, out


def update_values_table(data, animal_numbers, sex_list, days, experiment, metric, values_table):
    '''data           --> numpy arrays
    animal_numbers --> iterable of animal numbers
    sex_list       --> iterable of animal sex, corresponding with animal_numbers
    days           --> int or, preferably, list of days corresponding with values in data
    experiment     --> experiment name for lookup
    metric         --> name of the value being used'''
    return pd.concat((values_table, 
                      generate_values_table(data = data, 
                                            animal_numbers = animal_numbers, 
                                            sex_list = sex_list, 
                                            days = days, 
                                            experiment = experiment, 
                                            metric = metric)), 
                                            ignore_index=True)
 
def generate_values_table(data, animal_numbers, sex_list, days, experiment, metric):
    '''data            --> numpy arrays
        animal_numbers --> iterable of animal numbers
        sex_list       --> iterable of animal sex, corresponding with animal_numbers
        days           --> int or, preferably, list of days corresponding with values in data
        experiment     --> experiment name for lookup
        metric         --> name of the value being used'''
    output_df = pd.DataFrame(columns = ['animal', 'day', 'sex', 'value', 'experiment', 'metric'])
    if isinstance(days, int):
        
        #double check we only have 1 day of data
        if len(data[0]) == 1:
            tmp = np.insert(data, values = animal_numbers, obj = 0, axis = 1)
            tmp = np.insert(data, values = sex_list, obj = 1, axis = 1)
            tmp = np.insert(tmp, values = days)
            tmp_df = pd.DataFrame(tmp, columns = ['animal', 'day', 'value'])
            output_df = pd.concat((output_df, tmp_df), ignore_index = True)
            output_df['experiment'] = experiment
            output_df['metric'] = metric
    else:
        
        if len(data[0]) != len(days):
            
            raise Exception('data and days length mismatch')
        else:
            
            for ani_data, animal, sex in zip(data, animal_numbers, sex_list):
                tmp_df = pd.DataFrame(ani_data, columns = ['value'])
                tmp_df['day'] = days
                tmp_df['animal'] = animal
                tmp_df['sex'] = sex
                tmp_df['experiment'] = experiment
                tmp_df['metric'] = metric
                output_df = pd.concat((output_df, tmp_df), ignore_index = True)
    return output_df