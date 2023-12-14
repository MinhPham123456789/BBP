from tools_base.whois.whois_run import Whois
from tools_base.nmap.nmap_run import Nmap
from recon_logging import Logging
import functools
from multiprocessing import Pool

config_path = "./recon.config"
target = "medium.com"
DEBUG = True

def smap(f):
    return f()

### Init section
xml_logger = Logging(target, config_path)
tools_object_dictionary = {}
commands_dictionary = {}

whois_process = Whois(target, config_path, DEBUG)
tools_object_dictionary['whois'] = whois_process
commands_dictionary['whois'] = whois_process.command
# whois_output = whois_process.run_command()

nmap_process = Nmap(target, config_path, DEBUG)
tools_object_dictionary['nmap'] = nmap_process
commands_dictionary['nmap'] = nmap_process.command
# nmap_output = nmap_process.run_command()

processes = []
for p in list(tools_object_dictionary.values()):
    processes.append(functools.partial(p.run_command))

pool = Pool(processes=len(tools_object_dictionary))
res = pool.map(smap, processes)
pool.close()
pool.join()
if DEBUG:
    print(res)

### Build the outputs dictionary
outputs_dictionary = {}
for output_string in res:
    for cmd_key in list(commands_dictionary.keys()):
        if commands_dictionary[cmd_key] in output_string:
            outputs_dictionary[cmd_key] = output_string
            break

if len(outputs_dictionary) != len(res):
    print("[ALERT] THE EXPECTED OUTPUT AND THE PROCESS POOL'S OUTPUT LIST DO NOT HAVE THE SAME LENGTH!!!")

### Logging section
xml_output_order = xml_logger.get_output_order()
for i in xml_output_order:
    try:
        xml_logger.add_tool_log(i, outputs_dictionary[i])
    except KeyError:
        print(f"tools_object_dictionary KeyError with key '{i}'")
    except Exception as e:
        print(f"[Unknown error] message: {e}")

log_file_path = xml_logger.save_log()
print(f"Outputs are saved to {log_file_path}")