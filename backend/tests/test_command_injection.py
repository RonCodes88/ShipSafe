import os

def cleanup(user_input):
    os.system("rm -rf /data/" + user_input)
