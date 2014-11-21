import pyinotify
import epics
import os
import ipdb
import time
import threading
import shutil 

fn_livejob = 'livejob_{run:s}_2ide_{user:s}.txt'
mda_watch_dir = '/mnt/xfm0/data/2ide/{run:s}/{user:s}{repeat:s}/mda'
status_watch_dir = '/mnt/xfm0/data/jobs'

class OnFileModified(pyinotify.ProcessEvent):

    def __init__(self):
        pass

    def mda_created(self, event):
        print '==> MDA file created'
        dir = event.pathname[:event.pathname.find('mda')]
        if os.path.exists(dir+'/'+fn_livejob.format(**{'user': user.get(), 'run': run.get()})):
            shutil.move(dir+'/'+fn_livejob.format(**{'user': user.get(), 'run': run.get()}), '/mnt/xfm0/data/jobs/ready_to_go')

    def status_updated(self, event):
        print '==> MAPS Processing status updated'

    def process_IN_CREATE(self, event):
        
        if event.pathname.endswith('mda'):
            self.mda_created(event)
        elif event.pathname.startswith('status') and event.pathname.endswith('txt'):
            self.status_updated(event)

    def process_IN_MODIFY(self, event):

        if event.pathname.startswith('status') and event.pathname.endswith('txt'):
            self.status_updated(event)

def on_user_change(pvname, value, **kwargs):
    
    global wm
    global mda_watches

    for watch in mda_watches:
        wm.rm_watch(watch.values())

    t = threading.Thread(target=add_mda_watches)
    t.start()

def add_mda_watches():
    global wm
    global mda_watches
    mda_watches = []
    if os.path.exists(mda_watch_dir.format(**{'user':user.get(), 'run':run.get(), 'repeat':''})):
        print('Begin monitoring '+ mda_watch_dir.format(**{'user':user.get(), 'run':run.get(), 'repeat':''}))
        mda_watches.append(wm.add_watch(mda_watch_dir.format(**{'user':user.get(), 'run':run.get(), 'repeat':''}), pyinotify.IN_CREATE))
        for i in range(10):
            if os.path.exists(mda_watch_dir.format(**{'user': user.get(), 'run': run.get(), 'repeat': '{:d}'.format(i)})):
                print('Begin monitoring ' + mda_watch_dir.format(**{'user': user.get(), 'run': run.get(), 'repeat': '{:d}'.format(i)}))
                mda_watches.append( wm.add_watch(mda_watch_dir.format(**{'user':user.get(), 'run':run.get(), 'repeat': '{:d}'.format(i)}), pyinotify.IN_CREATE))
        status.put(1)
        return True
    else:
        status.put(0)
        print('Path does not exist, no monitoring')
        return False

def maps_processing_worker():
    global wm
    global mda_watches
    while True:
        if add_mda_watches():
            break
        else:
            time.sleep(5.0)

def maps_status_check(pvname, value, **kwargs):
    if value==0:
        # Processing is disabled, keep checking until processing can be reenabled
        t = threading.Thread(target=maps_processing_worker)
        t.start()

user = epics.PV('2xfmS1:user_string.VAL')
run = epics.PV('2xfmS1:run_string.VAL')
status = epics.PV('2xfmS1:maps_processing_status.VAL', callback = maps_status_check)

if __name__ == '__main__':

    wm = pyinotify.WatchManager()
    handler = OnFileModified()
    notifier = pyinotify.Notifier(wm, default_proc_fun=handler)
    add_mda_watches()
    status_watch = wm.add_watch(status_watch_dir, pyinotify.IN_MODIFY | pyinotify.IN_CREATE)

    user.add_callback(on_user_change)
    print('Start monitoring (type ctrl^c to exit).')
    notifier.loop()
