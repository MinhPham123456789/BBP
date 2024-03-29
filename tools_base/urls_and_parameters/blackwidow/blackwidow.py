#!/usr/bin/python3
# blackwidow by @xer0dayz - Last Updated 20200717
# https://sn1persecurity.com
#

from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests, sys, os, atexit, optparse
from http import cookies
import re

requests.packages.urllib3.disable_warnings()

OKBLUE = "\033[94m"
OKRED = "\033[91m"
OKGREEN = "\033[92m"
OKORANGE = "\033[93m"
COLOR1 = "\033[95m"
COLOR2 = "\033[96m"
RESET = "\x1b[0m"

def parse_action_form(form_node):
    form_relative_path = form_node.get("action")
    if form_relative_path is None:
        return None, None
    inputs_list = form_node.findall("input")
    form_parameters_string = ""
    for input_item in inputs_list:
        if input_item.get("type").lower() == "file":
            form_parameters_string = f"{form_parameters_string}, name: {input_item.get('name')}&id: {input_item.get('id')} FILE UPLOAD"
        else:
            form_parameters_string = f"{form_parameters_string}, name: {input_item.get('name')}&id: {input_item.get('id')}"
    return form_relative_path, form_parameters_string

def readlinks(url,domain, verbose):
    try:
        if len(cookies) > 2:
            headers = {"Cookie": cookies}
            r = requests.get(url, headers=headers, verify=False)
        else:
            r = requests.get(url, verify=False)

        data = r.text
        # print(data)
        soup = BeautifulSoup(data, "lxml")
        parsed_uri = urlparse(url)
        # print(soup.findall("a").toString())
        domain = "{uri.netloc}".format(uri=parsed_uri)
        domain = domain.split(":")[0]
    except Exception as ex:
        print(ex)

    urls = open("/tmp/" + domain + "_" + port + "-urls.txt", "w+")
    urls_saved = open(save_dir + domain + "_" + port + "-urls.txt", "a")
    forms_saved = open(save_dir + domain + "_" + port + "-forms.txt", "a")
    dynamic_saved = open(save_dir + domain + "_" + port + "-dynamic.txt", "a")
    emails_saved = open(save_dir + domain + "_" + port + "-emails.txt", "a")
    phones_saved = open(save_dir + domain + "_" + port + "-phones.txt", "a")
    subdomains_saved = open(save_dir + domain + "_" + port + "-subdomains.txt", "a")

    # print("")
    # print(
    #     OKGREEN
    #     + "=================================================================================================="
    #     + RESET
    # )
    # print(OKGREEN + url)
    # print(
    #     OKGREEN
    #     + "=================================================================================================="
    #     + RESET
    # )
    for form in soup.find_all("form"):
        # print (OKBLUE + "[+] Extracting form values...")
        # print ("__________________________________________________________________________________________________" + OKORANGE)
        # print (form)
        # print (OKBLUE + "__________________________________________________________________________________________________")
        # print (RESET)
        form_relative_path, form_parameters_string = parse_action_form(form)
        if form_relative_path is not None and form_parameters_string is not None:
            form_url = f"{url}/{form_relative_path}"
            form_url = re.sub(r"([a-zA-Z0-9]+)//([a-zA-Z0-9]+)", r"\1/\2", form_url) # replacing "//" to "/" and avoid "://"
            form_url = f"{form_url} with parameters {form_parameters_string}"
            forms_saved.write("[form] " + form_url + "\n")

    # PARSE LINKS
    for link in soup.find_all("a"):
        # IF LINK IS NOT NULL
        if link.get("href") is not None:
            parsed_uri = urlparse(link.get("href"))
            linkdomain = "{uri.netloc}".format(uri=parsed_uri)
            if (domain != linkdomain) and (linkdomain != "") and (domain in linkdomain):
                print(COLOR1 + "[+] Sub-domain found! " + linkdomain + " " + RESET)
                subdomains_saved.write("[subdomain] " + linkdomain + "\n")
            # IF LINK STARTS WITH HTTP
            if re.match(r"(?:http.*|https.*|ftp.*)", link.get("href")):
                # SAME ORIGIN
                if domain in link.get("href"):
                    # IF URL IS DYNAMIC
                    if "?" in link.get("href"):
                        if verbose:
                            print(
                                OKRED
                                + "[+] Dynamic URL found! "
                                + link.get("href")
                                + " "
                                + RESET
                            )
                        urls.write(link.get("href") + "\n")
                        # urls_saved.write("[url] " + link.get("href") + "\n")
                        dynamic_saved.write("[dyn_url] " + link.get("href") + "\n")
                    else:
                        if verbose:
                            print(link.get("href"))
                        urls.write(link.get("href") + "\n")
                        urls_saved.write("[url] " + link.get("href") + "\n")
                # EXTERNAL LINK FOUND
                # else:
                # IF URL IS DYNAMIC
                # if "?" in link.get('href'):
                # print (COLOR2 + "[+] External Dynamic URL found! " + link.get('href') + " " + RESET)
                # else:
                # print (COLOR2 + "[i] External link found! " + link.get('href') + " " + RESET)
            # IF URL IS DYNAMIC
            elif "?" in link.get("href"):
                if verbose:
                    print(
                        OKRED
                        + "[+] Dynamic URL found! "
                        + url
                        + "/"
                        + link.get("href")
                        + " "
                        + RESET
                    )
                output_url = url + "/" + link.get("href")
                output_url = re.sub(r"([a-zA-Z0-9]+)//([a-zA-Z0-9]+)", r"\1/\2", output_url)
                urls.write(output_url + "\n")
                urls_saved.write("[url] " + output_url + "\n")
                dynamic_saved.write("[dyn_url] " + output_url + "\n")
            # DOM BASED LINK
            # elif link.get('href')[:1] == "#":
            # print (OKBLUE + "[i] DOM based link found! " + link.get('href') + " " + RESET)
            # TELEPHONE
            elif link.get("href")[:4] == "tel:":
                s = link.get("href")
                phonenum = s.split(":")[1]
                if verbose:
                    print(OKORANGE + "[i] Telephone # found! " + phonenum + " " + RESET)
                phones_saved.write("[phone] " + phonenum + "\n")
            # EMAIL
            elif link.get("href")[:7] == "mailto:":
                s = link.get("href")
                email = s.split(":")[1]
                if verbose:
                    print(OKORANGE + "[i] Email found! " + email + " " + RESET)
                emails_saved.write("[email] " + email + "\n")
            # ELSE NORMAL LINK FOUND
            else:
                if verbose:
                    print(url + "/" + link.get("href"))
                output_url = url + "/" + link.get("href")
                output_url = re.sub(r"([a-zA-Z0-9]+)//([a-zA-Z0-9]+)", r"\1/\2", output_url)
                urls.write(output_url + "\n")
                urls_saved.write("[url] " + output_url + "\n")
    if verbose:
        print(
            OKGREEN
            + "__________________________________________________________________________________________________"
            + RESET
        )


def readfile(domain, verbose):
    filename = "/tmp/" + domain + "_" + port + "-urls.txt"
    with open(filename) as f:
        urls = f.read().splitlines()
        for url in urls:
            try:
                readlinks(url, domain, verbose)
            except Exception as ex:
                print(ex)


def logo():
    version = "1.3"
    print(OKRED + "")
    print(OKRED + "")
    print(OKRED + "                _.._")
    print(OKRED + "              .'    '.")
    print(OKRED + "             /   __   \ ")
    print(OKRED + "          ,  |   ><   |  ,")
    print(OKRED + "         . \  \      /  / .")
    print(OKRED + "          \_'--`(  )'--'_/")
    print(OKRED + "            .--'/()'--.")
    print(OKRED + "@xer0dayz  /  /` '' `\  \ ")
    print(OKRED + "             |        |")
    print(OKRED + "              \      /")
    print(OKRED + "")
    print(RESET)
    print(OKORANGE + " + -- --=[ https://sn1persecurity.com" + RESET)
    print(OKORANGE + " + -- --=[ blackwidow v" + version + " by @xer0dayz " + RESET)
    print(RESET)


def exit_handler():
    os.system(
        "sort -u "
        + save_dir
        + domain
        + "_"
        + port
        + "-urls.txt > "
        + save_dir
        + domain
        + "_"
        + port
        + "-urls-sorted.txt 2>/dev/null"
    )
    os.system(
        "sort -u "
        + save_dir
        + domain
        + "_"
        + port
        + "-forms.txt > "
        + save_dir
        + domain
        + "_"
        + port
        + "-forms-sorted.txt 2>/dev/null"
    )
    os.system(
        "sort -u "
        + save_dir
        + domain
        + "_"
        + port
        + "-dynamic.txt > "
        + save_dir
        + domain
        + "_"
        + port
        + "-dynamic-sorted.txt 2>/dev/null"
    )
    os.system(
        "rm -f " + save_dir + domain + "_" + port + "-dynamic-unique.txt 2>/dev/null"
    )
    # os.system("touch " + save_dir + domain + "_" + port + "-dynamic-unique.txt")
    # os.system(
    #     "for a in `cat "
    #     + save_dir
    #     + domain
    #     + "_"
    #     + port
    #     + "-dynamic-sorted.txt | cut -d '?' -f2 | sort -u | cut -d '=' -f1 | sort -u`; do for b in `egrep $a "
    #     + save_dir
    #     + domain
    #     + "_"
    #     + port
    #     + "-dynamic.txt -m 1`; do echo $b >> "
    #     + save_dir
    #     + domain
    #     + "_"
    #     + port
    #     + "-dynamic-unique.txt; done; done;"
    # )
    os.system(
        "sort -u "
        + save_dir
        + domain
        + "_"
        + port
        + "-subdomains.txt > "
        + save_dir
        + domain
        + "_"
        + port
        + "-subdomains-sorted.txt 2>/dev/null"
    )
    os.system(
        "sort -u "
        + save_dir
        + domain
        + "_"
        + port
        + "-emails.txt > "
        + save_dir
        + domain
        + "_"
        + port
        + "-emails-sorted.txt 2>/dev/null"
    )
    os.system(
        "sort -u "
        + save_dir
        + domain
        + "_"
        + port
        + "-phones.txt > "
        + save_dir
        + domain
        + "_"
        + port
        + "-phones-sorted.txt 2>/dev/null"
    )

    if verbose:
        logo()
    # print(
    #     OKGREEN
    #     + "[+] URL's Discovered: \n"
    #     + save_dir
    #     + domain
    #     + "_"
    #     + port
    #     + "-urls-sorted.txt"
    #     + RESET
    # )
    # print(
    #     OKGREEN
    #     + "__________________________________________________________________________________________________"
    #     + RESET
    # )
    os.system("cat " + save_dir + domain + "_" + port + "-urls-sorted.txt")
    # print(RESET)
    # print(
    #     OKGREEN
    #     + "[+] Dynamic URL's Discovered: \n"
    #     + save_dir
    #     + domain
    #     + "_"
    #     + port
    #     + "-dynamic-sorted.txt"
    #     + RESET
    # )
    # print(
    #     OKGREEN
    #     + "__________________________________________________________________________________________________"
    #     + RESET
    # )
    os.system("cat " + save_dir + domain + "_" + port + "-dynamic-sorted.txt")
    # print(RESET)
    # print(
    #     OKGREEN
    #     + "[+] Form URL's Discovered: \n"
    #     + save_dir
    #     + domain
    #     + "_"
    #     + port
    #     + "-forms-sorted.txt"
    #     + RESET
    # )
    # print(
    #     OKGREEN
    #     + "__________________________________________________________________________________________________"
    #     + RESET
    # )
    os.system("cat " + save_dir + domain + "_" + port + "-forms-sorted.txt")
    # print(RESET)
    # print(
    #     OKGREEN
    #     + "[+] Unique Dynamic Parameters Discovered: \n"
    #     + save_dir
    #     + domain
    #     + "_"
    #     + port
    #     + "-dynamic-unique.txt"
    #     + RESET
    # )
    # print(
    #     OKGREEN
    #     + "__________________________________________________________________________________________________"
    #     + RESET
    # )
    # os.system("cat " + save_dir + domain + "_" + port + "-dynamic-unique.txt")
    # print(RESET)
    # print(
    #     OKGREEN
    #     + "[+] Sub-domains Discovered: \n"
    #     + save_dir
    #     + domain
    #     + "_"
    #     + port
    #     + "-subdomains-sorted.txt"
    #     + RESET
    # )
    # print(
    #     OKGREEN
    #     + "__________________________________________________________________________________________________"
    #     + RESET
    # )
    os.system("cat " + save_dir + domain + "_" + port + "-subdomains-sorted.txt")
    # print(RESET)
    # print(
    #     OKGREEN
    #     + "[+] Emails Discovered: \n"
    #     + save_dir
    #     + domain
    #     + "_"
    #     + port
    #     + "-emails-sorted.txt"
    #     + RESET
    # )
    # print(
    #     OKGREEN
    #     + "__________________________________________________________________________________________________"
    #     + RESET
    # )
    os.system("cat " + save_dir + domain + "_" + port + "-emails-sorted.txt")
    # print(RESET)
    # print(
    #     OKGREEN
    #     + "[+] Phones Discovered: \n"
    #     + save_dir
    #     + domain
    #     + "_"
    #     + port
    #     + "-phones-sorted.txt"
    #     + RESET
    # )
    # print(
    #     OKGREEN
    #     + "__________________________________________________________________________________________________"
    #     + RESET
    # )
    os.system("cat " + save_dir + domain + "_" + port + "-phones-sorted.txt")
    # print(RESET)
    # print(OKRED + "[+] Loot Saved To: \n" + save_dir + RESET)
    # print(
    #     OKRED
    #     + "__________________________________________________________________________________________________"
    #     + RESET
    # )
    # print(RESET)
    os.system("rm -f " + save_dir + domain + "_" + port + "-dynamic.txt")
    os.system("rm -f " + save_dir + domain + "_" + port + "-forms.txt")
    os.system("rm -f " + save_dir + domain + "_" + port + "-emails.txt")
    os.system("rm -f " + save_dir + domain + "_" + port + "-phones.txt")
    os.system("rm -f " + save_dir + domain + "_" + port + "-urls.txt")
    os.system("rm -f " + save_dir + domain + "_" + port + "-subdomains.txt")
    os.system("rm -f /tmp/" + domain + "_" + port + "-urls.txt 2> /dev/null")
    os.system(f"rm -rf {blackwidow_base_log_dir}*")

    if scan == "y":
        os.system(
            "for a in `cat "
            + save_dir
            + domain
            + "_"
            + port
            + "-dynamic-unique.txt`; do python3 /usr/bin/injectx.py -u $a; done;"
        )
    else:
        pass


# logo()
globalURL = "globalBadness"
if len(sys.argv) < 2:
    print("You need to specify a URL to scan. Use --help for all options.")
    sys.exit()
else:
    parser = optparse.OptionParser()
    parser.add_option(
        "-u", "--url", action="store", dest="url", help="Full URL to spider", default=""
    )

    parser.add_option(
        "-d",
        "--domain",
        action="store",
        dest="domain",
        help="Domain name to spider",
        default="",
    )

    parser.add_option(
        "-c",
        "--cookie",
        action="store",
        dest="cookie",
        help="Cookies to send",
        default="",
    )

    parser.add_option(
        "-l",
        "--level",
        action="store",
        dest="level",
        help="Level of depth to traverse",
        default="2",
    )

    parser.add_option(
        "-s",
        "--scan",
        action="store",
        dest="scan",
        help="Scan all dynamic URL's found",
        default="n",
    )

    parser.add_option(
        "-p",
        "--port",
        action="store",
        dest="port",
        help="Port for the URL",
        default="443",
    )

    parser.add_option(
        "-v",
        "--verbose",
        action="store",
        dest="verbose",
        help="Set verbose mode ON",
        default=0,
    )

    options, args = parser.parse_args()
    target = str(options.url)
    # global domain
    domain = str(options.domain)
    cookies = str(options.cookie)
    max_depth = str(options.level)
    scan = str(options.scan)
    port = str(options.port)
    verbose = options.verbose
    ans = scan
    level = 1

    # using a domain and a port or a URL?
    if ":" not in target:

        if len(str(target)) > 6:
            url = target + ":" + port  # big change here

        else:
            url = "https://" + str(domain) + ":" + port

        if len(str(domain)) > 4:
            target = "https://" + domain + ":" + port
        else:
            print(target)
            urlparse(target)
            parsed_uri = urlparse(target)
            domain = "{uri.netloc}".format(uri=parsed_uri)

    else:
        url = target
        globalURL = target
        parsed_uri = urlparse(target)
        domainWithPort = "{uri.netloc}".format(uri=parsed_uri)
        domain = domainWithPort.split(":")[0]
        if len(target.split(":")) > 2:
            portWithPossiblePath = target.split(":")[2]
            port = portWithPossiblePath.split("/")[0]
        else:
            port = port

    blackwidow_base_log_dir = "./tools_base/blackwidow/log/"
    save_dir = blackwidow_base_log_dir + domain + "_" + port + "/"
    os.system("mkdir -p " + save_dir + " 2>/dev/null")
    atexit.register(exit_handler)

    # FILE INIT
    urls_file = "/tmp/" + domain + "_" + port + "-urls.txt"
    urls_saved_file = save_dir + domain + "_" + port + "-urls.txt"
    forms_saved_file = save_dir + domain + "_" + port + "-forms.txt"
    subdomain_file = save_dir + domain + "_" + port + "-subdomains.txt"
    emails_file = save_dir + domain + "_" + port + "-emails.txt"
    phones_file = save_dir + domain + "_" + port + "-phones.txt"
    urls = open(urls_file, "w+")
    urls.close()
    urls_saved = open(urls_saved_file, "w+")
    urls_saved.close()
    forms_saved = open(forms_saved_file, "w+")
    forms_saved.close()
    subdomains = open(subdomain_file, "w+")
    subdomains.close()
    emails = open(emails_file, "w+")
    emails.close()
    phones = open(phones_file, "w+")
    phones.close()

    try:
        readlinks(url, domain, verbose)
    except Exception as ex:
        print(ex)

    while int(level) <= int(max_depth):
        level = level + 1
        if int(level) <= int(max_depth):
            try:
                readfile(domain, verbose)
            except Exception as ex:
                print(ex)
        else:
            break
