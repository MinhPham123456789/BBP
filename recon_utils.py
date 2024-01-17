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
external_tools = ["snrublist3r", "chaos", "httpx", "blackwidow"]

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
            raise ExecutionError("Error in which command: " + errs.decode('utf8'))
    
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

def count_web_crawling_output(output_log_path, debug=False):
    output_count_dict = {}
    # URLs
    cmd = f"grep -E '(\[url\]|\[robots\]) .*' {output_log_path} | grep -v '?' | wc -l"
    cmd = prepare_command(cmd)
    sub_proc = subprocess.run(cmd, capture_output=True)
    if sub_proc.returncode == 0:
        if debug:
            output_count_dict['urls'] = [sub_proc.stdout.decode("utf-8"), cmd]
        else:
            output_count_dict['urls'] = [sub_proc.stdout.decode("utf-8")]
    else:
        raise ExecutionError(f"Something went wrong with this command {cmd}")
        output_count_dict['urls'] = f"Error during execution\n Command: {cmd}"

    # GET Parameters
    cmd = f"grep -E '(\[dyn_url\]|\[url\]|\[robots\]) .*[?].*' {output_log_path}| wc -l"
    cmd = prepare_command(cmd)
    sub_proc = subprocess.run(cmd, capture_output=True)
    if sub_proc.returncode == 0:
        if debug:
            output_count_dict['get_params'] = [sub_proc.stdout.decode("utf-8"), cmd]
        else:
            output_count_dict['get_params'] = [sub_proc.stdout.decode("utf-8")]
    else:
        raise ExecutionError(f"Something went wrong with this command {cmd}")
        output_count_dict['get_params'] = f"Error during execution\n Command: {cmd}"
    
    # POST form Parameters
    cmd = f"grep -E '(\[form\]) .*' {output_log_path}| wc -l"
    cmd = prepare_command(cmd)
    sub_proc = subprocess.run(cmd, capture_output=True)
    if sub_proc.returncode == 0:
        if debug:
            output_count_dict['post_params'] = [sub_proc.stdout.decode("utf-8"), cmd]
        else:
            output_count_dict['post_params'] = [sub_proc.stdout.decode("utf-8")]
    else:
        raise ExecutionError(f"Something went wrong with this command {cmd}")
        output_count_dict['post_params'] = f"Error during execution\n Command: {cmd}"
    
    # Linkfinder
    cmd = f"grep -E '(\[linkfinder\]) .*' {output_log_path}| wc -l"
    cmd = prepare_command(cmd)
    sub_proc = subprocess.run(cmd, capture_output=True)
    if sub_proc.returncode == 0:
        if debug:
            output_count_dict['linkfinder'] = [sub_proc.stdout.decode("utf-8"), cmd]
        else:
            output_count_dict['linkfinder'] = [sub_proc.stdout.decode("utf-8")]
    else:
        raise ExecutionError(f"Something went wrong with this command {cmd}")
        output_count_dict['linkfinder'] = f"Error during execution\n Command: {cmd}"

    # Javascript
    cmd = f"grep -E '(\[javascript\]) .*' {output_log_path}| wc -l"
    cmd = prepare_command(cmd)
    sub_proc = subprocess.run(cmd, capture_output=True)
    if sub_proc.returncode == 0:
        if debug:
            output_count_dict['javascript'] = [sub_proc.stdout.decode("utf-8"), cmd]
        else:
            output_count_dict['javascript'] = [sub_proc.stdout.decode("utf-8")]
    else:
        raise ExecutionError(f"Something went wrong with this command {cmd}")
        output_count_dict['javascript'] = f"Error during execution\n Command: {cmd}"

    return output_count_dict