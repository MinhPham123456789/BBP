# BBP
(Under Development)
## Overview
This project aims to integrate external pentesting tools into a reconnaissance script. The script automatically runs the tools against the target. Then, it summarises and combines the output of many tools to provide a statistical overview of the target, which helps the testers analyse and navigate the target's weak points to launch more detailed tests so that the testers can save time from crawling large attack surfaces and increase productivity.

## Workflow of the script
+ Collect the general OSINT of the target
+ Actively scan the available services and open ports of the target (This will be rearrange in the workflow later on, the current version is a prototype)
+ Collect the subdomain records of the target's domain name
+ Collect the records of the URL links, parameters, javascripts of the subdomains/domains of the target

## Abilities
### Gather target's general OSINT
+ Use `whois` to get the target's information regarding domain name, IP address block, registered user, contact email, contact phone number and so on
+ Use `nslookup` get the DNS record and IP address, IP address block of the target's domain name

### Subdomain Enumeration
+ Use `chaos` to get records of subdomains of the target's domain name from the ProjectDiscovery database (https://github.com/projectdiscovery/chaos-client)
+ Use `snrublist3r` to get records of subdomains of the target's domain name from 15 different resources (https://github.com/b3n-j4m1n/snrublist3r)
+ Use `gobuster` to validate the collected subdomain records from the databases and brute force subdomains using wordlist (https://github.com/OJ/gobuster)

### Web crawling and parameter discovery
+ Use `blackwidow` to crawl the domains/subdomains of the target to extract the URL links, parameters, and javascript (https://github.com/1N3/BlackWidow) (note: this repo has a customised blackwidow` script)
+ Use `gospider` to crawl the domains/subdomains of the target to extract the URL links, parameters, and javascript (https://github.com/jaeles-project/gospider)
+ Use `paramspider` to get records of URL links, parameters, javascripts of the target from Wayback archives database (https://github.com/devanshbatham/ParamSpider)

### Active Scan
+ Use `nmap` to get an overview of the open services and ports of the target along with potential vulnerabilities.

## Dev Notes
+ Add suitable tools to scan for potential vulnerabilities based on parameters
+ Add `dotdotpwn` with your module to change the payload based on OS

## Subdomain wordlist sources
+ https://wordlists.assetnote.io/
+ https://github.com/danielmiessler/SecLists
