#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# *
"""
speculative communications SCOPE.analyzer 2023
-----------------------------------------------

Based on scope_v1.5_ pc.py
    + for debugging purposes in the pc + webcam
    + windowed, change probe and synth with keys
    + 4 similar synths, moving along probes

[2023.03.14] ce_scope_a.py
    + 1280 x 720 resolution
    + better window decorators
    + 3 modes: hori, vert, radial
    + specculative communications osc compliant
[2023.03.18] ce_scope_b.py
    + tracker class
    + gui!
[2023.03.18] ce_scope_c.py
    + contours 
    + complete gui
    + source:
        image, video, cam
    + analysis:
        pixels
        contours
        objects
-----------------------------------------------

"""

import pygame
import pygame.camera
from pygame.locals import *
import math, statistics
from oscpy.client import OSCClient
import PySimpleGUI as sg
import os
#import serial
#import threading
import numpy as np
import cv2
from tracker import scTracker


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
#DEVICE = 1
DEVICE = "/dev/video2"
#
CAM_SIZE = (640, 480)
SIZE = (800, 640)
FILENAME = 'capture.png'



#type of detection, 0:pixel, 1:contours
obj_type = 0
#pixel path mode
el_mode = 0
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


# --------------------- otro layout --------------------
p1_column = [
    [
        sg.Text('1. Select Source (img/vid/cam)', size =(250, 1)),
    ],
    [
        sg.T(" "), sg.Text("[a] Load Image: "),
        sg.In(size=(18, 1), enable_events=True, key="-IMG-IN-"),
        sg.FileBrowse("Search", size=(9,1))
    ],
    [
        sg.T(" "), sg.Text("[b] Load Video: "),
        sg.In(size=(18, 1), enable_events=True, key="-VID-IN-"),
        sg.FileBrowse("Search", size=(9,1)),
    ],
    [
        sg.T(" "),sg.Button("[c] Use Camera", size=(40,1), enable_events=True, key="-CAM-IN-")
    ],
    [
        sg.Graph(
            (350, 10), (0, 0), (350, 10),
            background_color='lightblue', key='-GRAPH-'
        )
    ],
    
    [
        sg.T(" "),
    ],
    [
        sg.Text('2. Select Object Type', size =(250, 1)),
    ],
    [
        sg.T(" "),
        sg.Radio('[a] Pixels', "RADIO1", default=True, enable_events=True, key="-mode1-"),
        sg.Radio('[b] Shapes', "RADIO1", default=False, enable_events=True, key="-mode2-"),
        sg.Radio('[c] Objects',"RADIO1", default=False, enable_events=True, key="-mode3-"),
    ],
    [
        sg.T(" "),
    ],
    [
        sg.Text('[a]. Pixels Settings', size =(250, 1)),
    ],

    [
        sg.T(" "),
        sg.Button("Circular", size=(10,1), enable_events=True, key="-moCI-"),
        sg.Button("Horizontal", size=(10,1), enable_events=True, key="-moHO-"),
        sg.Button("Vertical", size=(10,1), enable_events=True, key="-moVE-"),
    ],
    [
        sg.T("Probe: "),
        sg.Radio('[I]', "RADIO1", default=True, enable_events=True, key="-Pr1-"),
        sg.Radio('[II]', "RADIO1", default=False, enable_events=True, key="-Pr2-"),
        sg.Radio('[III]',"RADIO1", default=False, enable_events=True, key="-Pr3-"),
        sg.Radio('[IV]',"RADIO1", default=False, enable_events=True, key="-Pr4-"),
        sg.Radio('[V]',"RADIO1", default=False, enable_events=True, key="-Pr5-"),
    ],
    [
        sg.T(" "),
    ],
    [
        sg.Text('[b]. Shapes Settings', size =(250, 1)),
    ],
    [
        sg.T(" "),
        sg.Text('Threshold', size =(7, 1)), sg.InputText(default_text = "200", size =(6, 1), enable_events=True, key="-SS1-"),
        sg.Text('Blur', size =(7, 1)), sg.InputText(default_text = "3", size =(6, 1), enable_events=True, key="-SS2-"),
        sg.Text('Iters', size =(7, 1)), sg.InputText(default_text = "5", size =(6, 1), enable_events=True, key="-SS3-")
    ],
    [
        sg.T(" "),
    ],
    [
        sg.Text('[c]. Objects Settings', size =(250, 1)),
    ],
    [
        sg.T(" "),
        sg.Text('Param 1', size =(7, 1)), sg.InputText(default_text = "128", size =(6, 1), enable_events=True, key="-SO1-"),
        sg.Text('Param 2', size =(7, 1)), sg.InputText(default_text = "0.5", size =(6, 1), enable_events=True, key="-SO2-"),
        sg.Text('Param 3', size =(7, 1)), sg.InputText(default_text = "255", size =(6, 1), enable_events=True, key="-SO3-")
    ],
    [
        sg.T(" "),
    ],
    [
        sg.Exit()
    ]
]

# ----- Full layout -----
layout = [
            [
                sg.Column(p1_column, size=(400, 500))
            ]
        ]





# --------------------- window layout --------------------
#layout = [[sg.Text(':: Control de Modo e Inicio  ::')],
#          [sg.Graph((400, 10), (0, 0), (400, 10),
#                    background_color='lightblue', key='-GRAPH-')],
#          [sg.Button('mode'), sg.Exit()]]

window = sg.Window('Comunicaciones Especulativas', layout, finalize=True)
graph = window['-GRAPH-']

# -------------- magic code to integrate -----------------
embed = graph.TKCanvas
os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
# change this to 'x11' to make it work on Linux
#os.environ['SDL_VIDEODRIVER'] = 'windib'
os.environ['SDL_VIDEODRIVER'] = 'x11'
# --------------    ------------------   -----------------


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
print(pygame.display.get_driver())
#DISPLAY = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
# invisible cursor
pygame.mouse.set_visible(False)
pygame.display.set_caption(": Speculative Communications :")

# a. start the cam
CAM = pygame.camera.Camera(DEVICE, CAM_SIZE)
CAM.start()
# a. start overlays
#screen = pygame.surface.Surface(SIZE, 0, display)
BASE = pygame.Surface(CAM_SIZE)
OVERLAY = pygame.Surface(SIZE, pygame.SRCALPHA)
ECHO =    pygame.Surface(SIZE, pygame.SRCALPHA)
ECHO.fill((0,0,0,0))

# a. states and counters
clock = pygame.time.Clock()
# timer events
TIC_EVENT = pygame.USEREVENT + 1
#TIC_TIMER = 1000

# b. load stuff, like fonts
FONT_PATH = './RevMiniPixel.ttf'
#FONT_PATH = '/home/pi/W/scope/RevMiniPixel.ttf'
FONT = pygame.font.Font(FONT_PATH, 14)
FONTmini = pygame.font.Font(FONT_PATH, 20)

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
    print("[pixels_osc] --- ---- ----- ---- ")
    act_set = current_set[cursor].copy()
    ruta = '/ce_scope/probe{}'.format(cursor)
    try:
        ##print(ruta,'\t',act_set)
        OSC_CLIENT.send_message(ruta.encode('utf-8'), act_set)
        print(ruta+"\t{:0.2f}\t{:0.2f}\t{:0.2f}\t{:0.2f}".format(act_set[0], act_set[1], act_set[2], act_set[3]))
    except:
        print("---- ----- ---- ")
    return

def update_data_send_m2():
    global OSC_CLIENT, current_contours, objects
    print("[contours_osc] --- ---- ----- ---- ")

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
            print("---- ----- ---- ")
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

# f
def handle_events():
    event_dict = {
        pygame.QUIT: exit_,
        pygame.KEYDOWN: handle_keys,
        TIC_EVENT: tic
        }
    for event in pygame.event.get():
        if event.type in event_dict:
            if (event.type==pygame.KEYDOWN):
                event_dict[event.type](event)
            else:
                event_dict[event.type]()
    return

# f
def handle_keys(event):
    global capture, cursor, past_cursor, act_synth, past_synth
    code = 0
    if event.key == K_q:
        capture = False
    elif event.key == K_s:
        pygame.image.save (DISPLAY, FILENAME)
    elif event.key == K_f:
        pygame.display.toggle_fullscreen()
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
    DISPLAY.blit(OVERLAY, (0,0))
    DISPLAY.blit(ECHO, (0,0))
    pygame.display.update()
    return



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
    pygame.draw.rect(OVERLAY, (0, 0, 0, 255), (of_base[0]+CAM_SIZE[0],0, of_base[0], SIZE[1]), 0)
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



offset_cam = [80,80]
#
def update_graphics_contours(mode_select = 2, source_mm = source_mode):
    """ process contours from camera """
    global BASE, OVERLAY, DISPLAY, current_set, objects, big_thresh, big_blur
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
    gray = cv2.GaussianBlur(gray, (big_blur*2+1, big_blur*2+1), 0)
    gray= cv2.medianBlur(gray, big_blur)   #to remove salt and paper noise
    gray = 255-gray
    #to binary
    ret,thresh = cv2.threshold(gray,big_thresh,255,0)  #to detect white objects
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
    return




# ---------------------------------------------------------------------------

# the loop from outside
def app_loop():
    global f_count, el_mode, obj_type, img_stream, video_stream, source_mode, cursor, past_cursor, big_thresh, big_blur
    while capture:
        # stop
        event, values = window.read(timeout=10)
        # -GUI EVENTS

        # ...detection mode
        if event == '-mode1-':
            obj_type = 1
        elif event == '-mode2-':
            obj_type = 2
        elif event == '-mode3-':
            obj_type = 0

        elif event == '-moCI-':
            el_mode = 0
        elif event == '-moHO-':
            el_mode = 1
        elif event == '-moVE-':
            el_mode = 2

        elif event == '-SS1-':
            try:
                big_thresh = int(values['-SS1-'])
            except:
                print("invalid thresh value")
        elif event == '-SS2-':
            try:
                big_blur = int(values['-SS1-'])
            except:
                print("invalid blur value")
        # ...source mode
        elif event == '-IMG-IN-':
            img_file = values['-IMG-IN-']
            try:
                # load image
                img_stream = pygame.image.load(img_file)
                source_mode = 0
            except:
                print ("There are errors loading image.")
        elif event == '-VID-IN-':
            video_file = values['-VID-IN-']
            try:
                # set video stream
                video_stream = cv2.VideoCapture(video_file)
                success, video_image = video_stream.read()
                fps = video_stream.get(cv2.CAP_PROP_FPS)
                v_clock = pygame.time.Clock()
                run = success
                source_mode = 1
            except:
                print ("There are errors loading video.")
        elif event == '-CAM-IN-':
            source_mode = 2


        # cursor selector
        elif event =='-Pr1-':
            past_cursor = cursor
            cursor = 0
        elif event =='-Pr2-':
            past_cursor = cursor
            cursor = 1
        elif event =='-Pr3-':
            past_cursor = cursor
            cursor = 2
        elif event =='-Pr4-':
            past_cursor = cursor
            cursor = 3
        elif event =='-Pr5-':
            past_cursor = cursor
            cursor = 4

        elif event in (sg.WIN_CLOSED, 'Exit'):
            pygame.quit()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        # go
        handle_events()
        handle_clicks()
        if obj_type == 0:
            update_graphics_void()
        elif obj_type == 1:
            update_graphics_pixels(el_mode, source_mode)
        elif obj_type == 2:
            update_graphics_contours(ct_mode, source_mode)
        update_text()
        tic()
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
