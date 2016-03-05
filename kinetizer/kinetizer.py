from __future__ import print_function, division
from simtk import unit as u
import math
import numpy as np
import pandas as pd

class Kinetizer():

    def __init__(self, drugs, patient_weight):
        # drugs is a dict of dictionaries {'ibuprofen': {dose: '', start_time}}
        self.drugs = drugs
        self.patient_weight = patient_weight

    def import_data(self):
        # import from CSV here, for now hardcode for example
        for drug in self.drugs:
            self.drugs[drug]['bioavailability_fraction'] = 1
            self.drugs[drug]['absorption_half_life'] = 15
            self.drugs[drug]['elimination_half_life'] = 360

        self.body_volume = 1 # should be some function of patient_weight

    def calculate_plasma_conc(self, drug_name, conc_time):
        drug_data = self.drugs[drug_name]
        #T0 = drug_data['start_time']
        T = conc_time
        F = drug_data['bioavailability_fraction']
        Ka = math.log(2)/drug_data['absorption_half_life']
        Ke = math.log(2)/drug_data['elimination_half_life']
        D = drug_data['dose']
        V = self.body_volume
        plasma_conc = C = 0

        # master equation
        C = (F*Ka*D)/(V*(Ka-Ke)) * (math.exp(-Ke*T) - math.exp(-Ka*T))
        return C

    def return_dataframe(self):
        dataframe = {}
        for drug in self.drugs:
            drug_list = dataframe[drug] = []
            # iterate over timees - time in minutes
            for time in range(0, 5*self.drugs[drug]['elimination_half_life'], 15): # every 15 minutes
                drug_list.append(((self.drugs[drug]['start_time'] + time), self.calculate_plasma_conc(drug, time)))
        return dataframe
