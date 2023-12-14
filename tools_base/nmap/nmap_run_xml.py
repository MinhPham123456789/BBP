import shlex
import os
import subprocess
import asyncio
from .nmap_utils import get_nmap_path, get_nmap_version, print_nmap_xml
from .nmap_exceptions import *
from recon_exceptions import *
from .nmap_parser import *

class Nmap:
    """
    This class initiates an object to carry out nmap commands inside python
    """
    def __init__(self, target, command_config_path):
        self.nmaptool = get_nmap_path()
        self.target = target    # domain name or ip address
        self.xml_output_arg = "-oX -"   # output in xml structure in the stdout (terminal output)
        self.xml_root = None
        self.stdout = asyncio.subprocess.PIPE
        self.stderr = asyncio.subprocess.PIPE

    def get_command(self, command_config_path):
        config = configparser.ConfigParser()
        config.read(command_config_path)
        self.command = config["commands"]["nmap"]

    def prepare_command(self, command):
        command_template = f"{self.nmaptool} {self.xml_output_arg} {self.target} {command}"
        shlex_command = shlex.split(command_template)
        return shlex_command
    
    async def async_run_command(self, command, timeout=None):
        if (os.path.exists(self.nmaptool)):
            cmd = f"{self.nmaptool} {self.xml_output_arg} {self.target} {command}" # self.prepare_command(command)    
            print(cmd)       
            process = await asyncio.create_subprocess_shell(cmd,stdout=self.stdout,stderr=self.stderr)
            
            try:
                data, stderr = await process.communicate()
            except Exception as e:
                raise (e)
            else:
                if 0 != process.returncode:
                    raise NmapExecutionError('Error during command: "' + ' '.join(cmd) + '"\n\n' + stderr.decode('utf8'))

                # Response is bytes so decode the output and return
                return data.decode('utf8').strip()
        else:
            raise NmapNotInstalledError()

    def run_command_xml(self, command, timeout=None):
        if (os.path.exists(self.nmaptool)):
            cmd = self.prepare_command(command)   
            sub_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                output, errs = sub_proc.communicate(timeout=timeout)
            except Exception as e:
                sub_proc.kill()
                raise (e)
            else:
                if 0 != sub_proc.returncode:
                    raise NmapExecutionError('Error during command: "' + ' '.join(cmd) + '"\n\n' + errs.decode('utf8'))

                # Response is bytes so decode the output and return
                return output.decode('utf8').strip()
        else:
            raise NmapNotInstalledError()

    def run_command():
        pass
    

# debug_obj = Nmap("10.10.1.10")
# print(get_nmap_version())
# xml_output_string = debug_obj.run_command("-sV --script=vuln")
# # out = asyncio.run(debug_obj.async_run_command("-sV"))

# print("Scan done")

# # Construct xml data
# hosts_data_list, sections_list = construct_nmap_data_to_be_parsed(xml_output_string)
# for index in range(0, len(hosts_data_list)):
#     print_nmap_xml(hosts_data_list[index], sections_list[index])
