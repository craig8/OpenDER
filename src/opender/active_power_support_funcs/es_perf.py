# Copyright © 2022 Electric Power Research Institute, Inc. All rights reserved.

# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met: 
# · Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# · Redistributions in binary form must reproduce the above copyright notice, 
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# · Neither the name of the EPRI nor the names of its contributors may be used 
#   to endorse or promote products derived from this software without specific
#   prior written permission.

from opender.auxiliary_funcs.ramping import Ramping


# %%
class EdgeDetector:
    """
    Edge Detector
    """

    def __init__(self, up_edge=False, dn_edge=False):
        # x0: initial output value
        # up_edge: detect up edge
        # dn_edge: detect down edge
        self.x = None
        self.up_edge = up_edge
        self.dn_edge = dn_edge

    def run(self, x):
        """
        Return 1 if an up edge or down edge is detected.

        Input Argument:
        
        :param x: Input signal for edge detection
        
        Output:
        
        :param y: If up edge or down edge detected, return 1
        """
        if self.x is None:
            self.x = x
        if self.up_edge and (x - self.x > 0.1):
            y = 1
        elif self.dn_edge and (self.x - x > 0.1):
            y = 1
        else:
            y = 0
        self.x = x
        return y


class EnterServicePerformance:
    """
    Calculate desired active power output in Enter service ramp condition
    EPRI Report Reference: Section 3.7 in Report #3002025583: IEEE 1547-2018 OpenDER Model
    """

    def __init__(self, der_obj):

        self.der_obj = der_obj
        self.der_file = der_obj.der_file
        self.exec_delay = der_obj.exec_delay

        self.rrl = Ramping()
        self.edge = EdgeDetector(
            up_edge=True,
            )
        self.es_flag = None
        self.p_desired_w = None
        self.es_completed = False

    def es_performance(self):
        """
        Variable used in this function:
        
        :param der_status:	Status of DER (on or off)
        :param es_ramp_rate_exec:	Enter service soft-start duration (ES_RAMP_RATE) signal after execution delay
        :param p_act_supp_w:	Desired output active power from active power support functions in kW
        :param NP_P_MAX:	Active power rating at unity power factor

        Internal Variable:
        
        :param es_flag:	Flag to indicate whether DER is in start-up process
        :param p_es_w:	Desired output active power considering DER status
        :param p_es_ramp_w:	Desired output active power during enter service ramp
        :param es_flag_set:	Set value for es_flag flipflop logic
        :param es_flag_reset:	Reset value for es_flag flipflop logic

        Output:
        
        :param p_desired_w:	Desired output active power considering DER enter service performance
        """


        # Eq. 3.7.1-2, ramp rate limiter



        # # Eq. 3.7.1-3 Edge detector to identify Enter Service decision
        # es_flag_set = self.edge.run(True if der_status != 'Trip' else False)

        # Eq. 3.7.1-4 Enter service ramp complete
        # es_flag_reset = (p_es_ramp_pu == p_desired_pu) or not der_status or self.der_obj.activepowerfunc.freqdroop.pf_uf_active or self.der_obj.activepowerfunc.freqdroop.pf_of_active


        # # Eq. 3.7.1-5, flip-flop logic to determine if in enter service ramp
        # if es_flag_reset:
        #     self.es_flag = 0
        # elif es_flag_set:
        #     self.es_flag = 1

        # Eq. 3.7.1-6, output selector
        if self.der_obj.der_status == "Entering Service":
            # if self.der_obj.der_input.p_avl_pu > 0:
            self.p_es_pu = self.rrl.ramp(1.1, self.exec_delay.es_ramp_rate_exec, 0)
            # else:
            #     self.p_es_pu = self.rrl.ramp(self.der_obj.der_input.p_avl_pu, 0, self.exec_delay.es_ramp_rate_exec)

            # self.es_completed = (abs(p_es_ramp_pu) >= abs(p_desired_pu)) # or self.der_obj.activepowerfunc.freqdroop.pf_uf_active or self.der_obj.activepowerfunc.freqdroop.pf_of_active
        elif self.der_obj.der_status == "Trip":
            self.p_es_pu = self.rrl.ramp(0, 0, 0)
        else:
            self.p_es_pu = self.rrl.ramp(self.der_obj.der_input.p_avl_pu, 0, 0)
            # self.es_completed = False

        return self.p_es_pu
