import shlex
import os
import subprocess
import configparser
from recon_exceptions import *
from recon_utils import *

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
        if self.debug:
            print(f"Merged subdomain wordlist: {merge_command}")

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
