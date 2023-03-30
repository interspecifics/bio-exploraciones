#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# *
"""
speculative communications SCOPE.analyzer 2023
-----------------------------------------------

"""

import pygame
import pygame.camera
from pygame.locals import *
import math, statistics
from oscpy.client import OSCClient
import os
#import serial
#import threading
import numpy as np
import cv2
from tracker import scTracker
# -


# * --------------------------------------- * #
OSC_HOST = "127.0.0.1"
OSC_PORT = 9000
OSC_CLIENT = []

TIC_TIMER = 250

# other globals
f_count = 0
capture = True
ii = 0
N_PROBES = 5
current_set = [[0.0,0.0,0.0,0.0] for j in range(N_PROBES)]
cursor = 0
past_cursor = 0
N_SYNTHS = 4
act_synth = 0
past_synth = 0

# * --------------------------------------- * #
DEVICE = 0
#DEVICE = "/dev/video2"
# * --------------------------------------- * #
CAM_SIZE = (640, 480)
SIZE = (800, 640)
SIZE = (800, 800)
WI, HE = SIZE
FILENAME = 'capture.png'



#type of detection, 0:pixel, 1:contours
obj_type = 1
#pixel path mode
probe_mode = 0
#contour mode
ct_mode = 0

current_contours = [[0,0,0,0]]
objects = []

big_thresh = 200
big_blur = 3

#source_mode: 0:img, 1:vid, 2:cam
source_mode = 2
img_stream = None
video_stream = None

ct = scTracker()
(H, W) = (640, 480)
kernel = np.ones((2,2),np.uint8)


# a. start the pygame engine
pygame.init()
print(pygame.camera.get_backends())
pygame.camera.init()
#pygame.camera.init(pygame.camera.get_backends()[1])
print(pygame.camera.list_cameras())
# a. start the display
DISPLAY = pygame.display.set_mode(SIZE, 0)       
pygame.display.init()
pygame.display.update()
#print(pygame.display.get_driver())
#DISPLAY = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
# invisible cursor
#pygame.mouse.set_visible(False)
pygame.display.set_caption(": Comunicaciones Especulativas :")

# a. start the cam
CAM = pygame.camera.Camera(DEVICE, CAM_SIZE)
CAM.start()
# a. start overlays
#screen = pygame.surface.Surface(SIZE, 0, display)
BASE = pygame.Surface(CAM_SIZE)
OVERLAY = pygame.Surface(SIZE, pygame.SRCALPHA)
ECHO =    pygame.Surface(SIZE, pygame.SRCALPHA)
ECHO.fill((0,0,0,0))
GUI = pygame.Surface((WI, HE),pygame.SRCALPHA)

# a. states and counters
clock = pygame.time.Clock()
# timer events
TIC_EVENT = pygame.USEREVENT + 1
#TIC_TIMER = 1000

# b. load stuff, like fonts
FONT_PATH = './RevMiniPixel.ttf'
#FONT_PATH = '/home/pi/W/scope/RevMiniPixel.ttf'
FONT = pygame.font.Font(FONT_PATH, 14)
FONTmed = pygame.font.Font(FONT_PATH, 10)
FONTmini = pygame.font.Font(FONT_PATH, 8)


# z. the pygame layout
# ------------------------------------------------------------------
#draw frames
colors = [(0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (192,192,192), (127, 127, 127), (64, 64, 64)]
colors = [(0, 0, 0), (255, 255, 255), (100, 144, 216), (147, 203, 241), (42, 60, 148), (164, 91, 92), (212, 159, 166), (58, 79, 91)]
pygame.draw.rect(GUI, colors[1], pygame.Rect([1,1,WI-2, HE-2]), 1)
pygame.draw.rect(GUI, colors[1], pygame.Rect([1,1,WI-2, 620]), 1)
pygame.draw.rect(GUI, colors[1], pygame.Rect([1,620,WI-2, HE-560-2]), 1)

#then buttons
buttons = []
# ------------------------------------------------------------------
# A0: back to camera
rb_in0 = [120, 640, 560, 20]
btn_in0 = pygame.draw.rect(GUI, colors[1], pygame.Rect(rb_in0), 2)
buttons.append(btn_in0) #- 0
# ------------------------------------------------------------------
# B0 .pixels
rb_mo0 = [120, 670, 170, 20]
btn_mo0 = pygame.draw.rect(GUI, colors[2], pygame.Rect(rb_mo0), 2)
buttons.append(btn_mo0) #- 1
# B1 .shapes
rb_mo1 = [315, 670, 170, 20]
btn_mo1 = pygame.draw.rect(GUI, colors[3], pygame.Rect(rb_mo1), 2)
buttons.append(btn_mo1) #- 2
# B2 .objects
rb_mo2 = [510, 670, 170, 20]
btn_mo2 = pygame.draw.rect(GUI, colors[4], pygame.Rect(rb_mo2), 2)
buttons.append(btn_mo2) #- 3
# ------------------------------------------------------------------
# C0 .pixels path C
rb_pix0 = [120, 700, 170, 20]
btn_pix0 = pygame.draw.rect(GUI, colors[2], pygame.Rect(rb_pix0), 1)
buttons.append(btn_pix0) #- 4
# C1 .pixels path H
rb_pix1 = [120, 730, 170, 20]
btn_pix1 = pygame.draw.rect(GUI, colors[2], pygame.Rect(rb_pix1), 1)
buttons.append(btn_pix1) #- 5
# C2 .pixels path V
rb_pix2 = [120, 760, 170, 20]
btn_pix2 = pygame.draw.rect(GUI, colors[2], pygame.Rect(rb_pix2), 1)
buttons.append(btn_pix2) #- 6
# ------------------------------------------------------------------
# D0 .contour thresh 1
rb_cont0 = [315, 700, 170, 20]
btn_cont0 = pygame.draw.rect(GUI, colors[3], pygame.Rect(rb_cont0), 1)
buttons.append(btn_cont0) #- 7
# D1 .contour thresh 2
rb_cont1 = [315, 730, 170, 20]
btn_cont1 = pygame.draw.rect(GUI, colors[3], pygame.Rect(rb_cont1), 1)
buttons.append(btn_cont1) #- 8
# D2 .contour param 3
rb_cont2 = [315, 760, 170, 20]
btn_cont2 = pygame.draw.rect(GUI, colors[3], pygame.Rect(rb_cont2), 1)
buttons.append(btn_cont2) #- 9
# ------------------------------------------------------------------
# E0 .contour thresh 1
rb_obj0 = [315, 700, 170, 20]
btn_obj0 = pygame.draw.rect(GUI, colors[3], pygame.Rect(rb_obj0), 1)
buttons.append(btn_obj0) #- 10
# E1 .contour thresh 2
rb_obj1 = [315, 730, 170, 20]
btn_obj1 = pygame.draw.rect(GUI, colors[3], pygame.Rect(rb_obj1), 1)
buttons.append(btn_obj1) #- 11
# E2 .contour param 3
rb_obj2 = [315, 760, 170, 20]
btn_obj2 = pygame.draw.rect(GUI, colors[3], pygame.Rect(rb_obj2), 1)
buttons.append(btn_obj2) #- 12

#LABELS
titles = [
    "Cámara",
    "Pixels",
    "Formas",
    "Objetos",
    "Circular",
    "Horizontal",
    "Vertical",
    "Thresh_A",
    "Thresh_B"
    "Param_C"
    ]
labels = [FONT.render(ti, 1, colors[1]) for ti in titles]
#self.labels["norm"] = [_fonts[2].render("N", 1, color_text_2 if self.state['norm'] else self.color), [posit[0]-200, posit[1]+15]]
i_lt = 0.5
i_ht = 1.0
hi_thresh = 127
low_thresh = 255
# ------------------------------------------------------------------




# c. osc functions
def start_osc(osc_host = OSC_HOST, osc_port = OSC_PORT):
    global OSC_CLIENT
    OSC_CLIENT = OSCClient(osc_host, osc_port)
    return

# c. osc functions
def update_alldata_send():
    global OSC_CLIENT, current_set
    print("[osc] --- ---- ----- ---- ")
    for i in range(N_PROBES):
        act_set = current_set[i].copy()
        ruta = '/ce_scope/synth{}'.format(i)
        try:
            ##print(ruta,'\t',act_set)
            OSC_CLIENT.send_message(ruta.encode('utf-8'), act_set)
            print(ruta+"\t{:0.2f}\t{:0.2f}\t{:0.2f}\t{:0.2f}".format(act_set[0], act_set[1], act_set[2], act_set[3]))
        except:
            print("---- ----- ---- ")
    return

# c. osc functions
def update_data_send_m1():
    global OSC_CLIENT, current_set, cursor, act_synth
    print("[pixels_osc]: ", end='')
    act_set = current_set[cursor].copy()
    ruta = '/ce_scope/probe{}'.format(cursor)
    try:
        ##print(ruta,'\t',act_set)
        OSC_CLIENT.send_message(ruta.encode('utf-8'), act_set)
        print(ruta+"\t{:0.2f}\t{:0.2f}\t{:0.2f}\t{:0.2f}".format(act_set[0], act_set[1], act_set[2], act_set[3]))
    except:
        print("\t ---- \t---- \t---- \t----")
    return

def update_data_send_m2():
    global OSC_CLIENT, current_contours, objects
    print("[contours_osc]: ", end='')

    for (objectID, centroid) in objects.items():
        # set text id
        #print(objectID, centroid)
        text = "obj{}".format(objectID)
        act_set = [int(objectID), int(centroid[0]), int(centroid[1])]
        #print(text, act_set[0], act_set[1], act_set[2])
        ruta = '/ce_scope/obj{}'.format(objectID)
        try:
            ##print(ruta,'\t',act_set)
            OSC_CLIENT.send_message(ruta.encode('utf-8'), act_set)
            print(ruta+"\t{}\t{}\t{}".format(act_set[0], act_set[1], act_set[2]))
        except:
            print("\t---- \t---- \t---- \t----")
    return


# c. osc functions
def serialEvent_data_send(cood):
    global OSC_CLIENT
    ruta = '/ce_scope/joy'
    try:
        OSC_CLIENT.send_message(ruta.encode('utf-8'), [cood])
        print(ruta+"\t{}".format(cood))
    except:
        print("---- ----- ---- ")
    return

# c. osc functions
def stop_start_synth(past_s, act_s):
    global OSC_CLIENT, current_set, cursor
    ruta_stop = '/ce_scope/s{}/stop'.format(past_s)
    ruta_start = '/ce_scope/s{}/start'.format(act_s)
    print("[switch synth] --- ---- --- --- ---- [] ")
    try:
        if (past_s!=0):
            OSC_CLIENT.send_message(ruta_stop.encode('utf-8'), [0])
            print(ruta_stop+"\t{}".format(past_s))
        OSC_CLIENT.send_message(ruta_start.encode('utf-8'), [1])
        print(ruta_start+"\t{}".format(act_s))
    except:
        print("---- ----- ---- ")
    return

# -mapping function
def pmap(value, inMin, inMax, outMin, outMax, clamp=True):
    """ like processing's map """
    inSpan = inMax - inMin
    outSpan = outMax - outMin
    if (clamp):
        if (value<inMin): value = inMin
        if (value>inMax): value = inMax
    try:
        transVal = float(value - inMin) / float(inSpan)
        return outMin + (transVal * outSpan)
    except:
        return 0


# --------------------------------------------------------------------
def check_buttons(_pos):
    #global source_mode, img_stream, 
    global f_count, probe_mode, obj_type, img_stream, video_stream, source_mode, cursor, past_cursor, i_lt, i_ht, low_thresh, hi_thresh, i_blur
    print ("click on {}".format(_pos))
    for j,bt in enumerate(buttons):
        if (bt.collidepoint(_pos)):
            if (j==0):
                print("B2: Going camera")
                source_mode = 2
            elif (j==1):
                print("------------------------------- Análisis de Píxels")
                obj_type = 1
            elif (j==2):
                print("------------------------------- Análisis de Formas")
                obj_type = 2
            elif (j==3):
                print("------------------------------- Análisis de Objetos")
                #obj_type = 0
            elif (j==4):
                print("--[Trayectoria Circular]")
                probe_mode = 0
            elif (j==5):
                print("--[Trayectoria Horizontal]")
                probe_mode = 1
            elif (j==6):
                print("--[Trayectoria Vertical]")
                probe_mode = 2
            elif (j==7):
                print("--[Umbral bajo]: ", end='')
                i_lt = pmap(_pos[0], buttons[7].x, buttons[7].x + buttons[7].w, 0, 1)
                low_thresh = int(i_lt*255)
                print("{}".format(low_thresh))
            elif (j==8):
                print("--[Umbral alto]: ", end='')
                i_ht = pmap(_pos[0], buttons[8].x, buttons[8].x + buttons[8].w, 0, 1)
                hi_thresh = int(i_ht*255)
                print("{}".format(hi_thresh))
            elif (j==9):
                print("--[Parámetro 3]: ", end='')
                par_p03 = int(pmap(_pos[0], buttons[9].x, buttons[9].x + buttons[9].w, 0, 255))
                print("{}".format(par_p03))
    return
# --------------------------------------------------------------------

# f
def handle_events():
    global source_mode, img_stream, video_stream
    event_dict = {
        pygame.QUIT: exit_,
        pygame.KEYDOWN: handle_keys,
        TIC_EVENT: tic,
        pygame.MOUSEBUTTONUP: handle_clicks
        }
    #
    for event in pygame.event.get():
        if event.type in event_dict:
            if (event.type==pygame.KEYDOWN):
                event_dict[event.type](event)
            else:
                event_dict[event.type]()
        elif (event.type == pygame.DROPFILE):
            path = event.file
            print("\n\n---------------------------------------------------")
            print("Archivo: {}".format(path))
            exten = path[path.rfind('.'):].lower()
            if (exten in [".jpg", ".jpeg", ".png"]):
                # load an IMAGE
                try:
                    img_stream = pygame.image.load(path)
                    source_mode = 0
                except:
                    print ("There are errors loading image.")
            elif (exten in [".mp4", ".mpeg", ".avi"]):
                # load a VIDEO
                try:
                    video_stream = cv2.VideoCapture(path)
                    success, video_image = video_stream.read()
                    fps = video_stream.get(cv2.CAP_PROP_FPS)
                    v_clock = pygame.time.Clock()
                    run = success
                    source_mode = 1
                except:
                    print ("There are errors loading video.")
            print("\n\n---------------------------------------------------")

    return

# f
def handle_keys(event):
    global capture, cursor, past_cursor, act_synth, past_synth
    code = 0
    if event.key == K_q:
        capture = False
    #elif event.key == K_s:
    #    pygame.image.save (DISPLAY, FILENAME)
    #elif event.key == K_f:
    #    pygame.display.toggle_fullscreen()
    # the part of the codes
    elif event.key == K_i: #UP
        code=1
    elif event.key == K_l: #RIGTH
        code=2
    elif event.key == K_k: #DOWN
        code=3
    elif event.key == K_j: #LEFT
        code=4
    # check the codes
    if (code>0):
        # send the messahe
        serialEvent_data_send(code)
        # update cursor
        if (code==1):
            if (act_synth<N_SYNTHS):
                past_synth = act_synth
                act_synth = act_synth+1
                stop_start_synth(past_synth, act_synth)
            print("[synth]: {}".format(act_synth))
        elif (code==2):
            if (cursor<N_PROBES-1):
                past_cursor = cursor
                cursor = cursor+1
                #stop_start_synth(past_cursor, cursor)
            print("[probe]: {}".format(cursor))
        elif (code==3):
            if (act_synth>0):
                past_synth = act_synth
                act_synth = act_synth-1
                stop_start_synth(past_synth, act_synth)
            print("[synth]: {}".format(act_synth))
        elif (code==4):
            if (cursor>0):
                past_cursor = cursor
                cursor = cursor-1
                #stop_start_synth(past_cursor, cursor)
            print("[probe]: {}".format(cursor))
    # end handle keys
    return

# f
def handle_clicks():
    pos = pygame.mouse.get_pos()
    check_buttons(pos)
    return

# f tic for the timer
def tic():
    global ii
    if obj_type == 1:
        update_data_send_m1()
    elif obj_type==2:
        update_data_send_m2()
    ii = ii+1
    #print ("\t\t -->   [OSC]")
    return

# f exit
def exit_():
    global capture, serial_read, t
    capture = False
    serial_read = False
    t.join()
    while t.isAlive():
        pass
    print("Thread stopped.")
    #serial_port.close()
    return








def update_graphics_void():
    """ default, no source, no process """
    global BASE, OVERLAY, DISPLAY, current_set
    # update base
    BASE = CAM.get_image(BASE)
    OVERLAY.fill((0, 0, 0, 0))
    pygame.draw.rect(OVERLAY, (0, 0, 32, 255), (0, 0, SIZE[0], SIZE[1]), 0)
        
    pygame.draw.rect(OVERLAY, (0, 255, 0, 255), (300, 250,  200, 140), 3)
    ID_LABEL = FONT.render("| open a source |", 1, (100,100,255))
    OVERLAY.blit(ID_LABEL, (300, 300))

    # render to display
    #DISPLAY.fill(0,0,0)
    DISPLAY.blit(BASE, (of_base))
    DISPLAY.blit(ECHO, (0,0))
    DISPLAY.blit(OVERLAY, (0,0))
    pygame.display.update()
    return



#
of_base = [80,80]
def update_graphics_pixels(mode_select = 2, source_mm = source_mode):
    """ process pixels from camera """
    global BASE, OVERLAY, DISPLAY, current_set
    # update frame
    if source_mm == 2:
        BASE = CAM.get_image(BASE)
    elif source_mm == 0:
        BASE = img_stream
    elif source_mm ==1:
        success, video_image = video_stream.read()
        if success:
            BASE =pygame.image.frombuffer(video_image.tobytes(), video_image.shape[1::-1], "BGR")
    # update overlay
    OVERLAY.fill((0,0,0, 0))
    #pygame.draw.rect(OVERLAY, (255, 255, 255, 128), (0,0,CAM_SIZE[0], CAM_SIZE[1]), 1)
    # black rectangles
    pygame.draw.rect(OVERLAY, (0, 0, 0, 255), (of_base[0]+CAM_SIZE[0],2, of_base[0]-2, of_base[1]+CAM_SIZE[1]-2), 0)
    pygame.draw.rect(OVERLAY, (0, 0, 0, 255), (2, of_base[1]+CAM_SIZE[1], SIZE[0]-4, of_base[1]-20), 0)
    pygame.draw.rect(OVERLAY, (0, 0, 0, 255), (2, 2, SIZE[0]-4, of_base[1]-2), 0)
    #pygame.draw.rect(OVERLAY, (255, 255, 255, 128), (CAM_SIZE[0],0, SIZE[0]-CAM_SIZE[0], SIZE[1]), 1)
    #update for each probe
    r = 0; x = 0; y = 0;
    for i in range (N_PROBES):
        if (mode_select == 0):
            # circular
            r = 59*i
            x = CAM_SIZE[0]/2 + r*math.sin(f_count%360 * 2*math.pi/360)
            y = CAM_SIZE[1]/2 + r*math.cos(f_count%360 * 2*math.pi/360)
        elif(mode_select == 1):
            # horizontal
            r = 59*i
            x = f_count % CAM_SIZE[0]
            y = (i+1) * CAM_SIZE[1]/(N_PROBES+1.0)
        elif(mode_select == 2):
            # horizontal
            r = 59*i
            x = (i+1) * CAM_SIZE[0]/(N_PROBES+1.0)
            y = f_count % CAM_SIZE[1]
        # get the color
        color = BASE.get_at((int(x),int(y)))
        
        #pygame.draw.rect(OVERLAY, (255-color.r, 255-color.g, 255-color.b, 128), (x-5, y-5, 10,10), 0)
        if (i==cursor):
            pygame.draw.rect(OVERLAY, (255-color.r, 255-color.g, 255-color.b, 255), (of_base[0]+x-6, of_base[1]+y-6, 12,12), 3)
            #pygame.draw.rect(ECHO, (0,0,0, 255), (0, 0, 32*5, 3), 0)
            #pygame.draw.rect(ECHO, (255, 255, 255, 255), (32*i, 0, 32, 3), 0)
        else:
            pygame.draw.rect(OVERLAY, (255-color.r, 255-color.g, 255-color.b, 92), (of_base[0]+x-6, of_base[1]+y-6, 12,12), 3)
        pygame.draw.line(OVERLAY,(200,200,200,100),(of_base[0]+x, of_base[1]+y), (of_base[0]+CAM_SIZE[0]+6*i, of_base[1]+y), 1)
        
        of_x = of_base[0]+CAM_SIZE[0]+20
        of_y = of_base[1]
        pygame.draw.rect(ECHO, (color.r, color.g, color.b, 255), (of_x + 6*i, of_y + y-3, 4, 4), 0)
        of_x = of_base[0]
        of_y = of_base[1]+CAM_SIZE[1]+20
        pygame.draw.rect(ECHO, (color.r, color.g, color.b, 255), (of_x + x-3, of_y + 6*i, 4, 4), 0)
        
        st_mean = statistics.mean([color.r, color.g, color.b])/255
        c_data = [color.r/255, color.g/255, color.b/255, st_mean]
        current_set[i] = c_data.copy()
        #DATA_LABEL = FONT.render("{:0.2f}".format(st_mean), 1, color)
        #CHAN_LABEL = FONT.render("CH"+str(i), 1, color)
        #if (i!=4):
        #    OVERLAY.blit(CHAN_LABEL, (CAM_SIZE[0]+4+32*i, CAM_SIZE[1]/2 - 60*i -35))
        #    OVERLAY.blit(DATA_LABEL, (CAM_SIZE[0]+2+32*i, CAM_SIZE[1]/2 - 60*i -18))
        #else: 
        #    OVERLAY.blit(CHAN_LABEL, (CAM_SIZE[0]+4+32*(i-1), CAM_SIZE[1]/2 + 60*i + 3 - 40))
        #    OVERLAY.blit(DATA_LABEL, (CAM_SIZE[0]+2+32*(i-1), CAM_SIZE[1]/2 + 60*i - 20))
    # render to display
    DISPLAY.blit(BASE, (of_base))
    DISPLAY.blit(OVERLAY, (0,0))
    DISPLAY.blit(ECHO, (0,0))
    pygame.display.update()
    return



#
offset_cam = [80,80]
def update_graphics_contours(mode_select = 2, source_mm = source_mode):
    """ process contours from camera """
    global BASE, OVERLAY, DISPLAY, current_set, objects, lo_thresh, hi_thresh, i_lt, i_ht, big_blur
    # update frame
    if source_mm == 2:
        BASE = CAM.get_image(BASE)
    elif source_mm == 0:
        BASE = img_stream
    elif source_mm ==1:
        success, video_image = video_stream.read()
        if success:
            BASE =pygame.image.frombuffer(video_image.tobytes(), video_image.shape[1::-1], "BGR")
    # update overlay
    OVERLAY.fill((0,0,0, 0))
    pygame.draw.rect(OVERLAY, (0, 0, 0, 255), (offset_cam[0]+CAM_SIZE[0],0, offset_cam[0], SIZE[1]), 0)

    # cast to ocv
    view = pygame.surfarray.array3d(BASE)
    view = view.transpose([1, 0, 2])
    frame = cv2.cvtColor(view, cv2.COLOR_RGB2BGR)
    # process on ocv
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7,7), 0)
    gray= cv2.medianBlur(gray, 3)   #to remove salt and paper noise
    gray = 255-gray
    #to binary
    ret,thresh = cv2.threshold(gray,low_thresh,hi_thresh,0)  #to detect white objects
    #outer bound only     
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_GRADIENT, kernel)
    #to strength week pixels
    thresh = cv2.dilate(thresh,kernel,iterations = 5)
    contours,hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    #contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    for k,c in enumerate(contours):
        rect = cv2.boundingRect(c)
        x, y, w, h = rect
        pygame.draw.rect(OVERLAY, (255, 255, 0,255), (offset_cam[0]+x, offset_cam[1]+y, w, h), 1)

    rects = [cv2.boundingRect(c) for c in contours]
    objects = ct.update(rects)

    # loop over the tracked objects
    for (objectID, centroid) in objects.items():
        # set text id
        text = "ID {}".format(objectID)

        #cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
        #    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        #cv2.circle(frame, (centroid[0], centroid[1]),2, (0, 255, 0), -1)
        pygame.draw.rect(OVERLAY, (0, 255, 0, 255), (offset_cam[0]+centroid[0], offset_cam[1]+centroid[1], 5, 5), 3)
        ID_LABEL = FONT.render(text, 1, (0,255,128))
        OVERLAY.blit(ID_LABEL, (offset_cam[0]+ centroid[0]+5, offset_cam[1]+ centroid[1]+5))

    # render to display
    #DISPLAY.fill(0,0,0)
    DISPLAY.blit(BASE, (of_base))
    DISPLAY.blit(OVERLAY, (0,0))
    DISPLAY.blit(ECHO, (0,0))
    pygame.display.update()
    return



def update_text():
    """global nu_datos, serial_port    
    #incoming_line = serial_port.read_until().decode('ascii')
    incoming_line = serial_port.readline().decode('ascii')
    print("[incoming_serial]: {}".format(incoming_line))
    incoming_line.strip().rstrip()
    #vals = [float(v) for v in incoming_line.split(',')]
    if (incoming_line != ""):
        nu_datos = incoming_line
        print("[serial]: {}".format(nu_datos))"""

    # slider bars
    #GUI.fill((0,0,0,0))
    pygame.draw.rect(GUI, colors[0], (buttons[7].x+1, buttons[7].y+1, buttons[7].w-2, buttons[7].h-2), 0)
    pygame.draw.rect(GUI, colors[-1], (buttons[7].x+1, buttons[7].y+1, i_lt*buttons[7].w-2, buttons[7].h-2), 0)
    pygame.draw.rect(GUI, colors[0], (buttons[8].x+1, buttons[8].y+1, buttons[8].w-2, buttons[8].h-2), 0)
    pygame.draw.rect(GUI, colors[-1], (buttons[8].x+1, buttons[8].y+1, i_ht*buttons[8].w-2, buttons[8].h-2), 0)
    for i,la in enumerate(labels):
        GUI.blit(la, (buttons[i].x+5, buttons[i].y+3))
    DISPLAY.blit(GUI, (0,0))
    return




# ---------------------------------------------------------------------------

# the loop from outside
def app_loop():
    global f_count, probe_mode, obj_type, img_stream, video_stream, source_mode, cursor, past_cursor, big_thresh, big_blur
    while capture:
        handle_events()
        #handle_clicks()
        if obj_type == 0:
            update_graphics_void()
        elif obj_type == 1:
            update_graphics_pixels(probe_mode, source_mode)
        elif obj_type == 2:
            update_graphics_contours(ct_mode, source_mode)
        # finally the gui
        update_text()
        #tic()
        clock.tick(12)
        f_count = f_count+1

# the main (init+loop)
def main():
    start_osc()
    pygame.time.set_timer(TIC_EVENT, TIC_TIMER)
    app_loop()
    CAM.stop()
    pygame.quit()
    exit_()
    print("FIN DE LA TRANSMISSION //...")
    
if __name__=="__main__":
    main()
