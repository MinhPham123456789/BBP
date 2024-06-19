from recon_phase_scripts.subdomain_run import SubdomainScanner
from recon_phase_scripts.urls_and_params_run import URLsAndParamsScanner

from tools_base.subdomain.snrublist3r_run import Snrublist3er
from tools_base.subdomain.chaos_run import Chaos
from tools_base.subdomain.domaintrail_run import Domaintrail
from tools_base.subdomain.gobuster_subdomain_run import GobusterSubdomain

from tools_base.urls_and_parameters.blackwidow.blackwidow_run import Blackwidow
from tools_base.urls_and_parameters.gospider.gospider_run import Gospider
from tools_base.urls_and_parameters.paramspider.paramspider_run import Paramspider
from tools_base.urls_and_parameters.hakrawler.hakrawler_run import Hakrawler
from tools_base.urls_and_parameters.waybackurls.waybackurls_run import Waybackurls
from tools_base.urls_and_parameters.gau.gau_run import Gau
from tools_base.urls_and_parameters.katana.katana_run import Katana

from tools_base.tech_analysis.nuclei_tech_analysis.nuclei_tech_analysis_run import NucleiTechAnalysis
from tools_base.tech_analysis.built_with.built_with_run import BuiltWithAnalysis

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
DEBUG = not True
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
    "www.tryhackme.com",
    "blog.zomato.com",
    "send.zomato.com"
]

# PARAM PROCESS TEST
# def params_probe_process(subdomain_log_path_name, target, config_path, master_timestamp, debug=False):
#     params_temp_path = get_env_values(config_path, "temp", "params_temp_path")
#     if not os.path.exists(params_temp_path):
#         os.makedirs(params_temp_path)

#     subdomains_string = ""
#     with open(subdomain_log_path_name, "r") as subdomain_log:
#         subdomains_string = subdomain_log.read()
#     subdomain_re_matches = re.findall(r"Found: (.*)", subdomains_string)

#     blackwidow_process = Blackwidow("www.discord.com", config_path, master_timestamp, DEBUG)
#     # output = blackwidow_process.run_probe()
#     # print(output)

#     gospider_process = Gospider("www.rei.com", config_path, master_timestamp, DEBUG)
#     paramspider_process = Paramspider("temp", config_path, master_timestamp, DEBUG)
#     hakrawler_process = Hakrawler("temp", config_path, master_timestamp, DEBUG)
#     waybackurls_process = Waybackurls("temp", config_path, master_timestamp, DEBUG)
#     gau_process = Gau("temp", config_path, master_timestamp, DEBUG)
#     katana_process = Katana("temp", config_path, master_timestamp, DEBUG)

#     ## Init Params Logging and params summary pd
#     params_logging = Logging(target, config_path, master_timestamp, "params")
#     params_logging_target_dir = params_logging.get_target_logs_dir()
#     print(params_logging_target_dir)
#     params_probe_schema = {
#         "subdomain": "object",
#         "urls": "int64",
#         "get_params": "int64",
#         "post_params": "int64",
#         "linkfinder": "int64",
#         "javascript":"int64"
#     }
#     params_probe_log_pd = pd.DataFrame(columns=params_probe_schema.keys()).astype(params_probe_schema)


#     params_tool_objs = {
#         "blackwidow": blackwidow_process,
#         "gospider": gospider_process,
#         "paramspider": paramspider_process,
#         "hakrawler": hakrawler_process,
#         "waybackurls": waybackurls_process,
#         "gau": gau_process,
#         "katana": katana_process
#     }

#     processes = []
#     for tool_name in params_tool_objs: 
#         processes.append(functools.partial(params_tool_objs[tool_name].run_probe))


#     for sub in subdomain_re_matches[40:43]: # REMOVE THE RANGE AFTER TESTING IN MAIN SCRIPT     
#         for tool_name in params_tool_objs:
#             params_tool_objs[tool_name].set_subdomain_targer(sub)
#         # blackwidow_process.set_subdomain_targer(sub)
#         # gospider_process.set_subdomain_targer(sub)
#         # paramspider_process.set_subdomain_targer(sub)

#         pool = Pool(processes=len(params_tool_objs))
#         res = pool.map(smap, processes)
#         pool.close()
#         pool.join()
#         if DEBUG:
#             print(res)

#         params_merged_log_path_name = merge_the_params_output_logs(res, params_logging_target_dir, sub, master_timestamp, DEBUG)
#         params_sum_dict = count_web_crawling_output(params_merged_log_path_name, sub)
#         print(params_sum_dict)

#     #     for r in res:
#     #         if params_temp_sum_dict["subdomain"] == r["subdomain"]:
#     #             params_temp_sum_dict["urls"] = params_temp_sum_dict["urls"] + r["urls"][0]
#     #             params_temp_sum_dict["get_params"] = params_temp_sum_dict["get_params"] + r["get_params"][0]
#     #             params_temp_sum_dict["post_params"] = params_temp_sum_dict["post_params"] + r["post_params"][0]
#     #             params_temp_sum_dict["linkfinder"] = params_temp_sum_dict["linkfinder"] + r["linkfinder"][0]
#     #             params_temp_sum_dict["javascript"] = params_temp_sum_dict["javascript"] + r["javascript"][0]
#     #             params_temp_sum_dict["log"] = f'{params_temp_sum_dict["log"]}, {str(r)}'
#     #             if DEBUG:
#     #                 print(params_temp_sum_dict)
#     #         else:
#     #             print(f"[ERROR] The subdomain name is not as expected\nExpected: {params_temp_sum_dict['subdomain']} vs Real {r['subdomain']}")
#         temp_row_pd = pd.DataFrame([params_sum_dict])
#         params_probe_log_pd = pd.concat([params_probe_log_pd, temp_row_pd], ignore_index=True)
        
#     params_probe_log_pd = params_probe_log_pd.sort_values(by=['get_params', 'post_params', 'urls'], ascending=False)
#     print(params_probe_log_pd)
#     # Delete the subdomains with 0 links maybe
#     params_probe_log_pd.to_csv(f"{params_logging_target_dir}/params_probe{master_timestamp}.csv", index=False)
#     if not DEBUG:
#         params_temp_path = get_env_values(config_path, "temp", "params_temp_path")
#         rm_cmd = f"rm -rf {params_temp_path}/"
#         prep_rm_cmd = prepare_command(rm_cmd)
#         rm_sub_proc = subprocess.run(prep_rm_cmd)
#         if rm_sub_proc.returncode != 0:
#             print(f"[ERROR] Error during running this command {rm_cmd}")
#         else:
#             print(f"[PROCESS] Remove the param tools output logs after merging completed!")

# # params_probe_process("logs/rei.com/subdomain_tools_log/gobuster_subdomain_validated_merged_2024_01_28T04_21_36.subs.brute", target, config_path, master_timestamp)

# # version_controller = VersionControl(config_path, "./logs/rei.com/subdomain_tools_log", "./logs/rei.com/subdomain_tools_log/2024_01_26T08_14_30.xml", "subdomain_validate", DEBUG)
# # version_controller.compare_version()

# urls_and_params_phase = URLsAndParamsScanner(target, config_path, master_timestamp, "logs/rei.com/subdomain_tools_log/gobuster_subdomain_validated_merged_2024_01_28T04_21_36.subs.brute")
# urls_and_params_phase.run_URLs_and_params_discovery()
# print(urls_and_params_phase.get_params_merged_log_path())
# print(urls_and_params_phase.get_params_probe_pd_log_path_name())

nuclei_tech_analysis_process = NucleiTechAnalysis(sample_subdomains[1], config_path, master_timestamp, DEBUG)
test = nuclei_tech_analysis_process.run_command()
print(test)

# built_with_process = BuiltWithAnalysis(sample_subdomains[0], config_path, master_timestamp, DEBUG)
# test2 = built_with_process.run_command()
# print(test2)