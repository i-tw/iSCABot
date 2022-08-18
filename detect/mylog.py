import os

def llog(fp, s):
    print(s, end="")
    fp.writelines(s)

