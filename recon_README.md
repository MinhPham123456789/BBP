# Should plan to work on
+ Should turn the tag labelling shell script into a config var
+ rather than retype the script's path

# Manual check
+ Reverse WHOIS: using the WHOIS result
+ Write and run a script to get all the ip addresses of a domain: using the NSLOOKUP result (CIDR, Organization)

# Subdomain scan
+ Have a separate subdomain tools output log for each target
+ Cannot run simultaneously with other tools because subprocess cannot initiate more children under it
+ Run it after information gathering

# Add/remove new tool main recon work flow process
+ Add or remove the process in main recon script
+ Add or remove the tool keywork in the reconfig

# Add/remove new tool in subdomain recon script
+ Add or remove the process in the run_subdomain_discovery() function in subdomain_run.py

# Remove the range when not running in DEBUG mode
+ The range in the subdomain loop in the urls_and_params_run.py script, the function run_urls_and_params_discovery()

# Notes
## Watchout the EXIT CODE of the last command in the commands change in config commands
+ grep has a slightly different exit code status
## End a command with grep (learnt through paramspider)
+ grep match exit code == 0, no match == 1, other errors >= 2
