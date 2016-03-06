from __future__ import print_function, division
#from simtk import unit as u
import math
import scipy.integrate as integrate
import csv
import itertools
#import numpy as np
import pandas as pd

class Kinetizer():

    def __init__(self, drugs):
        # drugs is a dict of dictionaries {'ibuprofen': {'start_time':0}}
        self.drugs = drugs
        #self.patient_weight = patient_weight
        self.drug_name_translator = {}
        self.import_data()

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
            #data_main_entry['bioaval_fraction'] = float(entry['bioaval_fraction'])
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
            #self.drugs[drug]['bioavailability_fraction'] = data_main[drug_index]['bioaval_fraction']
            self.drugs[drug]['absorption_time_to_peak'] = data_main[drug_index]['t_abs']
            self.drugs[drug]['elimination_half_life'] = data_main[drug_index]['t_elim']

            #self.drugs[drug]['bioavailability_fraction'] = 1
            #self.drugs[drug]['absorption_half_life'] = 15
            #self.drugs[drug]['elimination_half_life'] = 360

        #self.body_volume = 1 # should be some function of patient_weight

    #def calculate_plasma_conc(self, drug_name, conc_time):
    #    drug_data = self.drugs[drug_name]
    #    T = conc_time
        #F = drug_data['bioavailability_fraction']
    #    Tpeak = drug_data['absorption_time_to_peak']
    #    Telim = drug_data['elimination_half_life']
        #D = drug_data['dose']
        #V = self.body_volume
    #    if T <= Tpeak:
    #        C = T / Tpeak
    #    else:
    #        C = (0.5)**((T-Tpeak)/Telim)

        # master equation
        #C = (F*Ka*D)/(V*(Ka-Ke)) * (math.exp(-Ke*T) - math.exp(-Ka*T))
    #    return C
        
    def master_function(self, drug_name, Tstart, T):
        drug_data = self.drugs[drug_name]
        Trel = T - Tstart
        Tpeak = drug_data['absorption_time_to_peak']
        Telim = drug_data['elimination_half_life']
        if Trel < 0: 
            C = 0
        elif Trel <= Tpeak:
            C = Trel / Tpeak
        elif Trel > Tpeak and Trel <= Tpeak + 5*Telim:
            C = (0.5)**((Trel-Tpeak)/Telim)
        # at Trel == Tpeak + 5*Telim + 1e-10 I want it 0
        elif Trel > Tpeak + 5*Telim and Trel <= Tpeak + 5*Telim + 1e-10:
            C = -1e-10*Trel + 1e-10(Tpeak+5*Telim+1e-10)
        elif Trel > Tpeak + 5*Telim + 1e-10:
            C = 0
        return C

    def return_dataframe(self):
        dataframe = {}
        dataframe['Times'] = []
        for drug in self.drugs:
            drug_list = dataframe[drug] = []
            
            # iterate over timee - time in minutes
            #for time in range(0, 5*int(self.drugs[drug]['elimination_half_life']), 15): # every 15 minutes, up to 5 halflives - steady state
            for time in range(480, 1950, 2):
                drug_list.append(self.master_function(drug, self.drugs[drug]['start_time'], time))
        dataframe['Times'] = range(480, 1950, 2)                        
            # make sure you have value for Tpeak
            #time = self.drugs[drug]['absorption_time_to_peak']
            #drug_list.append(((self.drugs[drug]['start_time'] + time), self.master_function(drug, 0, time)))
        dataframe = pd.DataFrame.from_dict(dataframe)
        return dataframe

    #def integrate_AUC_full(self, drug_name):
    #    drug_data = self.drugs[drug_name]
        #F = drug_data['bioavailability_fraction']
    #    Tpeak = drug_data['absorption_time_to_peak']
    #    Telim = drug_data['elimination_half_life']
        #Ka = math.log(2)/drug_data['absorption_half_life']
        #Ke = math.log(2)/drug_data['elimination_half_life']
        #D = drug_data['dose']
        #V = self.body_volume
        # master equation
        #C = lambda T: (F*Ka*D)/(V*(Ka-Ke)) * (math.exp(-Ke*T) - math.exp(-Ka*T))
        # 5 halflives hardcoded here
    #    C1 = lambda T: T / Tpeak
    #    C2 = lambda T: (0.5)**((T-Tpeak)/Telim)
    #    AUC1 = integrate.quad(C1, 0, Tpeak)
    #    AUC2 = integrate.quad(C2, Tpeak, 5*Telim)
    #    AUC = AUC1 + AUC2
    #    return AUC
        
    def optimize_schedule(self):
        # hardcode interactions
        #interactions = [(0,1,2), (0,2,0), (0,3,1), (1,2,3), (1,3,0), (2,3,2)]
        interactions = [(0,1,2), (0,2,0), (1,2,3)]
        start_day = 0
        stop_day = 1440
        morning = 480
        evening = 1320
        #lunch = 780
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
            #out_combinations = list(itertools.combinations(out_list, 2))
            #for combination in out_combinations:
                #if combination[0] != 0 and combination[1] != 0:
                    #out = sum(combination) *
            if no_drugs == 3:        
                if out_list[0] != 0 and out_list[1] != 0:
                    out += (out_list[0] + out_list[1]) * interactions[0][2]
                if out_list[0] != 0 and out_list[2] != 0:
                    out += (out_list[0] + out_list[2]) * interactions[1][2]
                if out_list[1] != 0 and out_list[2] != 0:
                    out += (out_list[0] + out_list[2]) * interactions[2][2]
            if no_drugs == 4:
                if out_list[0] != 0 and out_list[1] != 0:
                    out += (out_list[0] + out_list[1]) * interactions[0][2]
                if out_list[0] != 0 and out_list[2] != 0:
                    out += (out_list[0] + out_list[2]) * interactions[1][2]
                if out_list[0] != 0 and out_list[3] != 0:
                    out += (out_list[0] + out_list[3]) * interactions[2][2]
                if out_list[1] != 0 and out_list[2] != 0:
                    out += (out_list[1] + out_list[2]) * interactions[3][2]
                if out_list[1] != 0 and out_list[3] != 0:
                    out += (out_list[1] + out_list[3]) * interactions[4][2]
                if out_list[2] != 0 and out_list[3] != 0:
                    out += (out_list[2] + out_list[3]) * interactions[5][2]                 
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
            raise RuntimeError('Too many drugs you moron')            
        time_matrix_results = []
        for entry in time_matrix:
            f = lambda T: sum_function(entry, T)            
            AUC = integrate.quad(f, morning, 5*stop_day, limit=150)
            time_matrix_results.append((AUC, entry))
        return time_matrix_results
        
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