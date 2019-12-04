
'''
a potentially easier way to do this is
nvidia-smi --query-gpu=gpu_name,driver_version,temperature.gpu,power.draw,power.limit,utilization.gpu,utilization.memory,memory.total,memory.free,memory.used,fan.speed --format=csv,nounits,noheader
then split(',')
'''

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk
gi.require_version('AppIndicator3', '0.1')
from gi.repository import AppIndicator3 as appindicator
from threading import Thread
import subprocess
import cairo
import os
import time

APPINDICATOR_ID = 'myappindicator'
# /run/user/1000/GPU-load-indicator/
#+ u'\u2103'
icon_directory = '/run/user/1000/GPU-load-indicator/'
if not os.path.exists(icon_directory):
    os.makedirs(icon_directory)

class app_indicator(Thread):

    def __init__(self, threadID, name):
        Thread.__init__(self)
        self.gpuVitals = []
        self.count = 0
        self.threadID = threadID
        self.name = name
        self.indicator = appindicator.Indicator.new(APPINDICATOR_ID, \
                         icon_directory + 'icon.png', \
                         appindicator.IndicatorCategory.HARDWARE)

    def run(self):
        self.indicate()

    def build_menu(self):
        menu = gtk.Menu()
        item_quit = gtk.MenuItem('Quit')
        item_quit.connect('activate', quit)
        menu.append(item_quit)
        menu.show_all()
        return menu

    def update_icon(self):
        #vitals = subprocess.Popen(['nvidia-smi'], bufsize=-1, stdout=subprocess.PIPE)
        vitals_cmd = ['nvidia-smi',
                      '--query-gpu=gpu_name,driver_version,temperature.gpu,power.draw,power.limit,utilization.gpu,utilization.memory,memory.total,memory.free,memory.used,fan.speed',
                      '--format=csv,nounits,noheader']
        vitals = subprocess.Popen(vitals_cmd, bufsize=-1, stdout=subprocess.PIPE)
        '''
        #   0   gpu_name,
        #   1   driver_version,
        #   2   temperature.gpu
        #   3   power.draw
        #   4   power.limit,
        #   5   utilization.gpu,
        #   6   utilization.memory,
        #   7   memory.total,
        #   8   memory.free,
        #   9   memory.used,
        #   10  fan.speed

        '''

        self.gpuVitals = vitals.stdout.read().decode("utf-8")[:-1].split(',')
        #print(self.gpuVitals)

        # set fan speed based on line equation     speed = temp * 2.9 - 60
        intendedFanSpeed = float(self.gpuVitals[2]) * 2.5 - 60
        subprocess.Popen(['nvidia-settings', '--assign=[fan:0]/GPUTargetFanSpeed={0:.0f}'.format(intendedFanSpeed)],
                         bufsize=-1)

        icon_width = 150
        fresh_icon = cairo.ImageSurface(cairo.FORMAT_ARGB32, icon_width, 22) #icon  # possibly create_similar
        cr = cairo.Context(fresh_icon)
        cr.set_source_rgba(1,0.6,0,0)
        cr.rectangle(0, 0, icon_width, 22)
        cr.fill()
        cr.select_font_face('Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(8)
        cr.set_source_rgb(0.9,0.9,0.9)#(1,1,1)
        cr.move_to(19, 8)
        cr.show_text('Nvidia ' + self.gpuVitals[0].strip() + '  v' + self.gpuVitals[1].strip())
        cr.set_font_size(10)
        cr.move_to(3, 21)
        cr.show_text(self.gpuVitals[2].strip() + u'\u2103' )
        cr.move_to(29, 21)
        cr.show_text(self.gpuVitals[10].strip())
        cr.move_to(60, 21)
        cr.show_text(self.gpuVitals[3].strip())
        cr.move_to(91, 21)
        cr.show_text(self.gpuVitals[5].strip())
        cr.move_to(120, 21)
        cr.show_text(self.gpuVitals[8].strip())
        fresh_icon.write_to_png(icon_directory + 'icon' + str(self.count % 2) + '.png')
        self.indicator.set_icon(icon_directory + 'icon' + str(self.count % 2) + '.png')

    def indicate(self):
        a = 1
        self.indicator = appindicator.Indicator.new(APPINDICATOR_ID, icon_directory + 'icon.png', appindicator.IndicatorCategory.HARDWARE)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.build_menu())
        while True:
            self.update_icon()
            self.count+=1
            time.sleep(0.5)

    def quit(self):
        subprocess.Popen(['nvidia-settings', '--assign=[fan:0]/GPUTargetFanSpeed=15'], bufsize=-1)
        gtk.main()
        Thread._stop()

if __name__ == '__main__':
    indicator_thread = app_indicator(3888, name='app_indicate')
    indicator_thread.start()
    gtk.main()
