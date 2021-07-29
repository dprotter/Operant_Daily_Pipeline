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