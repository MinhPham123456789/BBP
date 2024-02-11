from tools_base.whois.whois_run import Whois
from tools_base.nslookup.nslookup_run import Nslookup
from tools_base.nmap.nmap_run import Nmap
from recon_phase_scripts.subdomain_run import SubdomainScanner
from recon_phase_scripts.urls_and_params_run import URLsAndParamsScanner
from recon_logging import Logging
from recon_version_control import VersionControl

import functools
import re
from multiprocessing import Pool
from datetime import datetime

config_path = "./recon.config"
target = "rei.com"
DEBUG = not True
master_timestamp = datetime.today().strftime('%Y_%m_%dT%H_%M_%S')

def smap(f):
    """
    This method is utilised by multiprocess pool
    """
    return f()

### Init section
xml_logger = Logging(target, config_path, master_timestamp)
tools_object_dictionary = {}
commands_dictionary = {}

### Domain Intelligence Gather section
whois_process = Whois(target, config_path, master_timestamp)
tools_object_dictionary['whois'] = whois_process
commands_dictionary['whois'] = whois_process.command

nslookup_process = Nslookup(target, config_path, master_timestamp)
tools_object_dictionary['nslookup'] = nslookup_process
commands_dictionary['nslookup'] = nslookup_process.command

### Ports and services scan section
nmap_process = Nmap(target, config_path, master_timestamp)
tools_object_dictionary['nmap'] = nmap_process
commands_dictionary['nmap'] = nmap_process.command

processes = []
for tool_name in tools_object_dictionary:
    processes.append(functools.partial(tools_object_dictionary[tool_name].run_command))

pool = Pool(processes=len(tools_object_dictionary))
res = pool.map(smap, processes)
pool.close()
pool.join()
if DEBUG:
    print(res)

### Build the outputs dictionary information gathering
outputs_dictionary = {}
for output_string in res:
    for cmd_key in list(commands_dictionary.keys()):
        if commands_dictionary[cmd_key] in output_string:
            outputs_dictionary[cmd_key] = output_string
            break

if len(outputs_dictionary) != len(res):
    print("[ALERT] THE EXPECTED OUTPUT AND THE PROCESS POOL'S OUTPUT LIST DO NOT HAVE THE SAME LENGTH!!!")

### Subdomain section
# Note: Rebuild the subdomain wordlists is in recon_test
subdomain_process = SubdomainScanner(target, config_path, master_timestamp, 2, DEBUG)

# Build the subdomain wordlist
# subdomain_process.build_subdomain_wordlists()

tools_object_dictionary['subdomain'] = subdomain_process
outputs_dictionary['subdomain'] = subdomain_process.run_subdomain_discovery()
commands_dictionary['subdomain'] = subdomain_process.command

### URLs and parameters section
discovered_subdomain_logs_list = re.findall(r'gobuster_subdomain log path: (.*\.subs\.?.*)\n', outputs_dictionary['subdomain'])
# print(discovered_subdomain_logs_list)
urls_and_params_process = URLsAndParamsScanner(target, config_path, master_timestamp, discovered_subdomain_logs_list)
tools_object_dictionary['urls_and_params'] = urls_and_params_process
outputs_dictionary['urls_and_params'] = urls_and_params_process.run_URLs_and_params_discovery()
commands_dictionary['urls_and_params'] = urls_and_params_process.command

### Logging section
xml_output_order = xml_logger.get_output_order()
for i in xml_output_order:
    try:
        xml_logger.add_tool_log(i, commands_dictionary[i], outputs_dictionary[i])
    except KeyError:
        print(f"tools_object_dictionary KeyError with key '{i}'")
    except Exception as e:
        print(f"[Unknown error] message: {e}")

log_file_path = xml_logger.save_log()
print(f"Outputs are saved to {log_file_path}")

### Version control section
version_controller_display = VersionControl(config_path, xml_logger.get_target_logs_dir(), log_file_path.split("/")[-1], "main_display", DEBUG)
version_controller_display.compare_version()

# if DEBUG:
#     print(version_controller.previous_log_name)
#     print(version_controller.new_log_name)

version_controller_sorted = VersionControl(config_path, xml_logger.get_target_logs_dir(), log_file_path.split("/")[-1], "main_sorted", DEBUG)
try:
    version_control_log_path_name = version_controller_sorted.compare_version()
except TypeError:
    print("No new cersion control log to scan for changes")
version_controller_sorted.send_noti(version_control_log_path_name)