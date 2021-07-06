import pandas as pd
import numpy as np

import os

import analysis_functions as af

import traceback


#longitudinal functions
def read_summary_csv(filepath):
    head = af.get_header(filepath, skiplines = 0)
    df = pd.read_csv(filepath, header = 1)
    df.set_index('Unnamed: 0', inplace = True)
    return head, df.transpose()
    
    
def read_round_csv(filepath):
    head = af.get_header(filepath, skiplines = 0)
    df = pd.read_csv(filepath, header = 1)
    
    return head, df

class LongitudinalAnalysis:
    
    def __init__(self, experiment_name):
        self.experiment_name = experiment_name
        self.experiments = []
        self.metrics = {}
        self.metrics_by_round = {}
        self._plottable_metrics = []
    
    
    def get_data(self, metric: str, experiment: str, dataset):
        if not metric in self.metrics:
            print(f'metric: {metric} not found in dataset')
            return None
        met = self.metrics[metric].data
        data = met.loc[met.experiment == experiment]
        anis = sorted(data.animal.unique() )
        days = sorted(data.day.unique() )

        out = np.empty((len(anis), len(days)))
        out[:,:] = np.nan

        for i, ani in enumerate(anis):

            ani_slice = data.loc[data.animal == ani]
            for d in ani_slice.day.unique():
                val = ani_slice.loc[ani_slice.day == d, 'value'].values[0]
                
                out[i,int(d-1)] = val
        
        return anis, days, out
    
    
    def plottable_metrics(self):
            return self._plottable_metrics
        
    def set_plottable_metrics(self):
        for metric in self.metrics.keys():
            if metric in self._plottable_metrics:
                continue
                
            elif self.metrics[metric].plottable:
                self._plottable_metrics += [metric]
            
            else:
                continue

    def add_summary_csv(self, file):
        head, df = read_summary_csv(file)
        animal = df.loc[df.var_name == 'animal_ID', 'var'].values[0]
        experiment = df.loc[df.var_name == 'experiment', 'var'].values[0]
        day = df.loc[df.var_name == 'day', 'var'].values[0]
        
        self.experiments += [experiment]
        
        for var_n in df.var_name.unique():
            value = df.loc[df.var_name == var_n, 'var'].values[0]
            new_row = {'animal':[animal], 'day':[day], 'value':[value],
                      'experiment':[experiment], 'file':[file]}
            if var_n in self.metrics.keys():
                metric = self.metrics[var_n]
                
                try:
                    metric.add_data(new_row)
                    metric.sort_data()
                except:
                    print(f"\n\ncouldnt add data to {metric.name}:\n{new_row}\n\n")
                    pass
                    traceback.print_exc()
            else:
                value = df.loc[df.var_name == var_n, 'var'].values[0]
                name = var_n
                desc = df.loc[df.var_name == var_n, 'var_desc'].values[0]
                
                new_metric = Metric(name, desc,new_row)
                
                self.metrics[var_n] = new_metric
            self.set_plottable_metrics()
        
    def add_by_round_csv(self, file):
        
        head, df = read_round_csv(file)
        
        animal = head['vole']
        experiment = head['experiment']
        day = head['day']

        cols = [var for var in df.columns if var not in ['Unnamed: 0', 'Round']]
        
        for var_name in cols:
            value_df = df[['Round', var_name]]
            value_df.rename(columns = {var_name:'value'}, inplace = True)
            
            if var_name in self.metrics.keys():
                self.metrics[var_name].add_data(animal, experiment, day, value_df, file)

            else:
                value_df = df[['Round', var_name]]
                value_df.rename(columns = {var_name:'value'}, inplace = True)
                name = var_name

                new_metric = Metric_by_round(name)
                new_metric.add_data(animal, experiment, day, value_df, file)

                self.metrics[name] = new_metric            
        
        
        
        

class Metric:
    '''An object that is a single metric from the summary datasets. contains some basic
    information about the metric and some attributes that are useful for longitudinal experiments.'''
    
    def __init__(self, name, var_desc, first_row):
        self.name = name
        self.description = var_desc
        self.data = pd.DataFrame(first_row)
        self.data_type = str
        self.plottable = False
        self._do_not_plot = ['day', 'date']
        self._plottable_types = [int, float]
    
    def check_plottable(self):
        if self.name in self._do_not_plot:
            self.plottable = False
        
        elif self.data_type in self._plottable_types:
            self.plottable = True
            
        else:
            self.plottable = False
            print(f"{self.name} is {self.data_type} and plottable:{self.plottable}")
    
    '''def add_data(self, animal_num, day, value, experiment, file):'''
    def add_data(self, new_row):
        
        animal_num = new_row['animal'][0]
        day = new_row['day'][0]
        exp = new_row['experiment'][0]
        #check if this day is already occupied within this metric
        if len(self.data.loc[(self.data.animal == animal_num) & 
                             (self.data.day == day) &
                             (self.data.experiment == exp), 'value']) > 0:
            old_val = self.data.loc[(self.data.animal == animal_num) & (self.data.day == day), 'value'].values[0]
            old_file = self.data.loc[(self.data.animal == animal_num) & (self.data.day == day), 'file'].values[0]
            value = new_row['value']
            file = new_row['file']
            
            raise DuplicateData(self.name, animal_num, day,old_val , value, old_file, file, exp)
        

        new_row = pd.DataFrame(data = new_row, index=[len(self.data)+1])
        
        dtype = self.intuit_dtype(new_row)
        if dtype != self.data_type:
            self.data_type = dtype
        self.check_plottable()
        
        self.data = self.data.append(new_row)
        
        self.data = self.data.astype({'day':float})
        self.data = self.data.astype({'value':self.data_type, 'day':int})
        
        
        
        
    def sort_data(self):
        self.data.sort_values(['animal','experiment','day'], inplace = True)
    
    def intuit_dtype(self, new_row):
        val = new_row.value.values[0]
        try:
            b = int(val)
        except Exception as e:
            
            try:
                a = float(val)
            except Exception as e:
                
                return str
            else:
                if np.isnan(a): 
                    return float
                
                elif int(a) == a:
                    return int
                
                else:
                    return float
        return int
        
        
    
class DuplicateData(Exception):
    """The day and animal that was passed to this Metric is already present."""
    def __init__(self, metric_name, animal, day, old_val, new_val, old_file, new_file):
        self.metric_name = metric_name
        self.old_file = old_file
        self.new_file = new_file
        self.ani = animal
        self.day = day
        self.old_val = old_val
        self.new_val = new_val
        self.message = ''
        super().__init__(self.message)

    def __str__(self):
        return f'metric: {self.metric_name}\nday: {self.day}\nanimal: {self.ani}\nold value: {self.old_val}\nnew value passed: {self.new_val}\nold_file:{self.old_file}\nnew_file:{self.new_file}'

class DuplicateRoundData(Exception):
    """The day and animal that was passed to this Metric is already present."""
    def __init__(self, metric_name, animal, exp, day, old_file, new_file):
        self.metric_name = metric_name
        self.old_file = old_file
        self.new_file = new_file
        self.ani = animal
        self.day = day

        self.message = ''
        super().__init__(self.message)

    def __str__(self):
        return f'metric: {self.metric_name}\nday: {self.day}\nanimal: {self.ani}\nold_file:{self.old_file}\nnew_file:{self.new_file}'


class Metric_by_round:
    '''An object that '''
    def __init__(self, name):
        self.name = name
        
        #{ animal -> experiment -> day }
        self.data = {}
        self.animal_order = []
        
    
    def get_data(self, experiment, day = None, animal = None, order = None):
        
        animal_order = order if order else self.animal_order
        
        if animal and day:
            
            out = self.data[animal][experiment][day]
        
        elif day:
            
            out = {ani:self.data[ani][experiment][day] for ani in animal_order}
        
        elif animal:
            out = self.data[animal][experiment]
    
        else:
            out = {ani:self.data[ani][experiment] for ani in animal_order}
            
        return out
            
    def add_data(self, animal_num, experiment, day, df, file):
        df['file'] = file
        if animal_num in self.data.keys():
            
            if experiment in self.data[animal_num].keys():
                if day in self.data[animal_num][experiment].keys():
                    old_file = self.data[animal_num][experiment][day]['file'].values[0]
                    raise DuplicateRoundData(self.name, animal_num, experiment, day, old_file, file)
                else:
                    self.data[animal_num][experiment][day] = df
            else:
                #if we dont have this experiment yet, we must create a new heirarchy
                #                  animal
                #                     |
                #                    ----
                #                    |   |
                #          experiment 1  experiment 2
                #           |    |        |    |    |
                #         day1  day2     day1 day2 day3
                self.data[animal_num][experiment] = {day:df}
                
        else:
            #if we dont have this animal yet, we must create a new heirarchy
            #                  animal
            #                     |
            #                    ----
            #                    |   |
            #          experiment 1  experiment 2
            #           |    |        |    |    |
            #         day1  day2     day1 day2 day3
            
            self.data[animal_num]={experiment:{day:df}}
            
            #add new animal to the animal order to be used when fetching data
            self.animal_order +=[animal_num]
            self.animal_order = sorted(self.animal_order)
        
            
