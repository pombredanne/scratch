

p = subprocess.Popen(["find", "-name", "*.mine", "-print0"])
for filepath in p.read.split("\0"):
    cmd = ["mv", filepath, filepath[:-len(".mine")]]