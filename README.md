# FailStats Client
 Client that processes fail2ban logs and sends to [failstats.net](https://failstats.net) for aggregation and processing

 # OS Support:
 - Confirmed:
    - Ubuntu
    - Centos
    - Raspbian
 - Expected to work on:
    - Debian
    - RHEL

# Requirements:
- fail2ban
- Python3
- pytz (can be installed via pip)
- tzlocal

# Usage:
 - Put failstats.py into any appropriate folder, where the user has permission to read fail2ban logs
    - For example; ```~/fail/```
 - Setup a crontab to run it every hour/day/week as appropriate for your load-case for example:
   - ``` 18 * * * * cd ~/fail/ && python3 failstats.py  ```
   - Pick a random time if possible, as this spreads out the load on the server

# Created files:
 This will create three files:
- data.json.gz
    - This is the file that gets uploaded to failstats.net with all the ban information
- failstats.conf
    - Stores the following information:
        - Device UUID - Allows device statistics to be calculated
        - Last runtime - Sets the datetime to parse fail2ban logs from
- failstats.log
    - Logs the output of the upload API if an error occurs - usually just a temporary error