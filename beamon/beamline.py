import sys
import os
import datetime as dt
import epics
import maps
import ipdb
import schedule
import time
import shutil

def get_run_name_from_schedule():
    """
    Get the current run name from the scheduling system.
    """
    now = dt.datetime.now()
    return schedule.findRunName(now, now)

def get_user():
    return schedule.get_pi()

def get_current_run():

    """
    Return string with yearrun format: e.g 2011-2
    """
    # "-1" = month <5
    # "-2" = 5 <= month <9
    # "-3" = 9 <= month <12

    year = dt.datetime.now().year
    month = dt.datetime.now().month
    if month < 5:
            r_string = '-1'
    elif (month >=5) and (month < 9):
            r_string = '-2'
    elif month >= 9:
            r_string = '-3'

    return '{:d}{:s}'.format(year, r_string)

def generate_config(user, run, debug=False, root='/mnt/xfm0/data/2ide'):
    user = user.title()

    dirname = '/'.join([root, run, user])

    if not os.path.exists(dirname):
	return

    # Add maps settings
    #with open(dirname+'/maps_settings.txt', 'w') as f:
    #    f.writelines(maps.generate_maps_settings())

    # Add maps override params
    with open(dirname+'/maps_fit_parameters_override.txt', 'w') as f:
        f.writelines(maps.generate_maps_override(debug=debug))

    # Add maps livejob
    #with open(dirname+'/livejob_{run:s}_2ide_{user:s}.txt'.format(**{'user': user, 'run': run}),'w') as f:
    #    f.writelines(maps.generate_maps_livejob(user=user, run=run))

def setup_user_dirs(user, root='/mnt/xfm0/data/2ide', debug=False):
    while True:
        if user[-1].isdigit():
            user=user[:-1]
        else:
            break

    user = user.lower()
    current_run = get_run_name_from_schedule()

    dirname = '/'.join([root, current_run, user])

    # Check if dir exists
    if os.path.exists(dirname) or os.path.exists(dirname.lower()):
        idx = 1
        while True:
            if os.path.exists(dirname+'{:d}'.format(idx)) or os.path.exists(dirname.lower()+'{:d}'.format(idx)):
                idx+=1
            else:
                dirname = '{:s}{:d}'.format(dirname, idx)
                break

    os.makedirs(dirname)
    os.makedirs(dirname+'/mda', mode=0777)
    os.makedirs(dirname+'/flyXRF', mode=0777)
    os.makedirs(dirname+'/vlm', mode=0777)
    os.makedirs(dirname+'/focusing', mode=0777)
    os.makedirs(dirname+'/screenshots', mode=0777)

    # Add maps settings
    with open(dirname+'/maps_settings.txt', 'w') as f:
        f.writelines(maps.generate_maps_settings())

    # Add maps override params
    with open(dirname+'/maps_fit_parameters_override.txt', 'w') as f:
        f.writelines(maps.generate_maps_override(debug=debug))

    # Add maps livejob
    with open(dirname+'/livejob_{run:s}_2ide_{user:s}.txt'.format(**{'run':current_run, 'user': dirname.split('/')[-1]}),'w') as f:
        f.writelines(maps.generate_maps_livejob(user=dirname.split('/')[-1], run=current_run))
    
    # Check for maps.cfg
    if not os.path.exists(dirname+'/maps.cfg'):
        shutil.copy('/mnt/xfm0/data/2ide/2014-3/comm/maps.cfg', dirname)

    epics.caput('2xfmS1:user_string.VAL', dirname.split('/')[-1])
    return dirname.split('/')[-1]

def setup_user_dirs_save_data_location(user):
    name = setup_user_dirs(user)
    time.sleep(5.0)
    setup_save_data(name)

def setup_save_data(user, root='//xfm0/xfm0-data/data/2ide'):
    current_run = get_run_name_from_schedule()

    dirname = '/'.join([root, current_run, user])

    print('caput 2xfm:saveData_subDir {:s}/mda'.format(user))
    epics.caput('2xfm:saveData_subDir', '{:s}/mda'.format(user))

    print('caput 2xfm:saveData_scanNumber 1')
    epics.caput('2xfm:saveData_scanNumber', 1)

    print(epics.caget('2xfm:saveData_message'))

    print('caput dxpXMAP2xfm3:netCDF1:FilePath {:s}'.format(dirname+'/flyXRF'))
    epics.caput('dxpXMAP2xfm3:netCDF1:FilePath', '')
    epics.caput('dxpXMAP2xfm3:netCDF1:FilePath', dirname+'/flyXRF')

