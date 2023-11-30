import subprocess

mystep = 2

obs_intent    = "CALIBRATE_BANDPASS#ON_SOURCE"
target_source = "J1924-2914"



# Use the "ls" get the visibilities in list
visibility = subprocess.run("ls *.ms.split.cal -d", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
visibility = visibility.stdout.decode()
visibility = visibility.split("\n")
visibility.pop()

step = 1
# Use the "mstransform" in CASA split out the target source out of the original MS
if mystep == step:
    for ms in visibility:
        obs_list = listobs(vis=ms)
        for key, value in obs_list.items():
            if key.startswith('field_'):
                if obs_list[key]['name'] == target_source:
                    try:
                        source = target_source.replace("-", "m").replace("+", "p")
                        print(f"The {target_source} is observed in {ms}\nPerform the split by mstransform.")
                        mstransform(vis=ms, 
                                    outputvis=f"{source}.{ms}",
                                    field=target_source,
                                    intent=obs_intent,
                                    datacolumn="all")
                    except:
                        print(f"{target_source} is NOT observed in the {ms}.")

step = 2
# Export splited MS to .fits format
if mystep == step:
    target_source = target_source.repls
    MS_splited = subprocess.run("ls {target_source} -d", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    MS_splited = MS_splited.stdout.decode()
    MS_splited = MS_splited.split("\n")
    MS_splited.pop()
