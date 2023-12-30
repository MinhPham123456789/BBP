import shlex
import os
import subprocess
import configparser
from recon_exceptions import *
from recon_utils import *

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
        self.timeout = 100
        self.debug = debug

        # Merge command
        merge_command = get_command(self.command_config_path, "subdomain_merge")
        merge_command = replace_place_holder(merge_command, "SUBDOMAIN_WORDLISTS_PATH", self.subdomain_wordlists_path)
        merged_subdomain_wordlist = get_env_values(self.command_config_path, "temp", "subdomain_temp_merged_wordlist")
        merge_command = replace_place_holder(merge_command, "SUBDOMAIN_MERGE_WORDLIST", merged_subdomain_wordlist)
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
                self.output = f"Command: {self.command}\n{clean_output}"
                print(f"[Process]{tool_name} completed!")
                if self.debug:
                    print(self.output)
                return self.output
        else:
            raise NotInstalledError()