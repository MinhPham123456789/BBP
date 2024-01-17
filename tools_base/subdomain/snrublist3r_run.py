import shlex
import os
from recon_exceptions import *
from recon_utils import *
from datetime import datetime

class Snrublist3er:
    """
    This class initiates an object to carry out snrublist3r tool inside python
    """
    def __init__(self, target, command_config_path, timestamp, debug=False):
        self.target = target
        self.tool = "snrublist3r"
        self.command_config_path = command_config_path
        self.command = get_command(self.command_config_path, self.tool)
        self.command = replace_target(self.command, self.target)
        self.timeout = 10
        self.output = ""
        self.timestamp = timestamp
        self.debug = debug

        # Set up the tool log path, due to snrublist3r does not pipeline in shell
        log_base = get_env_values(self.command_config_path, "log", "base_path")
        self.tool_log_name = f"{self.tool}_{self.timestamp}.subs"
        subdomain_tools_log_path = get_env_values(self.command_config_path, "log", "subdomain_tools_log_path")
        self.tool_log_path = f"{log_base}/{self.target}/{subdomain_tools_log_path}/{self.tool_log_name}"
        self.command = f"{self.command} -o {self.tool_log_path}"

    def run_command(self):
        if check_command_existence(self.tool):
            cmd = self.command
            if self.debug:
                print(cmd)
            sub_proc = os.system(cmd)
            if sub_proc == 0:
                print(f"[Process]{self.tool} completed!")
                return f"Command: {self.command}\n{self.tool} log path: {self.tool_log_path}\n{self.tool} log name: {self.tool_log_name}\n"
            else:
                raise ExecutionError("Something went wrong with this snrublist3r tool")
                return f"Error during execution\n{self.tool_log_path} may not exist or empty"
        else:
            raise NotInstalledError()