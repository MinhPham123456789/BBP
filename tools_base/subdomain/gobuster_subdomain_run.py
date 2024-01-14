import shlex
import os
import subprocess
from recon_exceptions import *
from recon_utils import *
from datetime import datetime

class GobusterSubdomain:
    """
    This class initiates an object to carry out snrublist3r tool to brute force subdomains inside python
    """
    def __init__(self, target, command_config_path, number_of_wordlists=1, debug=False):
        self.target = target
        self.tool = "gobuster_subdomain"
        self.command_config_path = command_config_path
        self.command = get_command(self.command_config_path, self.tool)
        self.command = replace_target(self.command, self.target)
        self.original_command = self.command
        self.timeout = 10
        self.output = ""
        self.subdomain_temp_wordlists_path = get_env_values(self.command_config_path, "temp", "subdomain_temp_path")
        self.debug = debug
        self.number_of_wordlists = number_of_wordlists

        # Set up the tool log path
        log_base = get_env_values(self.command_config_path, "log", "base_path")
        timestamp = datetime.today().strftime('%Y_%m_%dT%H_%M_%S')
        self.tool_log_name = f"{self.tool}_{timestamp}.subs"
        subdomain_tools_log_path = get_env_values(self.command_config_path, "log", "subdomain_tools_log_path")
        self.tool_log_path = f"{log_base}/{self.target}/{subdomain_tools_log_path}/{self.tool_log_name}"
        self.command = f"{self.command} -o {self.tool_log_path}"

    def run_command(self):
        if check_command_existence(self.tool.split("_")[0]):
            # Get and sort the wordlists
            subdomain_wordlists = os.listdir(self.subdomain_temp_wordlists_path)
            subdomain_wordlists = sorted(subdomain_wordlists)          
            # Prepare cat them up
            prefix_cmd = "cat"
            for wl in subdomain_wordlists[:self.number_of_wordlists - 1]:
                prefix_cmd = f"{prefix_cmd} {self.subdomain_temp_wordlists_path}/{wl}"
            # if self.debug:
            #     prefix_cmd = "cat"
            #     for wl in subdomain_wordlists[1:3]:
            #         prefix_cmd = f"{prefix_cmd} {self.subdomain_temp_wordlists_path}/{wl}"

            self.command = f"{prefix_cmd} | {self.command} -w -"
            cmd = prepare_command(self.command)
            if self.debug:
                print(cmd)
                print(f"Available subdomain wordlists: {subdomain_wordlists}")
            sub_proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            if sub_proc.returncode == 0:
                print(f"[Process]{self.tool} completed!")
                return f"Command: {self.command}\n{self.tool} log path: {self.tool_log_path}\n{self.tool} log name: {self.tool_log_name}\n"
            else:
                raise ExecutionError(f"Something went wrong with this {self.tool} tool")
                return f"Error during execution\n{self.tool_log_path} may not exist or empty"
        else:
            raise NotInstalledError()

    def run_validation(self, brute_subdomain_log):
        cmd = self.original_command
        # Set up log path
        log_base = get_env_values(self.command_config_path, "log", "base_path")
        timestamp = datetime.today().strftime('%Y_%m_%dT%H_%M_%S')
        tool_log_name = f"{self.tool}_merged_{timestamp}.subs.brute"
        subdomain_tools_log_path = get_env_values(self.command_config_path, "log", "subdomain_tools_log_path")
        tool_log_path = f"{log_base}/{self.target}/{subdomain_tools_log_path}/{tool_log_name}"
        cmd = f"{cmd} -o {tool_log_path} -w {brute_subdomain_log}"

        # Run validation
        if check_command_existence(self.tool.split("_")[0]):       
            cmd = prepare_command(cmd)
            if self.debug:
                print(cmd)
                print(f"Available merged brute subdomains wordlist: {brute_subdomain_log}")
            sub_proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            if sub_proc.returncode == 0:
                print(f"[Process]{self.tool} validation subdomains completed!")
                return f"Command: {' '.join(cmd)}\n{self.tool} log path: {tool_log_path}\n{self.tool} log name: {tool_log_name}\n"
            else:
                raise ExecutionError(f"Something went wrong with this {self.tool} tool")
                return f"Error during execution\n{tool_log_path} may not exist or empty"
        else:
            raise NotInstalledError()