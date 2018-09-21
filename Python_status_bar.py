
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
           # hard coded GTX 970 out of laziness
        gpu_vitals = ['','GTX 970','','', '', '', '', '', '', '']
        vitals = subprocess.Popen(['nvidia-smi'], bufsize=-1, stdout=subprocess.PIPE)
        #b'| NVIDIA-SMI 367.57                 Driver Version: 367.57                    |\n'
        #b'| 22%   38C    P2    46W / 170W |    265MiB /  4034MiB |      0%      Default |\n'
        for key, line in enumerate(vitals.stdout):
            if key==2:
                line=line.decode("utf-8")
                gpu_vitals[0] = line[51:71]
                gpu_vitals[0] = gpu_vitals[0].replace(' ', '')
            if key==8:
                line=line.decode("utf-8")
                gpu_vitals[2] = line[1:5]
                gpu_vitals[3] = line[8:10]
                gpu_vitals[4] = line[20:24]
                gpu_vitals[5] = line[60:64]
                gpu_vitals[6] = int(line[36:40].strip())
                gpu_vitals[7] = int(line[47:51].strip())
                gpu_vitals[8] = '{:2d}%'.format(int((gpu_vitals[7] - gpu_vitals[6]) / gpu_vitals[7] * 100))

        thermal_int = int(gpu_vitals[3][:2])
        #  nvidia-settings -a [fan:0]/GPUTargetFanSpeed=15
        if 38 > thermal_int and gpu_vitals[2] != ' 15%':
            subprocess.Popen(['nvidia-settings', '-a', '[fan:0]/GPUTargetFanSpeed=15'], bufsize=-1)
        if 41 > thermal_int > 37 and gpu_vitals[2] != ' 25%':
            subprocess.Popen(['nvidia-settings', '-a', '[fan:0]/GPUTargetFanSpeed=25'], bufsize=-1)
        elif 45 > thermal_int > 40 and gpu_vitals[2] != ' 50%':
            subprocess.Popen(['nvidia-settings', '-a', '[fan:0]/GPUTargetFanSpeed=50'], bufsize=-1)
        elif 50 > thermal_int > 44 and gpu_vitals[2] != ' 70%':
            subprocess.Popen(['nvidia-settings', '-a', '[fan:0]/GPUTargetFanSpeed=70'], bufsize=-1)
        elif thermal_int > 49 and gpu_vitals[2] != ' 90%':
            subprocess.Popen(['nvidia-settings', '-a', '[fan:0]/GPUTargetFanSpeed=90'], bufsize=-1)

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
        cr.show_text('Nvidia ' + gpu_vitals[1] + '  v' + gpu_vitals[0])
        cr.set_font_size(10)
        cr.move_to(3, 21)
        cr.show_text(gpu_vitals[3] + u'\u2103' )
        cr.move_to(29, 21)
        cr.show_text(gpu_vitals[2])
        cr.move_to(60, 21)
        cr.show_text(gpu_vitals[4])
        cr.move_to(91, 21)
        cr.show_text(gpu_vitals[5])
        cr.move_to(120, 21)
        cr.show_text(gpu_vitals[8])
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


        #gtk.main()

    def quit(self):
        subprocess.Popen(['nvidia-settings', '-a', '[fan:0]/GPUTargetFanSpeed=15'], bufsize=-1)
        gtk.main()
        Thread._stop()

if __name__ == '__main__':
    indicator_thread = app_indicator(3888, name='app_indicate')
    indicator_thread.start()
    gtk.main()

