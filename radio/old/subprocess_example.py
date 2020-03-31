import time
import subprocess
#subprocess.call(["mpv", "http://rbb-fritz-live.cast.addradio.de/rbb/fritz/live/mp3/128/stream.mp3", "--quiet"])


stream = subprocess.Popen(["mpv", "http://rbb-fritz-live.cast.addradio.de/rbb/fritz/live/mp3/128/stream.mp3", "--quiet"], stdout=subprocess.PIPE)
time.sleep(3)
print("sleep fini, start comm")
output = stream.communicate()

print(output)
