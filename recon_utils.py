import configparser
import shlex
import subprocess
import re
from recon_exceptions import *

def replace_target(command, target):
    return command.replace("TARGET_HERE", target)

def replace_place_holder(command, place_holder_pattern, value):
    return command.replace(place_holder_pattern, value)

def get_command(config_path, tool):
    config = configparser.ConfigParser()
    config.read(config_path)
    command = config["commands"][tool]
    return command

def get_env_values(config_path, env_section, env_variable_name):
    config = configparser.ConfigParser()
    config.read(config_path)
    command = config[env_section][env_variable_name]
    return command

def prepare_command(command):
    if "|" in command:
        return ['sh', '-c', command]
    else:
        shlex_command = shlex.split(command)
        return shlex_command

command_whitelist = ["subdomains_merge"]
external_tools = ["snrublist3r", "chaos", "httpx"]

def check_command_existence(tool):
    if tool in command_whitelist:
        return True
    if tool in external_tools:
        return True
    shlex_command = shlex.split(f"which {tool}")
    sub_proc = subprocess.Popen(shlex_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        output, errs = sub_proc.communicate(timeout=3)
    except Exception as e:
        sub_proc.kill()
        raise (e)
        return False
    else:
        if 0 != sub_proc.returncode:
            raise ExecutionError("Error in where command: " + errs.decode('utf8'))
    
    clean_output = output.decode('utf8').strip()
    if "not found" in clean_output:
        print(f"where {tool} command result: {clean_output}")
        return False
    else:
        return True

def filter_tool_output(output, pattern):
    # print(pattern)
    # print(output)
    matches_list = re.findall(pattern, output)
    return matches_list