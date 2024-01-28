from tools_base.subdomain.subdomain_run import SubdomainScanner
from tools_base.subdomain.snrublist3r_run import Snrublist3er
from tools_base.subdomain.chaos_run import Chaos
from tools_base.subdomain.domaintrail_run import Domaintrail
from tools_base.subdomain.gobuster_subdomain_run import GobusterSubdomain

from tools_base.blackwidow.blackwidow_run import Blackwidow
from tools_base.gospider.gospider_run import Gospider
from tools_base.paramspider.paramspider_run import Paramspider
from tools_base.hakrawler.hakrawler_run import Hakrawler
from tools_base.waybackurls.waybackurls_run import Waybackurls
from tools_base.gau.gau_run import Gau
from tools_base.katana.katana_run import Katana

from recon_utils import *
from recon_logging import *
from recon_version_control import *

import os
from datetime import datetime
import pandas as pd
import functools
from multiprocessing import Pool
import re

config_path = "./recon.config"
target = "rei.com"
DEBUG = True
master_timestamp = datetime.today().strftime('%Y_%m_%dT%H_%M_%S')

def smap(f):
    """
    This method is utilised by multiprocess pool
    """
    return f()

# subdomain_process = SubdomainScanner(target, config_path, master_timestamp, DEBUG)
# subdomain_process.build_subdomain_wordlists()
# subdomain_process.run_command("subdomains_merge") # Run only to check the total unique subdomains

# snrublist3r_process = Snrublist3er(target, config_path, DEBUG)
# snrublist3r_process.run_command()

# chaos_process = Chaos(target, config_path, DEBUG)
# chaos_process.run_command()

# gobuster_subdomain_process = GobusterSubdomain(target, config_path, DEBUG)
# gobuster_subdomain_process.run_command(2)

# domaintrail_process = Domaintrail(target, config_path, master_timestamp, DEBUG)
# domaintrail_process.run_command()


# subdomain_process.save_subdomain_tools_output_log({},{})
# subdomain_process.run_subdomain_discovery()

test_tool_logs = {
    "snrublist3r": "./logs/google.com/subdomain_tools_log/snrublist3r_2024_01_13T05_43_51.subs",
    "chaos": "./logs/google.com/subdomain_tools_log/chaos_2024_01_13T05_43_51.subs"
}
# subdomain_process.filter_subdomain_tools_output_with_httpx(test_tool_logs)

sample_subdomains = [
    "winecellar.zomato.com",
    "blog.zomato.com",
    "send.zomato.com"
]

def params_probe_process(subdomain_log_path_name):
    params_temp_path = get_env_values(config_path, "temp", "params_temp_path")
    if not os.path.exists(params_temp_path):
        os.makedirs(params_temp_path)

    subdomains_string = ""
    with open(subdomain_log_path_name, "r") as subdomain_log:
        subdomains_string = subdomain_log.read()
    subdomain_re_matches = re.findall(r"Found: (.*)", subdomains_string)

    blackwidow_process = Blackwidow("www.discord.com", config_path, master_timestamp, DEBUG)
    # output = blackwidow_process.run_probe()
    # print(output)

    gospider_process = Gospider("www.rei.com", config_path, master_timestamp, DEBUG)
    # output2 = gospider_process.run_probe()
    # print(output2)

    paramspider_process = Paramspider("temp", config_path, master_timestamp, DEBUG)
    hakrawler_process = Hakrawler("temp", config_path, master_timestamp, DEBUG)
    waybackurls_process = Waybackurls("temp", config_path, master_timestamp, DEBUG)
    gau_process = Gau("temp", config_path, master_timestamp, True)
    katana_process = Katana("temp", config_path, master_timestamp, True)

    params_tool_objs = {
        "blackwidow": blackwidow_process,
        "gospider": gospider_process,
        "paramspider": paramspider_process,
        "hakrawler": hakrawler_process,
        "waybackurls": waybackurls_process,
        "gau": gau_process,
        "katana": katana_process
    }

    processes = []
    for tool_name in params_tool_objs: 
        processes.append(functools.partial(params_tool_objs[tool_name].run_probe))

    params_probe_schema = {
        "subdomain": "object",
        "urls": "int64",
        "get_params": "int64",
        "post_params": "int64",
        "linkfinder": "int64",
        "javascript":"int64",
        "log": "object"
    }
    params_probe_log_pd = pd.DataFrame(columns=params_probe_schema.keys()).astype(params_probe_schema)

    for sub in subdomain_re_matches[94:97]: # REMOVE THE RANGE AFTER TESTING IN MAIN SCRIPT
        params_temp_sum_dict = {
            "subdomain": sub,
            "urls": 0,
            "get_params": 0,
            "post_params": 0,
            "linkfinder": 0,
            "javascript":0,
            "log": "log"
        }
        
        for tool_name in params_tool_objs:
            params_tool_objs[tool_name].set_subdomain_targer(sub)
        # blackwidow_process.set_subdomain_targer(sub)
        # gospider_process.set_subdomain_targer(sub)
        # paramspider_process.set_subdomain_targer(sub)

        pool = Pool(processes=len(params_tool_objs))
        res = pool.map(smap, processes)
        pool.close()
        pool.join()
        if DEBUG:
            print(res)
        for r in res:
            if params_temp_sum_dict["subdomain"] == r["subdomain"]:
                params_temp_sum_dict["urls"] = params_temp_sum_dict["urls"] + r["urls"][0]
                params_temp_sum_dict["get_params"] = params_temp_sum_dict["get_params"] + r["get_params"][0]
                params_temp_sum_dict["post_params"] = params_temp_sum_dict["post_params"] + r["post_params"][0]
                params_temp_sum_dict["linkfinder"] = params_temp_sum_dict["linkfinder"] + r["linkfinder"][0]
                params_temp_sum_dict["javascript"] = params_temp_sum_dict["javascript"] + r["javascript"][0]
                params_temp_sum_dict["log"] = f'{params_temp_sum_dict["log"]}, {str(r)}'
                if DEBUG:
                    print(params_temp_sum_dict)
            else:
                print(f"[ERROR] The subdomain name is not as expected\nExpected: {params_temp_sum_dict['subdomain']} vs Real {r['subdomain']}")
        temp_row_pd = pd.DataFrame([params_temp_sum_dict])
        params_probe_log_pd = pd.concat([params_probe_log_pd, temp_row_pd], ignore_index=True)
        
    params_logging = Logging(target, config_path, master_timestamp, "params")
    params_loggin_target_dir = params_logging.get_target_logs_dir()
    print(params_loggin_target_dir)
    # print(params_probe_log_pd)
    params_probe_log_pd = params_probe_log_pd.sort_values(['get_params', 'post_params', 'urls'], ascending=False)
    params_probe_log_pd.to_csv(f"{params_loggin_target_dir}/params_probe{master_timestamp}.csv", index=False)

params_probe_process("logs/rei.com/subdomain_tools_log/gobuster_subdomain_validated_merged_2024_01_28T04_21_36.subs.brute")

# version_controller = VersionControl(config_path, "./logs/rei.com/subdomain_tools_log", "./logs/rei.com/subdomain_tools_log/2024_01_26T08_14_30.xml", "subdomain_validate", DEBUG)
# version_controller.compare_version()
