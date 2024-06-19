import shlex
import configparser
import subprocess
import re
import os

from recon_utils import *

class NucleiTechAnalysis:
    """
    This class initiates an object to carry out nuclei tool inside python
    to detect target's technologies
    """
    def __init__(self, target, command_config_path, timestamp, debug=False):
        self.subdomain_target = target
        self.tool = "nuclei_tech_analysis"
        self.command_config_path = command_config_path
        self.command = get_command(self.command_config_path, self.tool)
        self.command = replace_target(self.command, self.subdomain_target)
        self.timeout = 10
        self.output = ""
        self.timestamp = timestamp
        self.debug = debug
        self.params_temp_path = get_env_values(self.command_config_path, "temp", "params_temp_path")

# Note use the subprocess.run() with output capture
    def run_command(self):
        if check_command_existence(self.tool):
            cmd = prepare_command(self.command)
            # print(cmd)
            sub_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                output, errs = sub_proc.communicate()
                # print(output)
            except Exception as e:
                sub_proc.kill()
                raise (e)
            else:
                if 0 != sub_proc.returncode:
                    raise ExecutionError('Error during command: "' + ' '.join(cmd) + '"\n\n' + errs.decode('utf8'))
                # Response is bytes so decode the output and return
                clean_output = output.decode('utf8').strip()
                if clean_output == '':
                    self.output = f"Command: {self.command}\nNo technology was detected"
                else:
                    self.output = f"Command: {self.command}\n{clean_output}"
                extra_output = self.run_extra_analysis(clean_output)
                self.output = f"{self.output}\n##\n{extra_output}"
                print(f"[Process]{self.tool} completed!")
                if self.debug:
                    print(self.output)
                return self.output
        else:
            raise NotInstalledError()
        
    def run_extra_analysis(self, technology_output):
        if technology_output != '' and  re.match(r'^\[.*?\:.*?\].*', technology_output):
            extra_cmd = get_command(self.command_config_path, "nuclei_tech_analysis_extra")
            extra_cmd = replace_target(extra_cmd, self.subdomain_target)
            detected_techs = re.findall(r'^\[.*?:(.*?)\] ', technology_output)
            tech_tags = ','.join(detected_techs)
            extra_cmd = replace_place_holder(extra_cmd, 'TECH_TAGS', tech_tags)
            cmd = prepare_command(extra_cmd)
            sub_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                output, errs = sub_proc.communicate()
            except Exception as e:
                sub_proc.kill()
                raise (e)
            else:
                if 0 != sub_proc.returncode:
                    raise ExecutionError('Error during command: "' + ' '.join(cmd) + '"\n\n' + errs.decode('utf8'))
                clean_output = output.decode('utf8').strip()
                return_output = f"Extra Command: {extra_cmd}\n{clean_output}"
                return return_output
        else:
            return "No technology detected to run analysis"
 