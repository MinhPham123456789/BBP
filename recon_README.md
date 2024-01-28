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