import shlex
import subprocess
from recon_exceptions import *
from recon_utils import *
from datetime import datetime

class Chaos:
    """
    This class initiates an object to carry out chaos tool inside python
    """
    def __init__(self, target, command_config_path, timestamp, debug=False):
        self.target = target
        self.tool = "chaos"
        self.command_config_path = command_config_path
        self.command = get_command(self.command_config_path, self.tool)
        self.command = replace_target(self.command, self.target)
        self.timeout = 10
        self.output = ""
        self.timestamp = timestamp
        self.debug = debug

        # Set up the tool log path
        log_base = get_env_values(self.command_config_path, "log", "base_path")
        self.tool_log_name = f"{self.tool}_{self.timestamp}.subs"
        subdomain_tools_log_path = get_env_values(self.command_config_path, "log", "subdomain_tools_log_path")
        self.tool_log_path = f"{log_base}/{self.target}/{subdomain_tools_log_path}/{self.tool_log_name}"
        self.command = f"{self.command} -o {self.tool_log_path}"

    def run_command(self):
        if check_command_existence(self.tool):
            cmd = prepare_command(self.command)
            if self.debug:
                print(self.command)
            sub_proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            if sub_proc.returncode == 0:
                print(f"[Process]{self.tool} completed!")
                return f"Command: {self.command}\nChaos log path: {self.tool_log_path}\n Chaos log name: {self.tool_log_name}\n"
            else:
                raise ExecutionError("Something went wrong with this Chaos tool")
                return f"Error during execution\n{self.tool_log_path} may not exist or empty"
        else:
            raise NotInstalledError()