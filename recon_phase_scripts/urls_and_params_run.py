from multiprocessing import Pool
import pandas as pd
import functools

from recon_utils import *
from recon_logging import *

from tools_base.urls_and_parameters.blackwidow.blackwidow_run import Blackwidow
from tools_base.urls_and_parameters.gospider.gospider_run import Gospider
from tools_base.urls_and_parameters.paramspider.paramspider_run import Paramspider
from tools_base.urls_and_parameters.hakrawler.hakrawler_run import Hakrawler
from tools_base.urls_and_parameters.waybackurls.waybackurls_run import Waybackurls
from tools_base.urls_and_parameters.gau.gau_run import Gau
from tools_base.urls_and_parameters.katana.katana_run import Katana


class URLsAndParamsScanner:
    """
    This class run the URLs and parameters discovery process
    """
    def __init__(self, target, command_config_path, timestamp, subdomain_log_path_names_list, debug=not True):
        self.target = target
        self.config_path = command_config_path
        self.subdomain_log_path_names_list = subdomain_log_path_names_list
        self.timestamp = timestamp
        self.debug = debug
        self.command = "URLs and parameters discovery"
        self.params_merged_log_path = ""   # The path to the logs of the URLs and params lists
        self.params_probe_pd_log_path_name = "" # The path and name of the pd summary record
        self.params_temp_path = get_env_values(self.config_path, "temp", "params_temp_path")
        if not os.path.exists(self.params_temp_path):
            os.makedirs(self.params_temp_path)

    def run_URLs_and_params_discovery(self):
        subdomain_re_matches = []
        for subdomain_log_path_name in self.subdomain_log_path_names_list:
            subdomains_string = ""
            with open(subdomain_log_path_name, "r") as subdomain_log:
                subdomains_string = subdomain_log.read()
            subdomain_re_matches = subdomain_re_matches + re.findall(r"Found: (.*)", subdomains_string)
            print(len(subdomain_re_matches))
        # Init and create tool objects
        blackwidow_process = Blackwidow("www.discord.com", self.config_path, self.timestamp, self.debug)
        gospider_process = Gospider("www.rei.com", self.config_path, self.timestamp, self.debug)
        paramspider_process = Paramspider("temp", self.config_path, self.timestamp, self.debug)
        hakrawler_process = Hakrawler("temp", self.config_path, self.timestamp, self.debug)
        waybackurls_process = Waybackurls("temp", self.config_path, self.timestamp, self.debug)
        gau_process = Gau("temp", self.config_path, self.timestamp, self.debug)
        katana_process = Katana("temp", self.config_path, self.timestamp, self.debug)
        params_tool_objs = {
            "blackwidow": blackwidow_process,
            "gospider": gospider_process,
            "paramspider": paramspider_process,
            "hakrawler": hakrawler_process,
            "waybackurls": waybackurls_process,
            "gau": gau_process,
            "katana": katana_process
        }

        ## Init Params Logging and params summary pd
        params_logging = Logging(self.target, self.config_path, self.timestamp, "params")
        params_logging_target_dir = params_logging.get_target_logs_dir()
        # print(params_logging_target_dir)
        params_probe_schema = {
            "subdomain": "object",
            "urls": "int64",
            "get_params": "int64",
            "post_params": "int64",
            "linkfinder": "int64",
            "javascript":"int64"
        }
        params_probe_log_pd = pd.DataFrame(columns=params_probe_schema.keys()).astype(params_probe_schema)
        processes = []
        for tool_name in params_tool_objs: 
            processes.append(functools.partial(params_tool_objs[tool_name].run_probe))


        for sub in subdomain_re_matches[0:2]: # REMOVE THE RANGE AFTER TESTING IN MAIN SCRIPT     
            print(f"[Information] Scan URLs and paramters at {sub}")
            for tool_name in params_tool_objs:
                params_tool_objs[tool_name].set_subdomain_targer(sub)
            pool = Pool(processes=len(params_tool_objs))
            res = pool.map(smap, processes)
            pool.close()
            pool.join()
            if self.debug:
                print(res)

            params_merged_log_path_name = merge_the_params_output_logs(res, params_logging_target_dir, sub, self.timestamp, self.debug)
            params_merged_log_path_name_list = params_merged_log_path_name.split("/")
            self.params_merged_log_path = "/".join(params_merged_log_path_name_list[:-1])
            params_sum_dict = count_web_crawling_output(params_merged_log_path_name, sub)
            # print(params_sum_dict)
            temp_row_pd = pd.DataFrame([params_sum_dict])
            params_probe_log_pd = pd.concat([params_probe_log_pd, temp_row_pd], ignore_index=True)

        params_probe_log_pd = params_probe_log_pd.sort_values(by=['get_params', 'post_params', 'urls'], ascending=False)
        # print(params_probe_log_pd)
        # SHOULD DO: Delete the subdomains with 0 links maybe
        self.params_probe_pd_log_path_name = f"{params_logging_target_dir}/params_probe{self.timestamp}.csv"
        params_probe_log_pd.to_csv(self.params_probe_pd_log_path_name, index=False)
        if not self.debug:
            rm_cmd = f"rm -rf {self.params_temp_path}/"
            prep_rm_cmd = prepare_command(rm_cmd)
            rm_sub_proc = subprocess.run(prep_rm_cmd)
            if rm_sub_proc.returncode != 0:
                print(f"[ERROR] Error during running this command {rm_cmd}")
                return f"Command: {self.command}\n[ERROR] Error during running this command {rm_cmd}"
            else:
                print(f"[PROCESS] Remove the param tools output logs after merging completed!")
        print(f"[Process] URLs and Parameters Discovery completed!")
        urls_and_params_output = f"Command: {self.command}\nURLs and parameters summary record: {self.params_probe_pd_log_path_name}\nURLs and parameters log path: {self.params_merged_log_path}"
        return urls_and_params_output

    def get_params_merged_log_path(self):
        return self.params_merged_log_path
    
    def get_params_probe_pd_log_path_name(self):
        return self.params_probe_pd_log_path_name
