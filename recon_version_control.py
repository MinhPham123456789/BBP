import os
import subprocess
from recon_utils import *
import re

"""
The version control class using the vim -d (vim diff) capability to compare the log
and save the version control (comparison) as a website .html to be viewed easily
and provide more intuitive display

Currently there are 2 main version control comparison categories "display" and "sorted"
Then combined them with the purpose
Example:
    main_display: to have a version control displaying changes of unsorted main recon logs

There are 3 places requires the categories
get_previous_log_name()
compare_version()
process_log_name()

"""
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
        if "display" in self.log_type:
            return self.sub_get_previous_log_name(".xml")
        else: # sorted version
            if self.log_type == "main_sorted":
                return self.sub_get_previous_log_name(".xml")
            elif "subdomain" in self.log_type:
                if "validate" in self.log_type:
                    return self.sub_get_previous_log_name(".subs.brute", "gobuster_subdomain_validated")
                else:
                    return self.sub_get_previous_log_name(".subs", "gobuster_subdomain_brute")
            else:
                print(f"[ERROR] No suitable log type found {self.log_type}")
                return ""
        print("[ERROR] Cannot get the previous log name, highly because of the condition in function get_previous_log_name() in recon_version_control.py")
        return ""

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

    def compare_version_display(self, pl_name, nl_name, version_log_name):
        """
        This version comparison is for displaying because it is pretty to show
        """
        cmd = replace_place_holder(self.command, "NEW_LOG", nl_name)
        cmd = replace_place_holder(cmd, "PREV_LOG", pl_name)
        cmd = replace_place_holder(cmd, "OUTPUT_LOG", version_log_name)
        if self.debug:
            print(f"Version control command: {cmd}")
        cmd = prepare_command(cmd)
        sub_proc = subprocess.run(cmd)
        if sub_proc.returncode == 0:
            print(f"Version control log saved to {version_log_name}")
        else:
            raise ExecutionError(f"Something went wrong with this version control command {cmd}")
            print(f"Error during execution\n{version_log_name} may not exist or empty")
        
    def compare_version_sorted(self, pl_name, nl_name, version_log_name):
        """
        This version comparison is for helping vim diff to correct compare the differences between logs
        """
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
            print(f"Version control sorted log saved to {version_log_name}")
            clean_proc = os.system(f"rm {sorted_nl} {sorted_pl}")
            if clean_proc != 0:
                print("[ERROR] Deleting sorted logs is not working, recon_version_control.py")
        else:
            raise ExecutionError(f"Something went wrong with this version control command {cmd}")
            print(f"Error during execution\n{version_log_name} may not exist or empty")
        
    def compare_version(self):
        # Get version log path with name
        # print(f"[DEBUG] {self.previous_log_name}, {self.log_type}")
        if len(self.previous_log_name) == 0:
            return None
        pl_name, nl_name, version_log_name = self.process_logs_name()
        # print(f"[DEBUG] {pl_name}, {self.log_type}")
        if pl_name == "":
            return None
        # print(f"{pl_name}, {nl_name}, {version_log_name}, {self.log_type}")
        if "sorted" in self.log_type:
            self.compare_version_sorted(pl_name, nl_name, version_log_name)
        else:
            self.compare_version_display(pl_name, nl_name, version_log_name)
        return version_log_name

    def process_logs_name(self):
        # print(self.new_log_name)
        pl_name = ""
        nl_name = ""
        version_log_name = ""
        if "display" in self.log_type:
            if self.log_type == "main_display":
                pl_name = self.previous_log_name
                pl_temp = self.previous_log_name.split("/")[-1].split(".")[0]
                nl_name = f"{self.target_logs_dir}/{self.new_log_name}"
                nl_temp = self.new_log_name.split(".")[0]
                version_log_name = f"{self.version_logs_dir}/{pl_temp}_VS_{nl_temp}.html"
        elif "sorted" in self.log_type:
            if self.log_type == "main_sorted":
                pl_name = self.previous_log_name
                pl_temp = self.previous_log_name.split("/")[-1].split(".")[0]
                nl_name = f"{self.target_logs_dir}/{self.new_log_name}"
                nl_temp = self.new_log_name.split(".")[0]
                version_log_name = f"{self.version_logs_dir}/sorted_{pl_temp}_VS_{nl_temp}.html"
            if "subdomain" in self.log_type:
                if "validate" in self.log_type:
                    pl_name = self.previous_log_name
                    pl_temp = self.previous_log_name.split("/")[-1].split(".")[0].split("gobuster_subdomain_validated_merged_")[1]
                    nl_name = self.new_log_name
                    nl_temp = self.new_log_name.split("/")[-1].split(".")[0].split("gobuster_subdomain_validated_merged_")[1]
                    version_log_name = f"{self.version_logs_dir}/gobuster_subdomain_validated_merged_{pl_temp}_VS_{nl_temp}.html"
                else: # This means "subdomain brute" scenario
                    pl_name = self.previous_log_name
                    pl_temp = self.previous_log_name.split("/")[-1].split(".")[0].split("gobuster_subdomain_brute_")[1]
                    nl_name = self.new_log_name
                    nl_temp = self.new_log_name.split("/")[-1].split(".")[0].split("gobuster_subdomain_brute_")[1]
                    version_log_name = f"{self.version_logs_dir}/gobuster_subdomain_brute_{pl_temp}_VS_{nl_temp}.html"
        else:
            print("[ERROR] Not an available log type")
        return pl_name, nl_name, version_log_name


        # if self.log_type == "main" or self.log_type == "main_sorted":
        #     if "sorted" in self.log_type:
        #         pl_name = self.previous_log_name
        #         pl_temp = self.previous_log_name.split("/")[-1].split(".")[0]
        #         nl_name = f"{self.target_logs_dir}/{self.new_log_name}"
        #         nl_temp = self.new_log_name.split(".")[0]
        #         version_log_name = f"{self.version_logs_dir}/sorted_{pl_temp}_VS_{nl_temp}.html"
        #     else:
        #         pl_name = self.previous_log_name
        #         pl_temp = self.previous_log_name.split("/")[-1].split(".")[0]
        #         nl_name = f"{self.target_logs_dir}/{self.new_log_name}"
        #         nl_temp = self.new_log_name.split(".")[0]
        #         version_log_name = f"{self.version_logs_dir}/{pl_temp}_VS_{nl_temp}.html"
        # else:
        #     if "validate" in self.log_type:
        #         pl_name = self.previous_log_name
        #         pl_temp = self.previous_log_name.split("/")[-1].split(".")[0].split("gobuster_subdomain_validated_merged_")[1]
        #         nl_name = self.new_log_name
        #         nl_temp = self.new_log_name.split("/")[-1].split(".")[0].split("gobuster_subdomain_validated_merged_")[1]
        #         version_log_name = f"{self.version_logs_dir}/gobuster_subdomain_validated_merged_{pl_temp}_VS_{nl_temp}.html"
        #     else:
        #         pl_name = self.previous_log_name
        #         pl_temp = self.previous_log_name.split("/")[-1].split(".")[0].split("gobuster_subdomain_brute_")[1]
        #         nl_name = self.new_log_name
        #         nl_temp = self.new_log_name.split("/")[-1].split(".")[0].split("gobuster_subdomain_brute_")[1]
        #         version_log_name = f"{self.version_logs_dir}/gobuster_subdomain_brute_{pl_temp}_VS_{nl_temp}.html"
        # return pl_name, nl_name, version_log_name

    def send_noti(self, version_log_path_name):
        if version_log_path_name is None:
            print("No new version control log to scan for changes")
            return
        log_text = ""
        with open(version_log_path_name, 'r') as l:
            log_text = l.read()
        log_sections_list = log_text.split("<td>")
        # print(len(log_sections_list))
        scan_result_signal, scan_result_message = self.scan_for_critical_changes(log_sections_list[2])
        print(f"[DEBUG] Scan version control log result signal: {scan_result_signal}")
        print("[DEBUG] Scan version control log result message:")
        for message in scan_result_message:
            print(f"[Version control difference critical message] {message}")
        pass

    def scan_for_critical_changes(self, log_text):
        # Check for diffadd
        if re.search(r"span class\=\"DiffAdd\"", log_text):
            return True, ["New Adding"]

        # Check for diffdelete
        if re.search(r"span class\=\"DiffDelete\"", log_text):
            return True, ["New Deleting"]

        # Check for diffchange
        diff_change_list = re.findall(r'span (class\=\"DiffChange\".*?)\n', log_text)
        diff_text_list = re.findall(r'(.*?class\=\"DiffText\".*?)\n', log_text)
        diff_change_list = diff_change_list + diff_text_list
        if len(diff_change_list) > 0:
            return self.scan_for_critical_diff_change(diff_change_list)
        return False, []

    
    def scan_for_critical_diff_change(self, diff_change_list):
        diff_change_black_list_patterns = [
            'class="Identifier DiffChange">TimeStamp',
            'class="DiffChange">Command: cat ./temps/subdomain_temp',
            'class="DiffChange">Command: gobuster',
            'class="DiffChange">gobuster_subdomain log path:',
            'class="DiffChange">gobuster_subdomain log name:',
            'class="DiffChange">Subdomain Discovery log:',
            'class="DiffChange">URLs and parameters summary record:',
            'class="DiffChange">URLs and parameters log path:'
        ]
        # print(f"All changes: {diff_change_list}")
        new_change_list = []
        for i in range(0, len(diff_change_list)):
            for pattern in diff_change_black_list_patterns:
                new_signal = True
                if pattern in diff_change_list[i]:
                    new_signal = not True
                    break
            if new_signal:
                new_change_list.append(diff_change_list[i])
        # print(f"Real changes: {new_change_list}")
        if len(new_change_list) > 0:
            return True, new_change_list
        else:
            return not True, []

            
