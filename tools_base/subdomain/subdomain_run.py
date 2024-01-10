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
from .snrublist3r_run import Snrublist3er
from .chaos_run import Chaos

ordered_subdomain_wordlists = [
    "bug-bounty-program-subdomains-trickest-inventory.txt",
    "subdomains-top1million-5000.txt",
    "subdomains-top1million-20000.txt",
    "subdomains-top1million-110000.txt",
    "deepmagic.com-prefixes-top500.txt",
    "combined_subdomains.txt",
    "fierce-hostlist.txt",
    "sortedcombined-knock-dnsrecon-fierce-reconng.txt",
    "deepmagic.com-prefixes-top50000.txt",
    "2m-subdomains.txt",
    "namelist.txt",
    "dns-Jhaddix.txt",
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
    def __init__(self, target, command_config_path, debug=False):
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
        self.debug = debug

        # Merge command
        merge_command = get_command(self.command_config_path, "subdomain_merge")
        merge_command = replace_place_holder(merge_command, "SUBDOMAIN_WORDLISTS_PATH", self.subdomain_wordlists_path)
        merged_wordlist_0_name = get_env_values(self.command_config_path, "temp", "subdomain_temp_0_merged_wordlist")
        merged_wordlist_1_name = get_env_values(self.command_config_path, "temp", "subdomain_temp_1_merged_wordlist")
        self.merged_subdomain_wordlist = f"{self.subdomain_temp_wordlists_path}/{merged_wordlist_0_name}"
        self.merged_subdomain_wordlist1 = f"{self.subdomain_temp_wordlists_path}/{merged_wordlist_1_name}"
        merge_command = replace_place_holder(merge_command, "SUBDOMAIN_MERGE_WORDLIST", self.merged_subdomain_wordlist)

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
                print(f"[Process]{tool_name} completed!")
                if self.debug:
                    print(self.output)
                return self.output
        else:
            raise NotInstalledError()

    def build_subdomain_wordlists(self):
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

        # # Snrublist3r
        snrublist3r_process = Snrublist3er(self.target, self.command_config_path, self.debug)
        tools_object_dictionary['snrublist3r'] = snrublist3r_process
        commands_dictionary['snrublist3r'] = snrublist3r_process.command

        # Chaos
        chaos_process = Chaos(self.target, self.command_config_path, self.debug)
        tools_object_dictionary['chaos'] = chaos_process
        commands_dictionary['chaos'] = chaos_process.command

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
        tools_outputs_dict = {}
        for output_string in res:
            for tool in list(commands_dictionary.keys()):
                if commands_dictionary[tool] in output_string:
                    tools_outputs_dict[tool] = output_string
                    # tools_outputs_dict[tool] = f"{tools_outputs_dict[tool]}\nLog path: {tools_object_dictionary[tool].tool_log_path}"
                    # tools_outputs_dict[tool] = f"{tools_outputs_dict[tool]}\nLog name: {tools_object_dictionary[tool].tool_log_name}"
                    break

        if self.debug:
            print(f"Subdomain tools outputs dict:\n{tools_outputs_dict}")
        # Save the subdomain tools logs
        subdomain_log_file_path = self.save_subdomain_tools_output_log(tools_outputs_dict, commands_dictionary)
        self.filter_subdomain_tools_output(subdomain_log_file_path)

    def save_subdomain_tools_output_log(self, tools_outputs_dict, commands_dictionary):
        subdomain_logging = Logging(self.target, self.command_config_path, "subdomain")
        for tool_name in tools_outputs_dict:
            try:
                subdomain_logging.add_tool_log(tool_name, commands_dictionary[tool_name], tools_outputs_dict[tool_name])
            except KeyError:
                print(f"tools_object_dictionary KeyError with key '{tool_name}'")
            except Exception as e:
                print(f"[Unknown error] message: {e}")

        # Save the subdomain tools log
        subdomain_log_file_path = subdomain_logging.save_log()
        print(f"Subdomain tools' outputs are saved to {subdomain_log_file_path}")
        return subdomain_log_file_path

    def filter_subdomain_tools_output(self, subdomains_tool_output):
        # Read the log
        parser = etree.XMLParser(recover=True,encoding='utf-8')
        tree = ET.parse(subdomains_tool_output, parser=parser)
        root = tree.getroot()
        output_nodes_list = [] # This is for debugging
        clean_output_list = []
        subdomain_re_pattern = f"[\*\.a-z0-9\-]+\.{self.target}"
        for child in root:
            if "_output" in child.tag:
                output_nodes_list.append(child.tag)
                # if self.debug:
                #     print(output_nodes_list)
                if "subdomain_tools_log" in child.text and "log path" in child.text:
                    regex_tool_log = re.search(r".*log path: (.*)\.subs", child.text)
                    tool_output_log_path = ""
                    if regex_tool_log:
                        tool_output_log_path = regex_tool_log.group(1)
                        tool_output_log_path = f"{tool_output_log_path}.subs"
                    # print(tool_output_log_path)
                    with open(tool_output_log_path, 'r') as text:
                        tool_output = text.read()
                    clean_output_list.append(filter_tool_output(tool_output, subdomain_re_pattern))
                else:
                    clean_output_list.append(filter_tool_output(tool_output, subdomain_re_pattern))

        # Merge the clean output, sort, unique, and save to the main log
        uniq_clean_output_list = sorted(set(clean_output_list))
        

def smap(f):
    """
    This method is utilised by multiprocess pool
    """
    return f()