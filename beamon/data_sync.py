"""
.. module:: data_sync
   :platform: Unix
   :synopsis: Sync data between two directories one-time or as a daemon.

.. moduleauthor:: David Vine <djvine@gmail.com>


"""
import glob
import os
import subprocess
import sys
import time

src_dir = '/tmp/src'
dst_dir = '/tmp/dst'
rsync = 'rsync --compress --progress --verbose --times --update'
throttle_time = 10.0 # Don't sync more frequently than this (seconds)
daemonise = True
verbose = False
"""
Files from the source directory will be copied to a subfolder in the destination directory
as specfied in the extension mapping.
"""

extension_mapping = {
    'mda': 'mda',
    'nc': 'flyXRF',
}

def create_dest_dirs(src_dir=src_dir, dst_dir=dst_dir):
    for extension, subdir in extension_mapping.items():
        dirname = os.path.join(dst_dir, subdir)
        if not os.path.exists(dirname):
            os.makedirs(dirname)


def sync(verbose=False, src_dir=src_dir, dst_dir=dst_dir):
    files = glob.glob(os.path.join(src_dir, '*'))

    for filename in files:
        for extension, subdir in extension_mapping.items():
            if filename.endswith(extension):
                if verbose:
                    print('\n\n\nSyncing file {:s} to {:s}'.format(filename, os.path.join(dst_dir, subdir, os.path.split(filename)[-1])))
                cmd = ' '.join([rsync, filename, os.path.join(dst_dir, subdir, os.path.split(filename)[-1])])
                try:
                    p = subprocess.Popen(cmd, shell=True)
                    p.communicate()
                except KeyboardInterrupt:
                    p.kill()
                    sys.exit(1)




if __name__=='__main__':
    create_dest_dirs()
    sync(verbose=verbose)
    if daemonise:
        while True:
            then = time.time()
            sync(verbose=verbose)
            if time.time()-then < throttle_time:
                time.sleep(time.time()-then)
