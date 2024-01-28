import shlex
import os
import configparser

from recon_utils import *

class Waybackurls:
    """
    This class initiates an object to carry out waybackurls tool inside python
    """
    def __init__(self, target, command_config_path, timestamp, debug=False):
        self.subdomain_target = target
        self.tool = "waybackurls"
        self.command_config_path = command_config_path
        self.command = get_command(self.command_config_path, self.tool)
        self.timeout = 10
        self.output = ""
        self.timestamp = timestamp
        self.debug = debug
        self.params_temp_path = get_env_values(self.command_config_path, "temp", "params_temp_path")

    def set_subdomain_targer(self, subdomain_target):
        self.subdomain_target = subdomain_target

    def run_probe(self):
        if check_command_existence(self.tool):
            # Set temp log path
            temp_log_name = f"{self.tool}_{self.subdomain_target}_{self.timestamp}.log"
            temp_log_path = f"{self.params_temp_path}/{temp_log_name}"
            
            # Check temp log existence
            if os.path.exists(temp_log_path) and not self.debug:
                os.system(f"rm -rf {temp_log_path}") # exists then remove
            cmd = self.command
            cmd = replace_target(cmd, self.subdomain_target)
            cmd = f"{cmd} > {temp_log_path}"
            if self.debug:
                print(cmd)
            # cmd = prepare_command(cmd)
            sub_proc = os.system(cmd)
            if sub_proc == 0:
                print(f"[Process]{self.tool} completed!")
                output_count_dict = count_web_crawling_output(temp_log_path, self.subdomain_target, self.debug)
                output_count_dict['tool'] = self.tool
                output_count_dict['command'] = cmd
                if not self.debug:
                    os.system(f"rm -rf {temp_log_path}")
                return output_count_dict

            else:
                raise ExecutionError(f"Something went wrong with this {self.tool} tool")
                return f"Error during execution\n{self.tool_log_path} may not exist or empty"
        else:
            raise NotInstalledError()