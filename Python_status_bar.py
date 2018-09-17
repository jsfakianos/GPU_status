
import re
import subprocess
import cv2 as cv
import numpy as np
import time

Six_Color_Palette = {'Semat': ((255, 255, 255), (255, 233, 34), (54, 84, 151), (101, 153, 245), (177, 213, 252), (212, 212, 212) ),
                     'Succulent': ((228, 217, 237), (234, 188, 153), (119, 75, 93), (117, 140, 160), (147, 201, 224), (207, 229, 229)),
                     'Summer': ((228, 232, 235), (238, 253, 251), (59, 63, 60), (99, 125, 103), (152, 174, 149), (203, 211, 213) ),
                     'Wanderlust': ((67, 62, 59), (241, 238, 229), (227, 216, 192), (167, 125, 110), (129, 124, 116), (181, 190, 181) ),
                     'Rustic': ((167, 160, 158), (95, 88, 86), (47, 45, 50), (65, 76, 95), (103, 149, 161), (184, 214, 222) ),
                     'Flora': ((243, 241, 244), (220, 228, 238), (176, 193, 214), (80, 84, 124), (48, 54, 75), (169, 206, 165) ),
                     'Foraged Hues': ((235, 236, 219), (202, 196, 186), (153, 143, 137), (56, 50, 50), (16, 20, 22), (37, 45, 63) ),
                     'Slow Living': ((50, 69, 84), (19, 22, 26), (56, 24, 31), (95, 89, 85), (157, 165, 153), (221, 224, 216) ),
                     'Nature Hues': ((171, 196, 195), (111, 145, 152), (98, 88, 80), (208, 169, 133), (238, 224, 199), (233, 236, 223) ),
                     'Punch Line 2': ((244, 191, 137), (87, 163, 121), (138, 84, 163), (180, 117, 154), (79, 76, 86) ),
                     'Punch line': ((185, 231, 178), (255, 223, 91), (96, 204, 148), (120, 92, 80), (255, 226, 201) ),
                     'moving on': ((70, 250, 255), (242, 194, 255), (255, 151, 151), (255, 220, 165), (207, 255, 205) ),
                     'Fishy': ((90, 159, 157), (148, 95, 95), (100, 154, 110), (75, 86, 122), (84, 150, 132) ),
                     'tetradic': ((103, 104, 225), (224, 101, 225), (227, 226, 106), (101, 221, 100), (242, 99, 121) ),
                     'jeff': ((80, 80, 80), (90, 159, 157), (148, 95, 95), (100, 154, 110), (75, 86, 122), (84, 150, 132)),
                     'Heavens Door': ((109, 187, 216), (255, 132, 132), (152, 244, 182), (251, 186, 218), (236, 227, 144) )}

def rgb2bgr(color=(0,0,0)):
    return int(color[2]), int(color[1]), int(color[0])

def main_loop():

    value = re.compile('>.*?<')
    cols = 400 * 2
    rows = 40 * 2
    margin = 10
    font = cv.FONT_HERSHEY_SIMPLEX
    oldtime = time.time()
    updateFan = False
    #   driver, product, fan_speed, gpu_temp, power_draw, utilization
    #      0       1         2          3          4          5           6      7    8     9
    gpu_vitals = ['367.57','GTX 970','','', '', '', '', '', '']
    c_list = Six_Color_Palette['jeff']
    background_color = rgb2bgr(c_list[0])
    text_color = rgb2bgr(c_list[5])

    img = np.full([rows, cols, 3], background_color, np.uint8)
    cv.putText(img, 'fan speed', (20, 30), cv.FONT_HERSHEY_DUPLEX, 1, color=text_color)
    cv.putText(img, 'temperature', (20, 65), cv.FONT_HERSHEY_DUPLEX, 1, color=text_color)
    cv.putText(img, 'power draw', (400, 30), cv.FONT_HERSHEY_DUPLEX, 1, color=text_color)
    cv.putText(img, 'gpu utilization', (400, 65), cv.FONT_HERSHEY_DUPLEX, 1, color=text_color)

    swatch = 0
    swatch_width = 50
    #for bgr in c_list:
    #    cv.rectangle(img, (swatch, 0), (swatch_width + swatch, 40), rgb2bgr(bgr), -1)
    #    swatch += swatch_width

    def update_canvas():
        dim = (int(cols/2), int(rows/2))
        new_img = np.copy(img)
        cv.putText(new_img, gpu_vitals[2], (180, 30), cv.FONT_HERSHEY_DUPLEX, 1, color=text_color)
        cv.putText(new_img, gpu_vitals[3], (225, 65), cv.FONT_HERSHEY_DUPLEX, 1, color=text_color)
        cv.putText(new_img, gpu_vitals[4], (590, 30), cv.FONT_HERSHEY_DUPLEX, 1, color=text_color)
        cv.putText(new_img, gpu_vitals[5], (635, 65), cv.FONT_HERSHEY_DUPLEX, 1, color=text_color)
        new_img = cv.resize(new_img, dim, interpolation=cv.INTER_AREA)
        #cv.setWindowProperty(new_img,a)
        cv.imshow(gpu_vitals[1] + ' - ' + gpu_vitals[0], new_img)


    def get_GPU_vitals(updateFan):

        vitals = subprocess.Popen(['nvidia-smi'], bufsize=-1, stdout=subprocess.PIPE)
        #b'| 22%   38C    P2    46W / 170W |    265MiB /  4034MiB |      0%      Default |\n'
        #b'| NVIDIA-SMI 367.57                 Driver Version: 367.57                    |\n'

        for key, line in enumerate(vitals.stdout):
            if key==2:
                line=line.decode("utf-8")
                gpu_vitals[2] = line[51:71]
                gpu_vitals[2] = gpu_vitals[2].replace(' ', '')
            if key==8:
                line=line.decode("utf-8")
                gpu_vitals[2] = line[1:5]
                gpu_vitals[3] = line[8:12]
                gpu_vitals[4] = line[20:24]
                gpu_vitals[5] = line[60:64]
                print(line[36:40])
                print(line[47:51])
                gpu_vitals[6] = int(line[36:40].strip())
                gpu_vitals[7] = int(line[47:51].strip())
                gpu_vitals[8] = str(int((gpu_vitals[7] - gpu_vitals[6]) / gpu_vitals[7] * 100)) + '%fmem'

        if updateFan:
            thermal_int = int(gpu_vitals[3][:2])
            #  nvidia-settings -a [fan:0]/GPUTargetFanSpeed=15
            if 38 > thermal_int and gpu_vitals[2] != ' 15%':
                subprocess.Popen(['nvidia-settings', '-a', '[fan:0]/GPUTargetFanSpeed=15'], bufsize=-1)
            if 42 > thermal_int > 37 and gpu_vitals[2] != ' 25%':
                subprocess.Popen(['nvidia-settings', '-a', '[fan:0]/GPUTargetFanSpeed=25'], bufsize=-1)
            elif 45 > thermal_int > 41 and gpu_vitals[2] != ' 50%':
                subprocess.Popen(['nvidia-settings', '-a', '[fan:0]/GPUTargetFanSpeed=50'], bufsize=-1)
            elif 50 > thermal_int > 44 and gpu_vitals[2] != ' 70%':
                subprocess.Popen(['nvidia-settings', '-a', '[fan:0]/GPUTargetFanSpeed=70'], bufsize=-1)
            elif thermal_int > 49 and gpu_vitals[2] != ' 90%':
                subprocess.Popen(['nvidia-settings', '-a', '[fan:0]/GPUTargetFanSpeed=90'], bufsize=-1)

        update_canvas()






    while True:
        key = cv.waitKey(100)
        #if key == 1048676:      # 'd' = 1048676
        if key == 1048689:   # 'q'==1048689
            subprocess.Popen(['nvidia-settings', '-a', '[fan:0]/GPUTargetFanSpeed=15'], bufsize=-1)
            cv.destroyAllWindows()
            break
        elif key == 1113939: #right arrow
            break
        elif key == 1113937: #left arrow
            break
        if time.time() > oldtime + 3:
            get_GPU_vitals(True)
            oldtime = time.time()
        else:
            get_GPU_vitals(False)

main_loop()
