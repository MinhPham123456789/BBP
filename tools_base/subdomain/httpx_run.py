import shlex
import subprocess
import os
from recon_exceptions import *
from recon_utils import *
from datetime import datetime

class Httpx:
    """
    This class initiates an object to carry out httpx commands inside python
    """
    def __init__(self, target, command_config_path, debug=False):
        self.target = target
        self.tool = "httpx"
        self.command_config_path = command_config_path
        self.command = get_command(self.command_config_path, self.tool)
        self.timeout = 10
        self.output = ""
        self.debug = debug

        # Set up the tool log path
        log_base = get_env_values(self.command_config_path, "log", "base_path")
        timestamp = datetime.today().strftime('%Y_%m_%dT%H_%M_%S')
        self.tool_log_name = f"{self.tool}_{timestamp}.subs"
        subdomain_tools_log_path = get_env_values(self.command_config_path, "log", "subdomain_tools_log_path")
        self.tool_log_path = f"{log_base}/{self.target}/{subdomain_tools_log_path}/{self.tool_log_name}"
        self.command = f"{self.command} -o {self.tool_log_path}"

    def run_command(self, target_log):
        if check_command_existence(self.tool):
            cmd =  self.command
            cmd = replace_target(cmd, target_log)
            if self.debug:
                print(cmd)
            # cmd = prepare_command(cmd)
            # sub_proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            cmd = f"{cmd} > /dev/null"
            sub_proc = os.system(cmd)
            if sub_proc == 0:
                print(f"[Process]{self.tool} completed!")
                if self.debug:
                    exp_cmd = f"wc -l {target_log}"
                    exp_cmd = prepare_command(exp_cmd)
                    exp_process = subprocess.run(exp_cmd, capture_output=True)
                    val_cmd = f"wc -l {self.tool_log_path}"
                    val_cmd = prepare_command(val_cmd)
                    validate_proc = subprocess.run(val_cmd, capture_output=True)
                    print(f"Expected lines: {exp_process.stdout}, Real lines: {validate_proc.stdout}")
                return f"Output from {target_log}\nCommand: {self.command}\n{self.tool} log path: {self.tool_log_path}\n{self.tool} log name: {self.tool_log_name}\n"
            else:
                raise ExecutionError(f"Output from {target_log}, something went wrong with this httpx tool")
                return f"Output from {target_log}\nError during execution\n{self.tool_log_path} may not exist or empty"
        else:
            raise NotInstalledError()