from __future__ import print_function, division
from simtk import unit as u
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
        data_main = {}
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
            for index in self.drug_name_translator:
                if drug in self.drug_name_translator[index]:
                    drug_index = index
                    break
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
        elif Trel > Tpeak: #and Trel <= Tpeak + 5*Telim:
            C = (0.5)**((Trel-Tpeak)/Telim)
        #elif Trel > Tpeak + 5*Telim:
        #    C = 0
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
        start_day = 0
        stop_day = 1440
        morning = 480
        evening = 1320
        #lunch = 780
        interval = 30
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
            if out_list[0] != 0 and out_list[1] != 0:
                out = sum(out_list)
            return out
        
        time_matrix = list(itertools.combinations_with_replacement(range(morning, evening, interval), no_drugs))
        time_matrix_results = []
        for entry in time_matrix:
            f = lambda T: sum_function(entry, T)            
            AUC = integrate.quad(f, morning, 5*stop_day, limit=150)
            time_matrix_results.append((AUC, entry))
        return time_matrix_results