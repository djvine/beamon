import sys
import os
import datetime as dt
import epics
import maps
import ipdb

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

def setup_user_dirs(user, root='/tmp/2ide', debug=False):
    user = user.title()
    current_run = get_current_run()

    dirname = '/'.join([root, current_run, user])

    # Check if dir exists
    if os.path.exists(dirname) or os.path.exists(dirname.lower()):
        idx = 1
        while True:
            if os.path.exists(dirname+'{:d}'.format(idx)) or os.path.exists(dirname.lower()+'{:d}'.format(idx)):
                idx+=1
            dirname = '{:s}{:d}'.format(dirname, idx)
            break

    os.makedirs(dirname)
    os.makedirs(dirname+'/mda')
    os.makedirs(dirname+'/flyXRF')
    os.makedirs(dirname+'/vlm')
    os.makedirs(dirname+'/focusing')
    os.makedirs(dirname+'/screenshots')

    if debug:
        sys_user = 'david'
    else:
        sys_user = 'user2ide'

    os.system('chown -R {:s} {:s}'.format(sys_user, dirname))

    # Add maps settings
    with open(dirname+'/maps_settings.txt', 'w') as f:
        f.writelines(maps.generate_maps_settings())

    # Add maps override params
    with open(dirname+'/maps_fit_parameters_override.txt', 'w') as f:
        f.writelines(maps.generate_maps_override(debug=debug))

def setup_save_data(user):
    print('caput 2xfm:saveData_subDir {:s}'.format(dirname+ '/mda'))
    epics.caput('2xfm:saveData_subDir {:s}'.format(dirname + '/mda'))

    print('caput 2xfm:saveData_scanNumber 1')
    epics.caput('2xfm:saveData_scanNumber', 1)

    print(epics.caget('2xfm:saveData_message'))

