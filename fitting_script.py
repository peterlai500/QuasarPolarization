import subprocess

INT = "CALIBRATE_BANDPASS#ON_SOURCE"
target_source = "J1924-2914"
ms = "uid___A002_Xfe62c1_X8ff4.ms.split.cal"

visibility = subprocess.run("ls *.ms.split.cal -d", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
visibility = visibility.stdout.decode()
visibility = visibility.split("\n")
visibility.pop()

print(visibility)

target_source = target_source.replace("-", "m").replace("+", "p")

for ms in visibility:
    obs_list = listobs(vis=ms)
    mstransform_done = False
    for key, value in obs_list.items():
        if key.startswith('field_'):
            if obs_list[key]['name'] == target_source:
                print(f"The {target_source} is observed in {ms}")
                mstransform(vis=ms, 
                            outputvis=f"{target_source}.{ms}",
                            field=target_source,
                            intent=INT)
                mstransform_done = True
                break
    if mstransform_done:
        break

                
