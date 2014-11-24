import epics
import data_sync
import time

#run = epics.PV()
#user = epics.PV()
#esaf = epics.PV()

src = '/tmp/src'
dst = '/tmp/dst'

throttle_time = 10.0

data_sync.create_dest_dirs(src_dir=src, dst_dir=dst)
while True:
    then = time.time()
    data_sync.sync(verbose=True, src_dir=src, dst_dir=dst)
    if time.time()-then<throttle_time:
        print(throttle_time+then-time.time())
        time.sleep(throttle_time+then-time.time())


