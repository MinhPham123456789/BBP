import shlex
import subprocess
import sys

def get_nmap_path():
    """
    Returns the location path where nmap is installed
    by calling which nmap
    """
    os_type = sys.platform
    if os_type == 'win32':
        cmd = "where nmap"
    else:
        cmd = "which nmap"
    args = shlex.split(cmd)
    sub_proc = subprocess.Popen(args, stdout=subprocess.PIPE)

    try:
        output, errs = sub_proc.communicate(timeout=15)
    except Exception as e:
        print(e)
        sub_proc.kill()
    else:
        if os_type == 'win32':
            return output.decode('utf8').strip().replace("\\", "/")
        else:
            return output.decode('utf8').strip()

def get_nmap_version():
    nmap = get_nmap_path()
    cmd = nmap + " --version"

    args = shlex.split(cmd)
    sub_proc = subprocess.Popen(args, stdout=subprocess.PIPE)

    try:
        output, errs = sub_proc.communicate(timeout=15)
    except Exception as e:
        print(e)
        sub_proc.kill()
    else:
        return output.decode('utf8').strip()

def iterate_and_print_xml(data_dicts_list, start_sign, data_dicts_list_index):
    """
    This function iterates the data dictionaries list and print the data out
    Then it build up the sub dictionaries in recursive_print_list and
    recursive_sections_list to put them in recursive process
    :param data_dicts_list: A list storing the dictionaries that store data
    :param depth_start: The string mark starting new section/new line
    :return:
        recursive_print_list: A list storing the sub dictionaries
        recursive_sections_list: A list storing the sub dictionaries' name
    """
    for data_dict in data_dicts_list[data_dicts_list_index]:
        output_string = start_sign
        recursive_print_list = []  # This list is created to store the sub dictionaries
        recursive_sections_list = [] # This list stores the key of the sub dictionaries
        for key in data_dict.keys():
            if isinstance(data_dict[key], list):
                recursive_print_list.append(data_dict[key])
                recursive_sections_list.append(key.upper())
            else:
                output_string = f"{output_string} {key}:{data_dict[key]}"
        print(output_string)
    return recursive_print_list, recursive_sections_list

def print_nmap_xml(data_dicts_list: list, section_names: list, depth_start = None):
    """
    This function prints the xml output
    :param data_dicts_list: A list of lists of dictionary
    :param section_names: A list of section names
    :param depth_start: A new line starting sign
    :return:
        None
    """
    if depth_start is not None:
        if len(section_names) != len(data_dicts_list):
            print("The name list length is not equal to the data list")
            return None
        newline_space = "|  " * ((len(depth_start) - 1)//2)
        for index in range(0, len(data_dicts_list)):
            if data_dicts_list[index] is not None:
                print(f"{depth_start} {section_names[index]}:")
                # for data_dict in data_dicts_list[index]:
                #     if depth_start is None:
                #         output_string = "+"
                #     else:
                #         output_string = newline_space
                #     recursive_print_list = []  # This list is created to store the sub dictionaries
                #     recursive_sections_list = [] # This list stores the key of the sub dictionaries
                #     for key in data_dict.keys():
                #         if isinstance(data_dict[key], list):
                #             recursive_print_list.append(data_dict[key])
                #             recursive_sections_list.append(key.upper())
                #         else:
                #             output_string = f"{output_string} {key}:{data_dict[key]}"
                #     print(output_string)
                recursive_print_list, recursive_sections_list = iterate_and_print_xml(data_dicts_list, newline_space, index)
                print_nmap_xml(recursive_print_list, recursive_sections_list, f"  {depth_start}")
            else:
                print(f"{depth_start} {section_names[index]}: None")
    else:
        if len(section_names) != len(data_dicts_list):
            print("The name list length is not equal to the data list")
        else:
            depth_1_start_sign = "+"
            for index in range(0, len(section_names)):
                if len(data_dicts_list[index]) > 0:
                    print(section_names[index])
                    # for data_dict in data_dicts_list[index]:
                    #     if depth_start is None:
                    #         output_string = depth_1_start_sign
                    #     else:
                    #         output_string = depth_start
                    #     # print(data_dict)
                    #     recursive_print_list = []  # This list is created to store the sub dictionaries
                    #     recursive_sections_list = [] # This list stores the key of the sub dictionaries
                    #     for key in data_dict.keys():
                    #         if isinstance(data_dict[key], list):
                    #             recursive_print_list.append(data_dict[key])
                    #             recursive_sections_list.append(key.upper())
                    #         else:
                    #             output_string = f"{output_string} {key}:{data_dict[key]}"
                    #     print(output_string)
                    recursive_print_list, recursive_sections_list = iterate_and_print_xml(data_dicts_list, depth_1_start_sign, index)
                    print_nmap_xml(recursive_print_list, recursive_sections_list, "|_+")
                else:
                    print(f"{section_names[index]} NONE")
