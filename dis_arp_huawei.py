
from nornir import InitNornir
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result
from nornir.plugins.inventory.simple import SimpleInventory
from nornir.core.plugins.inventory import InventoryPluginRegister
from nornir_netmiko.tasks import netmiko_send_command
from itertools import count
from time import sleep
from ttp import ttp
import json
from collections import OrderedDict
import types
from datetime import datetime
import time


#https://saidvandeklundert.net/2020-12-06-nornir/



ttp_template_l2 = """
{{interface}} transceiver information:
  Wavelength(nm)                 :{{Wavelength}}
  Transfer Distance(m)           :{{Distance}}
  Vendor Part Number             :{{PN}}     
  RX Power(dBM)                 :{{RX}}
  RX Power Low Threshold(dBM)   :{{RX_THR}}
  TX Power(dBM)                 :{{TX}}
"""

 
ttp_l3 = """
{{interface}} transceiver information:
  Wavelength(nm)                 :{{Wavelength}}
  Transfer Distance(m)           :{{Distance}}
  Vendor Part Number             :{{PN}}
  Current Rx Power(dBM)                 :{{RX}}
  Default Rx Power Low  Threshold(dBM)  :{{RX_THR}}
  Current Tx Power(dBM)                 :{{TX}}
"""


ttp_2 ="""
<group name="interfaces">
{{if_name}} current state : {{if_state}}
{{if_dscr | contains ('Description')}}
The Vendor Name is {{Vendor}}            , The Vendor PN is {{PN}} 
Transceiver max BW: {{BW}}, Transceiver Mode: {{Mode}}
WaveLength: {{Wavelength}}, Transmission Distance: {{Distance}}
Rx Optical Power: {{RX | ORPHRASE}}
</group>
"""



ttp_template_router_optics = """ 
{{if_name}} current state : {{if_state}}
The Vendor Name is {{Vendor}}            , The Vendor PN is {{PN}} 
Transceiver max BW: {{BW}}, Transceiver Mode: {{Mode}}
WaveLength: {{Wavelength}}, Transmission Distance: {{Distance}}
Rx Optical Power: {{RX | ORPHRASE}}
"""
#Tx Optical Power: {{TX | re(r"-\d+.\d\d...")}}, TX_RANGE | re(r".-\d+.\d+,.-\d.\d+....")}}


def print_influx_metrics(olt_hostname,data):
    """
    The print_influx_metrics function takes the data collected in a dictionary format and prints out
    each of the necesary components on a single line, which matches the Influx data format.

    Args:
        data (dictionary): Dictionary of the results to print out for influx
    """
    data_string = ""
    cnt = count()
    for measure, value in data.items():
        if next(cnt) > 0:
            data_string += ","
        data_string += f"{measure}={value}"

    print(f" {olt_hostname} {data_string}")

    return True

# ttp supported format 
# Supported: ['raw', 'yaml', 'json', 'csv', 'jinja2', 'pprint', 'tabulate', 'table', 'excel', 'graph'].



def main():
    
    nr = InitNornir(
        runner={
            "plugin": "threaded",
            "options": {
                "num_workers": 100,
            },
        },
        inventory={
            "plugin": "SimpleInventory",
            "options": {
                    "host_file": "/home/srdjan/nr3/inventory/hosts.yaml",
                    "group_file": "/home/srdjan/nr3/inventory/groups.yaml",
                    "defaults_file": "/home/srdjan/nr3/inventory/defaults.yaml"
            },
        }
    )         
    #filter nornir to Huawei
  #  nr = nr.filter(platform="huawei")        # SVI HUAWEI UREDJAJI 
 #   nr = nr.filter(F(groups__contains="huawei_igw"))   # SVI IZ GRUPE HUAWEI IGW 
  #  nr = nr.filter(hostname='bg-igw')   # run just on one router 
    hl2 = nr.filter(F(groups__contains="huawei_switchl2"))   # SVI L2 switchevi
    hl3 = nr.filter(F(groups__contains="huawei_switchl3"))   # SVI L3 switchevi
#    hrouters = nr.filter(F(groups__contains="huawei_igw") | F(groups__contains="huawei_pe"))
    hrouters = nr.filter(F(groups__contains="huawei_igw"))
#    cmd_l2 = "display transceiver verbose"
#    cmd_l3 = "display transceiver verbose"
    cmd_router_optics = "display interface GigabitEthernet main"
    cmd_dis_arp = "dis arp all"
    
#    nr_hl2 = hl2.run(name="hl2_grab_info", task=netmiko_send_command, command_string=cmd_l2)  
#    nr_hl3 = hl3.run(name="hl3_grab_info", task=netmiko_send_command, command_string=cmd_l3)
    nr_hrouters = hrouters.run(name="hrouters_grab_info", task=netmiko_send_command, command_string=cmd_dis_arp)  # Dict

# (Pdb) nr_hl2
# AggregatedResult (hl2_grab_info): {'sw-palic': MultiResult: [Result: "hl2_grab_info"], 'sw-se-1': MultiResult: [Result: "hl2_grab_info"], 
# 'sw-bp-1': MultiResult: [Result: "hl2_grab_info"], 'sw-voip': MultiResult: [Result: "hl2_grab_info"], 
# 'sw-tm-1': MultiResult: [Result: "hl2_grab_info"], 'sw-moravica': MultiResult: [Result: "hl2_grab_info"], 'sw-orom': MultiResult: [Result: "hl2_grab_info"], 'sw-turija': MultiResult: [Result: "hl2_grab_info"], 'sw-ap-1': MultiResult: [Result: "hl2_grab_info"], 'sw-ka-1': MultiResult: [Result: "hl2_grab_info"], 'sw-srb-1': MultiResult: [Result: "hl2_grab_info"], 'fk': MultiResult: [Result: "hl2_grab_info"], 'sc': MultiResult: [Result: "hl2_grab_info"], 'sox': MultiResult: [Result: "hl2_grab_info"], 'sw-ada-1': MultiResult: [Result: "hl2_grab_info"], 'sw-be-15': MultiResult: [Result: "hl2_grab_info"], 'sw-zg-1': MultiResult: [Result: "hl2_grab_info"], 'sw-ti-1': MultiResult: [Result: "hl2_grab_info"], 'sw-za-1': MultiResult: [Result: "hl2_grab_info"], 'sw-crv-1': MultiResult: [Result: "hl2_grab_info"]}


#    nr_hrouters = hrouters.run(name="hrouters_grab_info", task=netmiko_send_command, command_string=cmd_router_optics)  # Dict


# (Pdb) nr_hrouters
# AggregatedResult (hrouters_grab_info): {'bg-igw': MultiResult: [Result: "hrouters_grab_info"], 
# 'ho-igw': MultiResult: [Result: "hrouters_grab_info"], 'be-igw': MultiResult: [Result: "hrouters_grab_info"], 
# 'ho-pe': MultiResult: [Result: "hrouters_grab_info"], 'be-pe': MultiResult: [Result: "hrouters_grab_info"], 
# 'bg-pe': MultiResult: [Result: "hrouters_grab_info"]}

# Pdb) nr_hrouters.keys()
# dict_keys(['bg-igw', 'ho-igw', 'be-igw', 'ho-pe', 'be-pe', 'bg-pe'])        # DICT KEYS 

# Pdb) nr_hrouters['bg-igw']
# MultiResult: [Result: "hrouters_grab_info"]        # 0 je jedini elemnet list-e

######### RESULT STRING ACCESS - VIDIS REALNI STRING OUTPUT 
# (Pdb) nr_hrouters['bg-igw'][0].result    # OUTPUT JE S>T>RING REZULT - OUTPUT SA RUTERA 


#### Ovde stopiramo scriptu i mozemo da chekiramo line by line , uncomment ako hoces pdb 
    # import pdb; pdb.set_trace()
    # breakpoint()

    for host, task_result in nr_hrouters.items():
        data_all = {}
        my_task_data = task_result[0] 
        print_result(my_task_data)
#        parser = ttp(data=str(my_task_data), template=ttp_2)
#        parser.parse()

#        results = parser.result(format='json')[0]

#        d = json.loads(results)




if __name__ == "__main__":
     main()




