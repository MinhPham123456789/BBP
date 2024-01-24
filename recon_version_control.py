import os
import subprocess
from recon_utils import *

class VersionControl:
    def __init__(self, config_path, target_logs_dir, new_log_name, log_type="main", DEBUG=False):
        self.target_logs_dir = target_logs_dir
        self.version_logs_dir = f"{self.target_logs_dir}/version_comparison"
        self.new_log_name = new_log_name
        self.config_path = config_path
        self.log_type = log_type
        self.command = get_command(self.config_path, "diff")
        self.debug = DEBUG
        self.check_version_logs_dir_existence()
        self.previous_log_name = self.get_previous_log_name()

    def check_version_logs_dir_existence(self):
        if not os.path.exists(self.version_logs_dir):
            os.makedirs(self.version_logs_dir)

    def get_previous_log_name(self):
        path = self.target_logs_dir
        if self.log_type == "main":
            return self.sub_get_previous_log_name(".xml")
        else:
            if "validate" in self.log_type:
                return self.sub_get_previous_log_name(".subs.brute", "gobuster_subdomain_validated")
            else:
                return self.sub_get_previous_log_name(".subs", "gobuster_subdomain_brute")
                
    def sub_get_previous_log_name(self, log_extension, pattern=None):
        files = [f"{self.target_logs_dir}/{file}" for file in os.listdir(self.target_logs_dir) if (file.lower().endswith(log_extension))]
        if pattern is not None:
            subdomains_files = [i for i in files if pattern in i]
            files = subdomains_files
        if len(files) <= 1:
            return ""
        files.sort(key=os.path.getmtime, reverse=True)
        return files[1]

    # def compare_version_obsolete(self):
    #     if self.debug:
    #         print(f"previous_log_name: {self.previous_log_name}")
    #     if len(self.previous_log_name) != 0:
    #         with open(f"{self.previous_log_name}", 'r') as pl:
    #             previous_log = pl.readlines()
    #             previous_log = previous_log[1:] # Remove 1st line with timestamp triggering wrong alert
    #         with open(f"{self.target_logs_dir}/{self.new_log_name}", 'r') as nl:
    #             new_log = nl.readlines()
    #             new_log = new_log[1:] # Remove 1st line with timestamp triggering wrong alert
    #         compare_result = []
    #         for line in difflib.unified_diff(previous_log, new_log, fromfile=self.previous_log_name, tofile=f"{self.target_logs_dir}/{self.new_log_name}", lineterm='', n=0):
    #             compare_result.append(line)
    #         compare_result = "\n".join(compare_result)
    #         if self.debug:
    #             print(compare_result)
    #         self.save_version_log(compare_result)

    def compare_version_main(self, pl_name, nl_name, version_log_name):
        cmd = replace_place_holder(self.command, "NEW_LOG", nl_name)
        cmd = replace_place_holder(cmd, "PREV_LOG", pl_name)
        cmd = replace_place_holder(cmd, "OUTPUT_LOG", version_log_name)
        if self.debug:
            print(f"Version control command: {cmd}")
        cmd = prepare_command(cmd)
        sub_proc = subprocess.run(cmd)
        if sub_proc.returncode == 0:
            print(f"Version control log saved to {self.version_logs_dir}/{version_log_name}")
        else:
            raise ExecutionError(f"Something went wrong with this version control command {cmd}")
            print(f"Error during execution\n{self.version_logs_dir}/{version_log_name} may not exist or empty")
        
    def compare_version_subdomain(self, pl_name, nl_name, version_log_name):
        sorted_pl = f"{self.version_logs_dir}/sorted_{pl_name.split('/')[-1]}"
        sort_proc_1 = os.system(f"sort {pl_name} > {sorted_pl}")
        if sort_proc_1 != 0:
            print(f"[ERROR] The sort 1 pl does not work, recon_version_control.py")
        sorted_nl = f"{self.version_logs_dir}/sorted_{nl_name.split('/')[-1]}"
        sort_proc_2 = os.system(f"sort {nl_name} > {sorted_nl}")
        if sort_proc_2 != 0:
            print(f"[ERROR] The sort 2 nl does not work, recon_version_control.py")
        cmd = replace_place_holder(self.command, "NEW_LOG", sorted_nl)
        cmd = replace_place_holder(cmd, "PREV_LOG", sorted_pl)
        cmd = replace_place_holder(cmd, "OUTPUT_LOG", version_log_name)
        if self.debug:
            print(f"Version control command: {cmd}")
        cmd = prepare_command(cmd)
        sub_proc = subprocess.run(cmd)
        if sub_proc.returncode == 0:
            print(f"Version control log saved to {self.version_logs_dir}/{version_log_name}")
            clean_proc = os.system(f"rm {sorted_nl} {sorted_pl}")
            if clean_proc != 0:
                print("[ERROR] Deleting sorted logs is not working, recon_version_control.py")
        else:
            raise ExecutionError(f"Something went wrong with this version control command {cmd}")
            print(f"Error during execution\n{self.version_logs_dir}/{version_log_name} may not exist or empty")
        
    def compare_version(self):
        # Get version log path with name
        if len(self.previous_log_name) == 0:
            return
        pl_name, nl_name, version_log_name = self.process_logs_name()
        if self.log_type == "main":
            self.compare_version_main(pl_name, nl_name, version_log_name)
        else:
            self.compare_version_subdomain(pl_name, nl_name, version_log_name)

    def process_logs_name(self):
        # print(self.new_log_name)
        if self.log_type == "main":
            pl_name = self.previous_log_name
            pl_temp = self.previous_log_name.split("/")[-1].split(".")[0]
            nl_name = f"{self.target_logs_dir}/{self.new_log_name}"
            nl_temp = self.new_log_name.split(".")[0]
            version_log_name = f"{self.version_logs_dir}/{pl_temp}_VS_{nl_temp}.html"
        else:
            if "validate" in self.log_type:
                pl_name = self.previous_log_name
                pl_temp = self.previous_log_name.split("/")[-1].split(".")[0].split("gobuster_subdomain_validated_merged_")[1]
                nl_name = self.new_log_name
                nl_temp = self.new_log_name.split("/")[-1].split(".")[0].split("gobuster_subdomain_validated_merged_")[1]
                version_log_name = f"{self.version_logs_dir}/gobuster_subdomain_validated_merged_{pl_temp}_VS_{nl_temp}.html"
            else:
                pl_name = self.previous_log_name
                pl_temp = self.previous_log_name.split("/")[-1].split(".")[0].split("gobuster_subdomain_brute_")[1]
                nl_name = self.new_log_name
                nl_temp = self.new_log_name.split("/")[-1].split(".")[0].split("gobuster_subdomain_brute_")[1]
                version_log_name = f"{self.version_logs_dir}/gobuster_subdomain_brute_{pl_temp}_VS_{nl_temp}.html"
        return pl_name, nl_name, version_log_name
