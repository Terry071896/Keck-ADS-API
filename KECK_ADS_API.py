import numpy as np
import pandas as pd
from keckAdsApi import Keck_ADS_API
from progressbar import ProgressBar
pbar = ProgressBar()
import os
cwd = os.getcwd()

from threading import Lock
import multiprocessing
multiprocessing.freeze_support()

try:
    mutex = Lock()

    mutex.acquire()
    theAPI = Keck_ADS_API()

    search = '1'
    while(search == '1'):
        queue = None
        while(queue == None):
            try:
                queue = input('Type Search: ')
            except:
                print('Try again')
                queue = None
        if queue != '':
            theAPI.search(queue, rows=1000)
            theAPI.add()
        search = 4
        while(search not in ['1','2','3']):
            print('1. New Search')
            print('2. Export')
            print('3. Exit WITHOUT Saving')
            search = (input('Enter \'1\', \'2\', or \'3\': '))

    if search == 2:
        print('In Folder: '+cwd)
        theAPI.export()

    print('Done.')
    mutex.release()
    exit()
except:
    import subprocess
    p = subprocess.Popen(['killall', '-9', 'KECK_ADS_API'], stdout=subprocess.PIPE)
    out, err = p.communicate()
