import os, re, gzip, pytz, tzlocal, json, requests, uuid, sys
from datetime import datetime


regex = re.compile(r"(\d+-\d+-\d+ \d+:\d+:\d+,\d+)\sfail2ban.actions\W+.*\WBan (.*)", re.IGNORECASE)
logfiles = [f for f in os.listdir("/var/log/") if re.match(r"fail2ban", f)]

# Checks log rotation method
if any("-" in log for log in logfiles):
    # Log filenames have rotation date appended to end - centos?
    logfiles.sort(reverse=True)

    # Moves current logfile back to start
    logfiles.insert(0, logfiles.pop())
else:
    # Log filenames have integer appended - last rotated is 1
    logfiles.sort()

# Stores the parsed data
data = []

# Works out local timezone
localTZ = tzlocal.get_localzone()

# Checks for datetime of last run
if os.path.exists("failstats.conf"):
    with open("failstats.conf", "r") as f:
        conf = str(f.read()).strip().split(";")
        lastrun = datetime.strptime(conf[0], "%Y-%m-%d %H:%M:%S %Z%z")
        id = str(conf[1])
else:
    lastrun = datetime.strptime("1900-01-01 00:00:00 UTC+0000", "%Y-%m-%d %H:%M:%S %Z%z")
    id = str(uuid.uuid4())

for file in logfiles:
    if file[-3:] == ".gz":
        # Use gzip library to open
        log = gzip.open("/var/log/"+file, "rt")
    else:
        log = open("/var/log/"+file)

    skipfiles = False
    # Checks log in reverse and ends when lastrun is reached to prevent duplicates

    for match in reversed(list(regex.finditer(log.read()))):
        utc = localTZ.localize(datetime.strptime(match.group(1)[:-4], "%Y-%m-%d %H:%M:%S"), is_dst=True).astimezone(pytz.UTC)

        if utc < lastrun:
            skipfiles = True
            break
        data.append([utc.strftime("%Y-%m-%d %H:%M:%S %Z%z"), match.group(2)])

    if skipfiles:
        break

# Only submits if there is data
if len(data) > 0:
    with gzip.open("data.json.gz", "wb") as j:
        j.write(json.dumps(data).encode("utf-8"))

    f = open('data.json.gz','rb')

    url = "https://failstats.net/api/"
    files = {'data': f}
    r = requests.post(url, files=files, data={"id":id})
    f.close()

    if b'1' != r.content:
        os.remove("data.json.gz")
        with open("failstats.log", "a") as f:
            f.write(str(r.content))
            f.close()
    else:
        lastrun = data[0][0]

        with open("failstats.conf", 'w') as f:
            f.write(lastrun + ";" + id)
            f.close()

