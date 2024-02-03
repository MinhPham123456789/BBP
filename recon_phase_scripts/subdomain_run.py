import shlex
import os
import subprocess
import configparser
from multiprocessing import Pool
import functools
from xml.etree import ElementTree as ET
from lxml import etree
import re

from recon_exceptions import *
from recon_utils import *
from recon_logging import Logging
from recon_version_control import VersionControl
from tools_base.subdomain.snrublist3r_run import Snrublist3er
from tools_base.subdomain.chaos_run import Chaos
from tools_base.subdomain.httpx_run import Httpx
from tools_base.subdomain.gobuster_subdomain_run import GobusterSubdomain
from tools_base.subdomain.domaintrail_run import Domaintrail

ordered_subdomain_wordlists = [
    "deepmagic.com-prefixes-top500.txt",
    "subdomains-top1million-5000.txt",   
    "dns-Jhaddix.txt",
    "combined_subdomains.txt",
    "subdomains-top1million-20000.txt",
    "subdomains-top1million-110000.txt",
    "bug-bounty-program-subdomains-trickest-inventory.txt",   
    "fierce-hostlist.txt",
    "sortedcombined-knock-dnsrecon-fierce-reconng.txt",
    "deepmagic.com-prefixes-top50000.txt",
    "2m-subdomains.txt",
    "namelist.txt",  
    "italian-subdomains.txt",
    "tlds.txt",
    "n0kovo_subdomains.txt",
    "subdomains-spanish.txt",
    "bitquark-subdomains-top100000.txt",
    "shubs-stackoverflow.txt",
    "shubs-subdomains.txt",
]

class SubdomainScanner:
    """
    This class initiates an object to merge subdomain wordlists using bash commands inside python
    """
    def __init__(self, target, command_config_path, timestamp, number_of_wordlists=1, debug=False):
        """
        The current plan is
        Change the tools and commands to list because this class will involve the usage of multiple tools to get the last result
        And potentially log the tools result separately or in the same log
        How to return the results
            Answer: a list of long strings, each string => each commands
        """
        self.target = target
        self.command_config_path = command_config_path
        self.subdomain_wordlists_path = get_env_values(self.command_config_path, "temp", "subdomain_wordlists_path")
        self.subdomain_temp_wordlists_path = get_env_values(self.command_config_path, "temp", "subdomain_temp_path")
        self.timeout = 100
        self.timestamp = timestamp
        self.debug = debug
        self.number_of_wordlists = number_of_wordlists
        self.command = "Subdomain Discovery Commands"

        # Merge command
        merge_command = get_command(self.command_config_path, "subdomain_merge")
        merge_command = replace_place_holder(merge_command, "SUBDOMAIN_WORDLISTS_PATH", self.subdomain_wordlists_path)
        merged_wordlist_0_name = get_env_values(self.command_config_path, "temp", "subdomain_temp_0_merged_wordlist")
        merged_wordlist_1_name = get_env_values(self.command_config_path, "temp", "subdomain_temp_1_merged_wordlist")
        self.merged_subdomain_wordlist = f"{self.subdomain_temp_wordlists_path}/{merged_wordlist_0_name}"
        self.merged_subdomain_wordlist1 = f"{self.subdomain_temp_wordlists_path}/{merged_wordlist_1_name}"
        merge_command = replace_place_holder(merge_command, "SUBDOMAIN_MERGE_WORDLIST", self.merged_subdomain_wordlist)
        merge_command = f"{merge_command}; wc -l {self.merged_subdomain_wordlist}"

        self.tools_commands_dict = {
            "subdomains_merge": merge_command,
        }
        
    def run_command(self, tool_name):
        if check_command_existence(tool_name):
            cmd = prepare_command(self.tools_commands_dict[tool_name])
            sub_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                output, errs = sub_proc.communicate()
            except Exception as e:
                sub_proc.kill()
                raise (e)
            else:
                if 0 != sub_proc.returncode:
                    raise ExecutionError('Error during command: "' + ' '.join(cmd) + '"\n\n' + errs.decode('utf8'))

                # Response is bytes so decode the output and return
                clean_output = output.decode('utf8').strip()
                self.output = f"Command: {tool_name}\n{clean_output}"
                print(f"[Process]{tool_name} completed!\n{self.output}")
                return self.output
        else:
            raise NotInstalledError()

    def build_subdomain_wordlists(self):
        if not os.path.exists(self.subdomain_temp_wordlists_path):
            os.makedirs(self.subdomain_temp_wordlists_path)
        if self.debug:
            print(f"Merged subdomain wordlist command: {self.tools_commands_dict['subdomains_merge']}")
        self.run_command("subdomains_merge")
        for index in range(0, len(ordered_subdomain_wordlists)):
            # Sort the wordlist in the list
            cmd0 = f"sort {self.subdomain_wordlists_path}/{ordered_subdomain_wordlists[index]} | uniq > {self.subdomain_wordlists_path}/sorted_{ordered_subdomain_wordlists[index]}"
            cmd0 = prepare_command(cmd0)
            sub_proc = subprocess.Popen(cmd0, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                output, errs = sub_proc.communicate()
            except Exception as e:
                sub_proc.kill()
                raise (e)
            else:
                if 0 != sub_proc.returncode:
                    raise ExecutionError('Error during command: "' + ' '.join(cmd0) + '"\n\n' + errs.decode('utf8'))

                # Response is bytes so decode the output and return
                # clean_output = output.decode('utf8').strip()
                # output = f"Command: {cmd1}\n{clean_output}"
                # if self.debug:
                #     print(output)

            # Get same to the new wordlist
            cmd1 = f"comm -12 {self.merged_subdomain_wordlist} {self.subdomain_wordlists_path}/sorted_{ordered_subdomain_wordlists[index]} | uniq > {self.subdomain_temp_wordlists_path}/{index:03}_{ordered_subdomain_wordlists[index]}"
            cmd1 = prepare_command(cmd1)
            # print(cmd1)
            sub_proc = subprocess.Popen(cmd1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                output, errs = sub_proc.communicate()
            except Exception as e:
                sub_proc.kill()
                raise (e)
            else:
                if 0 != sub_proc.returncode:
                    raise ExecutionError('Error during command: "' + ' '.join(cmd1) + '"\n\n' + errs.decode('utf8'))

                # Response is bytes so decode the output and return
                # clean_output = output.decode('utf8').strip()
                # output = f"Command: {cmd1}\n{clean_output}"
                # if self.debug:
                #     print(output)
            
            # Get difference to the merged wordlist
            cmd2 = f"comm -23 {self.merged_subdomain_wordlist} {self.subdomain_wordlists_path}/sorted_{ordered_subdomain_wordlists[index]} | uniq > {self.merged_subdomain_wordlist1} && cp {self.merged_subdomain_wordlist1} {self.merged_subdomain_wordlist}"
            # The command above is necessary because the shell command cannot overwrite a file with new content, it just wipe out the whole file at least tested in python
            cmd2 = prepare_command(cmd2)
            sub_proc = subprocess.Popen(cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                output, errs = sub_proc.communicate()
            except Exception as e:
                sub_proc.kill()
                raise (e)
            else:
                if 0 != sub_proc.returncode:
                    raise ExecutionError('Error during command: "' + ' '.join(cmd2) + '"\n\n' + errs.decode('utf8'))

                print(f"[Process] Build wordlist {index:03}_{ordered_subdomain_wordlists[index]} completed!")
                # Response is bytes so decode the output and return
                # clean_output = output.decode('utf8').strip()
                # output = f"Command: {cmd1}\n{clean_output}"
                # if self.debug:
                #     print(output)
        os.system(f"rm {self.subdomain_wordlists_path}/sorted_*")
        print(f"[Process]Rebuild the subdomain wordlists in {self.subdomain_temp_wordlists_path} completed!")

    def run_subdomain_discovery(self):
        """
        Idea: 
        + a dict to store all tools instance and then run them in
        multiprocess pool then save them to log in order, pass the
        output dictionary to the save_subdomain_tools_output_log()
        + another method to clean, merge, and sort all the discovered
        subdomains by all the tools then put them in a big list string
        as output to be saved into the main ReconLog

        """
        tools_object_dictionary = {}
        commands_dictionary = {}
        # Initiating subdomain logging directory
        self.subdomain_logging = Logging(self.target, self.command_config_path, self.timestamp, "subdomain")

        # Snrublist3r
        snrublist3r_process = Snrublist3er(self.target, self.command_config_path, self.timestamp, self.debug)
        tools_object_dictionary['snrublist3r'] = snrublist3r_process
        commands_dictionary['snrublist3r'] = snrublist3r_process.command

        # Chaos
        chaos_process = Chaos(self.target, self.command_config_path, self.timestamp, self.debug)
        tools_object_dictionary['chaos'] = chaos_process
        commands_dictionary['chaos'] = chaos_process.command

        # DomainTrail
        domaintrail_process = Domaintrail(self.target, self.command_config_path, self.timestamp, self.debug)
        tools_object_dictionary['domaintrail'] = domaintrail_process
        commands_dictionary['domaintrail'] = domaintrail_process.command

        # GobusterSubdomain
        gobuster_subdomain_process = GobusterSubdomain(self.target, self.command_config_path, self.timestamp, self.number_of_wordlists, self.debug)
        tools_object_dictionary['gobuster_subdomain'] = gobuster_subdomain_process
        commands_dictionary['gobuster_subdomain'] = gobuster_subdomain_process.command

        processes = []
        for p in list(tools_object_dictionary.values()):
            processes.append(functools.partial(p.run_command))

        pool = Pool(processes=len(tools_object_dictionary))
        res = pool.map(smap, processes)
        pool.close()
        pool.join()
        if self.debug:
            print(res)

        # Build the output dictionary
        exclude_tool_output = ["gobuster_subdomain"]
        tools_outputs_dict = {}
        tools_log_path_dict = {}
        for output_string in res:
            for tool in list(commands_dictionary.keys()):
                if commands_dictionary[tool] in output_string:
                    tools_outputs_dict[tool] = output_string
                    regex_tool_log = re.search(r".*log path: (.*)\.subs", output_string)
                    tool_output_log_path = ""
                    if tool not in exclude_tool_output and regex_tool_log:
                        tool_output_log_path = regex_tool_log.group(1)
                        tool_output_log_path = f"{tool_output_log_path}.subs"
                        tools_log_path_dict[tool] = tool_output_log_path
                    # tools_outputs_dict[tool] = f"{tools_outputs_dict[tool]}\nLog path: {tools_object_dictionary[tool].tool_log_path}"
                    # tools_outputs_dict[tool] = f"{tools_outputs_dict[tool]}\nLog name: {tools_object_dictionary[tool].tool_log_name}"
                    break

        if self.debug:
            print(f"Subdomain tools outputs dict:\n{tools_outputs_dict}")
        # Save the subdomain tools logs
        merge_brute_subdomains_log_name = self.merge_subdomain_tools_output(tools_log_path_dict)
        # tools_outputs_dict["httpx"] = httpx_output
        gobuster_validation_output = gobuster_subdomain_process.run_validation(merge_brute_subdomains_log_name)
        tools_outputs_dict['gobuster_subdomain'] = f"{tools_outputs_dict['gobuster_subdomain']}\n{gobuster_validation_output}"
        subdomain_log_file_path = self.save_subdomain_tools_output_log(tools_outputs_dict, commands_dictionary)
        
        print("[Process] Subdomain Discovery completed!")
        subdomain_discovery_output = f"Command: {self.command}\nDiscovered and validated subdomains list:\n{tools_outputs_dict['gobuster_subdomain']}"
        subdomain_discovery_output = f"{subdomain_discovery_output}\n\nSubdomain Discovery log: {subdomain_log_file_path}\n"
        
        # Version control subdomain brute
        brute_version_control = VersionControl(self.command_config_path, self.subdomain_logging.get_target_logs_dir(), gobuster_subdomain_process.tool_log_path, "subdomain_sorted_brute", True)
        brute_version_control.compare_version()
        # Version control subdomain validate
        gobuster_validate_log_path = re.search(r"log path: (.*?)\n", gobuster_validation_output).group(1)
        validate_version_control = VersionControl(self.command_config_path, self.subdomain_logging.get_target_logs_dir(), gobuster_validate_log_path, "subdomain_sorted_validate", True)
        validate_version_control.compare_version()
        
        return subdomain_discovery_output


    def save_subdomain_tools_output_log(self, tools_outputs_dict, commands_dictionary):
        for tool_name in tools_outputs_dict:
            try:
                self.subdomain_logging.add_tool_log(tool_name, commands_dictionary[tool_name], tools_outputs_dict[tool_name])
            except KeyError:
                print(f"tools_object_dictionary KeyError with key '{tool_name}'")
            except Exception as e:
                print(f"[Unknown error] message: {e}")

        # Save the subdomain tools log
        subdomain_log_file_path = self.subdomain_logging.save_log()
        print(f"Subdomain tools' outputs are saved to {subdomain_log_file_path}")
        return subdomain_log_file_path

    def merge_subdomain_tools_output(self, tools_log_path_dict):
        # Merge the clean output, sort, unique, and save to the main log
        cmd = "sort"
        log_base = get_env_values(self.command_config_path, "log", "base_path")
        subdomain_tools_log_path = get_env_values(self.command_config_path, "log", "subdomain_tools_log_path")
        tools_log_name = f"{log_base}/{self.target}/{subdomain_tools_log_path}/merged"
        for key in tools_log_path_dict:
            tools_log_name = f"{tools_log_name}_{key}"
            cmd = f"{cmd} {tools_log_path_dict[key]}"
        tools_log_name = f"{tools_log_name}_{self.timestamp}.subs"
        cmd1 = f"{cmd} | uniq > {tools_log_name}"
        sub_proc = os.system(cmd1)
        if sub_proc == 0:
            print(f"Merge subdomains from online db completed!")
        else:
            raise ExecutionError("Something went wrong with merging subdomains from online db tool")
        
        cmd2 = f"{cmd} | uniq | sed 's/.{self.target}//g' > {tools_log_name}.brute"
        sub_proc = os.system(cmd2)
        if sub_proc == 0:
            print(f"Merge BRUTE subdomains from online db completed!")
        else:
            raise ExecutionError("Something went wrong with merging BRUTE subdomains from online db tool")
        
        # httpx is very slow on validating the DNS
        # httpx_process = Httpx(self.target, self.command_config_path, self.debug)
        # httpx_log_output = httpx_process.run_command(tools_log_name)
        return f"{tools_log_name}.brute"
        

def smap(f):
    """
    This method is utilised by multiprocess pool
    """
    return f()