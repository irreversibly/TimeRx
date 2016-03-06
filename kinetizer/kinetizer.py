from __future__ import print_function, division
import math
import scipy.integrate as integrate
import csv
import pandas as pd
from collections import OrderedDict

# demo
#drugs3 = ['nadolol', 'simvastatin', 'atazanavir']
#drugs4 = ['nadolol', 'simvastatin', 'atazanavir', 'vicodin']

class Kinetizer():

    def __init__(self, drugs):
        self.drugs = OrderedDict()
        for drug in drugs:
            self.drugs[drug] = {}
        self.drug_name_translator = {}
        self.import_data()
        # for demo
        #self.load_demo()

    def import_data(self):
        data_main_reader = csv.DictReader(open('../data/drugs_main.csv'))
        data_side_effects_reader = csv.DictReader(open('../data/drugs_side_effects.csv'))
        self.data_main = data_main = {}
        data_side_effects = {}
        # fill in drug_name_translator
        for entry in data_main_reader:
            self.drug_name_translator[int(entry['index'])] = eval(entry['drug_names'])
            data_main_entry = {}
            data_main[int(entry['index'])] = data_main_entry
            data_main_entry['t_elim'] = float(entry['t_elim'])
            data_main_entry['t_abs'] = float(entry['t_abs'])
            data_main_entry['side_eff_single'] = entry['side_eff_single']
            data_main_entry['side_eff_double'] = eval(('tuple(%s)' % entry['side_eff_double']))
        for entry in data_side_effects_reader:
            data_side_effects[entry['index']] = entry['description']
        for drug in self.drugs:
            translated = False
            for index in self.drug_name_translator:
                if drug in self.drug_name_translator[index]:
                    drug_index = index
                    translated = True
                    break
            if not translated:
                raise RuntimeError('Drug not found')
            self.drugs[drug]['absorption_time_to_peak'] = data_main[drug_index]['t_abs']
            self.drugs[drug]['elimination_half_life'] = data_main[drug_index]['t_elim']

    def master_function(self, drug_name, Tstart, T):
        drug_data = self.drugs[drug_name]
        Trel = T - Tstart
        Tpeak = drug_data['absorption_time_to_peak']
        Telim = drug_data['elimination_half_life']
        if Trel < 0:
            C = 0
        elif Trel <= Tpeak:
            C = Trel / Tpeak
        elif Trel > Tpeak:
            C = (0.5)**((Trel-Tpeak)/Telim)
        return C

    def return_dataframe(self):
        dataframe = {}
        dataframe['Times'] = []
        for drug in self.drugs:
            drug_list = dataframe[drug] = []
            for time in range(480, 1950, 2):
                drug_list.append(self.master_function(drug, self.drugs[drug]['start_time'], time))
        dataframe['Times'] = range(480, 1950, 2)
        dataframe = pd.DataFrame.from_dict(dataframe)
        return dataframe

    def optimize_schedule(self):
        interactions4 = [(0,1,2), (0,2,0), (0,3,1), (1,2,3), (1,3,0), (2,3,2)]
        interactions3 = [(0,1,2), (0,2,0), (1,2,3)]
        start_day = 0
        stop_day = 1440
        morning = 480
        evening = 1320
        interval = 60
        no_drugs = len(self.drugs)
        drug_names = {}
        counter = 0
        for drug in self.drugs:
            drug_names[counter] = drug
            counter += 1
        def sum_function(entry, T):
            out_list = []
            out = 0
            for x in drug_names:
                out_list.append(self.master_function(drug_names[x], entry[x], T))
            if no_drugs == 3:
                if out_list[0] != 0 and out_list[1] != 0:
                    out += (out_list[0] + out_list[1]) * interactions3[0][2]
                if out_list[0] != 0 and out_list[2] != 0:
                    out += (out_list[0] + out_list[2]) * interactions3[1][2]
                if out_list[1] != 0 and out_list[2] != 0:
                    out += (out_list[0] + out_list[2]) * interactions3[2][2]
            if no_drugs == 4:
                if out_list[0] != 0 and out_list[1] != 0:
                    out += (out_list[0] + out_list[1]) * interactions4[0][2]
                if out_list[0] != 0 and out_list[2] != 0:
                    out += (out_list[0] + out_list[2]) * interactions4[1][2]
                if out_list[0] != 0 and out_list[3] != 0:
                    out += (out_list[0] + out_list[3]) * interactions4[2][2]
                if out_list[1] != 0 and out_list[2] != 0:
                    out += (out_list[1] + out_list[2]) * interactions4[3][2]
                if out_list[1] != 0 and out_list[3] != 0:
                    out += (out_list[1] + out_list[3]) * interactions4[4][2]
                if out_list[2] != 0 and out_list[3] != 0:
                    out += (out_list[2] + out_list[3]) * interactions4[5][2]
            return out
        the_range = range(morning, evening, interval)
        vicodin_start = 660
        vicodin_end = 840
        the_vicodin_range = range(vicodin_start, vicodin_end, interval)
        if no_drugs == 2:
            time_matrix = [(x,y) for x in the_range for y in the_range]
        elif no_drugs == 3:
            time_matrix = [(x,y,z) for x in the_range for y in the_range for z in the_range]
        elif no_drugs == 4:
            time_matrix = [(x,y,z,w) for x in the_range for y in the_range for z in the_range for w in the_vicodin_range]
        else:
            raise RuntimeError('Too many drugs')
        time_matrix_results = []
        for entry in time_matrix:
            f = lambda T: sum_function(entry, T)
            AUC = integrate.quad(f, morning, 5*stop_day, limit=150)
            time_matrix_results.append((AUC, entry))
        return (time_matrix_results, drug_names)

    def find_min(self, time_matrix_results):
        holding_list = []
        for entry in time_matrix_results:
            holding_list.append(entry[0][0])
        minimum = min(holding_list)
        min_times = []
        for entry in time_matrix_results:
            if entry[0][0] == minimum:
                min_times.append(entry[1])
        return min_times

    def get_schedule(self):
        if self.schedule:
            tuple_schedule = []
            for drug in self.schedule:
                tuple_schedule.append((drug, self.schedule[drug]))
            tuple_schedule = sorted(tuple_schedule, key=lambda x: float(x[1]))
            return tuple_schedule
        time_matrix_results, drug_names = self.optimize_schedule()
        min_times = self.find_min(time_matrix_results)
        if len(min_times) > 1:
            raise RuntimeError('More than one min_times options')
        schedule = {}
        for index in drug_names:
            schedule[drug_names[index]] = min_times[0][index]
        return schedule

    def save_for_demo(self):
        schedule = self.get_schedule()
        field_names = ['drug_name', 'scheduled_time']
        if len(self.drugs) == 3:
            with open('../demo/schedule_3drugs.csv', 'w') as f:
                csv_writer = csv.DictWriter(f, fieldnames=field_names)
                csv_writer.writeheader()
                for drug in schedule:
                    csv_writer.writerow({'drug_name':drug, 'scheduled_time':schedule[drug]})
        elif len(self.drugs) == 4:
            with open('../demo/schedule_4drugs.csv', 'w') as f:
                csv_writer = csv.DictWriter(f, fieldnames=field_names)
                csv_writer.writeheader()
                for drug in schedule:
                    csv_writer.writerow({'drug_name':drug, 'scheduled_time':schedule[drug]})

    def load_demo(self):
        schedule_reader_3drugs = csv.DictReader(open('../demo/schedule_3drugs.csv'))
        schedule_reader_4drugs = csv.DictReader(open('../demo/schedule_4drugs.csv'))
        schedule_3drugs = {}
        schedule_4drugs = {}
        if len(self.drugs) == 3:
            for entry in schedule_reader_3drugs:
                schedule_3drugs[entry['drug_name']] = int(entry['scheduled_time'])
                self.drugs[entry['drug_name']]['start_time'] = int(entry['scheduled_time'])
                self.schedule = schedule_3drugs
        if len(self.drugs) == 4:
            for entry in schedule_reader_4drugs:
                schedule_4drugs[entry['drug_name']] = int(entry['scheduled_time'])
                self.drugs[entry['drug_name']]['start_time'] = int(entry['scheduled_time'])
                self.schedule = schedule_4drugs