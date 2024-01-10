import shlex
import os
from recon_exceptions import *
from recon_utils import *
from datetime import datetime

class Chaos:
    """
    This class initiates an object to carry out chaos tool inside python
    """
    def __init__(self, target, command_config_path, debug=False):
        self.target = target
        self.tool = "chaos"
        self.command_config_path = command_config_path
        self.command = get_command(self.command_config_path, self.tool)
        self.command = replace_target(self.command, self.target)
        self.timeout = 10
        self.output = ""
        self.debug = debug

        # Set up the tool log path
        log_base = get_env_values(self.command_config_path, "log", "base_path")
        timestamp = datetime.today().strftime('%Y_%m_%dT%H_%M_%S')
        self.tool_log_name = f"{self.tool}_{timestamp}.subs"
        subdomain_tools_log_path = get_env_values(self.command_config_path, "log", "subdomain_tools_log_path")
        self.tool_log_path = f"{log_base}/{self.target}/{subdomain_tools_log_path}/{self.tool_log_name}"
        self.command = f"{self.command} > {self.tool_log_path}"

    def run_command(self):
        if check_command_existence(self.tool):
            cmd = self.command
            print(cmd)
            sub_proc = os.system(cmd)
            if sub_proc == 0:
                return f"Command: {self.command}\nChaos log path: {self.tool_log_path}\n Chaos log name: {self.tool_log_name}\n"
            else:
                raise ExecutionError("Something wnet wrong with this Chaos tool")
                return f"Error during execution\n{self.tool_log_path} may not exist or empty"
        else:
            raise NotInstalledError()