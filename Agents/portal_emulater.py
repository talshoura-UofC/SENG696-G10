#%% Use Case 1
# User Login
import subprocess
import os
import json


proc = subprocess.Popen(['python3', 'UI_Agent.py',  '-c 1', '-u sAli@domain.com', '-p somePass'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
out = proc.communicate()
if proc.poll() == 1:
    output = json.loads(out[0].decode("utf-8")) # output here is an object
    print("Exit Code:", proc.poll(), "\nData: ", out)
else:
    print("Exit Code:", proc.poll(), "\nData: ", out[0].decode("utf-8"))

#%% Use Case 2
# User Registration
import subprocess
import os

# python3 UI_Agent.py -c 2 -u Ali@domain.com -p somePass -f Ali -l Dehagi -a "Calgary, Alberta" -m 0501234567

proc = subprocess.Popen(['python3', 'UI_Agent.py',  
    '-c 2', 
    '-u Ali@domain.ca', 
    '-p somePass',
    '-f Ali',
    '-l Dehagi',
    # '-a "Calgary, Alberta"',
    '-m 123456789'
], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
out = proc.communicate()
print("Exit Code:", proc.poll(), "\nData: ", out[0].decode("utf-8"))



# %%  Use Case 3
# Fetching Appointments
import subprocess
import os
import json

proc = subprocess.Popen(['python3', 'UI_Agent.py',  '-c 3', '-d 1'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
out = proc.communicate()
output = json.loads(out[0].decode("utf-8")) # output here is an object 
print("Exit Code:", proc.poll(), "\nData: ", json.dumps(output, indent=4, default=str))


# %% Use Case 4
# ALlocating an appointment
import subprocess
import os

proc = subprocess.Popen(
    ['python3', 'UI_Agent.py',  '-c 4', 
    '-u Tariq.AlShoura@ucalgary.ca', '-o 13', '-t 4'], 
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
out = proc.communicate()
print("Exit Code:", proc.poll(), "Data: ", out[0].decode("utf-8"))

# %%
