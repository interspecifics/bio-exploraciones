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
import numpy as np
import cv2
from tracker import scTracker
# -


# * --------------------------------------- * #
OSC_HOST = "127.0.0.1"
#OSC_HOST = "192.168.1.84"
OSC_PORT = 9000
OSC_CLIENT = []
OSC_HOST2 = "127.0.0.1"
OSC_PORT2 = 9001
OSC_CLIENT2 = []
# * --------------------------------------- * #
DEVICE = 0
#DEVICE = "/dev/video2"
# * --------------------------------------- * #
CAM_SIZE = (640, 480)
SIZE = (800, 640)
SIZE = (800, 800)
WI, HE = SIZE
FILENAME = 'capture.png'

TIC_TIMER = 250
# * --------------------------------------- * #

# * --------------------------------------- * #
obj_type = 1        # 1:pixel, 2:contours
send_all_probes = False
probe_mode = 0      #pixel path mode
ct_mode = 0         #contour mode
cont_rev = True
cont_view = False
# -
source_mode = 2     #0:img, 1:vid, 2:cam
img_stream = None
video_stream = None
ffcc = 0            # video frame counter
# -
current_contours = [[0,0,0,0]]
objects = {}
# * --------------------------------------- * #
ct = scTracker()
(H, W) = (640, 480)
kernel = np.ones((2,2),np.uint8)
# * --------------------------------------- * #


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
pygame.display.set_caption(": [interspecifics / comunicaciones especulativas] : S C O P E :")

# a. start the cam
CAM = pygame.camera.Camera(DEVICE, CAM_SIZE)
CAM.start()
# a. start overlays
#screen = pygame.surface.Surface(SIZE, 0, display)
BASE = pygame.Surface(CAM_SIZE, pygame.SRCALPHA)
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
FONTbig = pygame.font.Font(FONT_PATH, 20)
FONT = pygame.font.Font(FONT_PATH, 14)
FONTmed = pygame.font.Font(FONT_PATH, 10)
FONTmini = pygame.font.Font(FONT_PATH, 8)

# b. icon
pygame_icon = pygame.image.load('icon.png')
pygame.display.set_icon(pygame_icon)

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
# D2 .contour rev
rb_cont2 = [315, 760, 80, 20]
btn_cont2 = pygame.draw.rect(GUI, colors[3], pygame.Rect(rb_cont2), 1)
buttons.append(btn_cont2) #- 9
# E2 .contour view
rb_cont3 = [405, 760, 80, 20]
btn_cont3 = pygame.draw.rect(GUI, colors[3], pygame.Rect(rb_cont3), 1)
buttons.append(btn_cont3) #- 10
# ------------------------------------------------------------------
# E0 .contour thresh 1
rb_obj0 = [315, 700, 170, 20]
btn_obj0 = pygame.draw.rect(GUI, colors[3], pygame.Rect(rb_obj0), 1)
buttons.append(btn_obj0) #- 11
# E1 .contour thresh 2
rb_obj1 = [315, 730, 170, 20]
btn_obj1 = pygame.draw.rect(GUI, colors[3], pygame.Rect(rb_obj1), 1)
buttons.append(btn_obj1) #- 12
# E2 .contour reverse
rb_obj2 = [315, 760, 80, 20]
btn_obj2 = pygame.draw.rect(GUI, colors[3], pygame.Rect(rb_obj2), 1)
buttons.append(btn_obj2) #- 13
# E2 .contour view
rb_obj3 = [405, 760, 80, 20]
btn_obj3 = pygame.draw.rect(GUI, colors[3], pygame.Rect(rb_obj3), 1)
buttons.append(btn_obj3) #- 14

#LABELS
titles = [
    "Cámara",
    "Pixels",
    "Formas",
    "Rastreo",
    "Circular",
    "Horizontal",
    "Vertical",
    "Thresh_A",
    "Thresh_B",
    "Reverse",
    "View"
    ]
labels = [FONT.render(ti, 1, colors[1]) for ti in titles]
#self.labels["norm"] = [_fonts[2].render("N", 1, color_text_2 if self.state['norm'] else self.color), [posit[0]-200, posit[1]+15]]
i_lt = 0.75
i_ht = 1.0
hi_thresh = 192
low_thresh = 255
# ------------------------------------------------------------------

linked_id = None
linked_ids = [None, None, None]
insert_index = 1
# ------------------------------------------------------------------




# c. osc functions
def start_osc(osc_host = OSC_HOST, osc_port = OSC_PORT, osc_host2 = OSC_HOST2, osc_port2 = OSC_PORT2):
    global OSC_CLIENT, OSC_CLIENT2
    OSC_CLIENT = OSCClient(osc_host, osc_port)
    OSC_CLIENT2 = OSCClient(osc_host2, osc_port2)
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
    global OSC_CLIENT, OSC_CLIENT2, current_set, cursor, act_synth
    print("[pixels_osc]: ", end='')
    act_set = current_set[cursor].copy()
    ruta = '/ce_scope/probe{}'.format(cursor)
    try:
        ##print(ruta,'\t',act_set)
        OSC_CLIENT.send_message(ruta.encode('utf-8'), act_set)
        OSC_CLIENT2.send_message(ruta.encode('utf-8'), act_set)
        print(ruta+"\t{:0.2f}\t{:0.2f}\t{:0.2f}\t{:0.2f}".format(act_set[0], act_set[1], act_set[2], act_set[3]))
    except:
        print("\t ---- \t---- \t---- \t----")
    return

def update_data_send_m1_all():
    global OSC_CLIENT, OSC_CLIENT2, current_set, cursor, act_synth
    for i in range(N_PROBES):
        act_set = current_set[i].copy()
        ruta = '/ce_scope/probe{}'.format(i)
        try:
            ##print(ruta,'\t',act_set)
            OSC_CLIENT.send_message(ruta.encode('utf-8'), act_set)
            OSC_CLIENT2.send_message(ruta.encode('utf-8'), act_set)
            print(ruta+"\t{:0.2f}\t{:0.2f}\t{:0.2f}\t{:0.2f}".format(act_set[0], act_set[1], act_set[2], act_set[3]))
        except:
            print("\t ---- \t---- \t---- \t----")
    return

def update_data_send_m2():
    global OSC_CLIENT, OSC_CLIENT2, current_contours, objects
    print("[contours_osc]: ")

    id_min = 1000
    id_max = 0
    for (objectID, centroid) in objects.items():
        # get min and max index
        if objectID<id_min: id_min = objectID
        if objectID>id_max: id_max = objectID
        #print(objectID, centroid)
        text = "obj{}".format(objectID)
        act_set = [int(objectID), int(centroid[0]), int(centroid[1])]
        #print(text, act_set[0], act_set[1], act_set[2])
        #ruta = '/ce_scope/obj{}'.format(objectID)
        ruta = '/ce_scope/obj'
        try:
            ##print(ruta,'\t',act_set)
            OSC_CLIENT.send_message(ruta.encode('utf-8'), act_set)
            OSC_CLIENT2.send_message(ruta.encode('utf-8'), act_set)
            print(ruta+"\t{}\t{}\t{}".format(act_set[0], act_set[1], act_set[2]))
        except:
            print("\t---- \t---- \t---- \t----")
    # range
    ruta = '/ce_scope/range'
    range_set = [id_min, id_max, len(objects.items())]
    try:
        ##print(ruta,'\t',act_set)
        OSC_CLIENT.send_message(ruta.encode('utf-8'), range_set)
        OSC_CLIENT2.send_message(ruta.encode('utf-8'), range_set)
        print(ruta+"\t{}\t{}\t{}".format(range_set[0], range_set[1], range_set[2]))
    except:
        print("\t---- \t---- \t---- \t----")

    return

def update_data_send_m3():
    global OSC_CLIENT, OSC_CLIENT2, current_contours, objects, linked_id
    #print("[channels_osc]: ")
    """
    objectID = linked_id
    #centroid = objects[linked_id]
    try:
        centroid = objects[objectID]
        ##print(ruta,'\t',act_set)
        act_set = [int(objectID), int(centroid[0]), int(centroid[1])]
        ruta = '/ce_scope/A'.format(objectID)
        OSC_CLIENT.send_message(ruta.encode('utf-8'), act_set)
        print(ruta+"\t{}\t{}\t{}".format(act_set[0], act_set[1], act_set[2]))
    except:
        a = 1
        #print("\t---- \t---- \t---- \t----")
    """
    ####
    for j,lid in enumerate(linked_ids):
        if lid is not None:
            objectID = lid
            #centroid = objects[linked_id]
            try:
                centroid = objects[objectID]
                ##print(ruta,'\t',act_set)
                act_set = [int(objectID), int(centroid[0]), int(centroid[1])]
                ruta = '/ce_scope/CH{}'.format(j+1)
                OSC_CLIENT.send_message(ruta.encode('utf-8'), act_set)
                OSC_CLIENT2.send_message(ruta.encode('utf-8'), act_set)
                print(ruta+"\t{}\t{}\t{}".format(act_set[0], act_set[1], act_set[2]))
            except:
                a = 1
                #print("\t---- \t---- \t---- \t----")

    return


# c. osc functions
def serialEvent_data_send(cood):
    global OSC_CLIENT, OSC_CLIENT2
    ruta = '/ce_scope/joy'
    try:
        OSC_CLIENT.send_message(ruta.encode('utf-8'), [cood])
        OSC_CLIENT2.send_message(ruta.encode('utf-8'), [cood])
        print(ruta+"\t{}".format(cood))
    except:
        print("---- ----- ---- ")
    return

# c. osc functions
def stop_start_synth(past_s, act_s):
    global OSC_CLIENT, OSC_CLIENT2, current_set, cursor
    ruta_stop = '/ce_scope/s{}/stop'.format(past_s)
    ruta_start = '/ce_scope/s{}/start'.format(act_s)
    print("[switch synth] --- ---- --- --- ---- [] ")
    try:
        if (past_s!=0):
            OSC_CLIENT.send_message(ruta_stop.encode('utf-8'), [0])
            OSC_CLIENT2.send_message(ruta_stop.encode('utf-8'), [0])
            print(ruta_stop+"\t{}".format(past_s))
        OSC_CLIENT.send_message(ruta_start.encode('utf-8'), [1])
        OSC_CLIENT2.send_message(ruta_start.encode('utf-8'), [1])
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
def check_unbuttons(_pos):
    #global source_mode, img_stream, 
    global f_count, probe_mode, obj_type, img_stream, video_stream, source_mode, cursor, past_cursor, i_lt, i_ht, low_thresh, hi_thresh, i_blur, cont_rev, cont_view, objects
    print ("unclick on {}".format(_pos))
    was_button = False
    for j,bt in enumerate(buttons):
        if (bt.collidepoint(_pos)):
            if (j==0):
                print("B2: Going camera")
                source_mode = 2
                try:
                    CAM.start()
                    print ("[camera]: ON")
                except:
                    print ("can't start camera")

                ECHO.fill((0,0,0, 0))
            elif (j==1):
                print("------------------------------- Análisis de Píxels")
                obj_type = 1
                ECHO.fill((0,0,0, 0))
            elif (j==2):
                print("------------------------------- Análisis de Formas")
                obj_type = 2
                ECHO.fill((0,0,0, 0))
                low_thresh = 192
                i_lt = 0.75
                hi_thresh = 255
                i_ht = 1.0
            elif (j==3):
                print("------------------------------- Objetos via channels")
                obj_type = 3
                ECHO.fill((0,0,0, 0))
                low_thresh = 192
                i_lt = 0.75
                hi_thresh = 255
                i_ht = 1.0
                print("[channels_osc]: ")
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
                print("--[Reverse]: ", end='')
                cont_rev = not cont_rev
                #par_p03 = int(pmap(_pos[0], buttons[9].x, buttons[9].x + buttons[9].w, 0, 255))
                print("{}".format(cont_rev))
            elif (j==10):
                print("--[View Contours]: ", end='')
                cont_view = not cont_view
                print("{}".format(cont_view))
            was_button = True
    """
    if not was_button and obj_type==2:
        #si no fue un boton, entonces revisa cuál es el objeto más cercano
        list_of_indexes = []
        list_of_centroids = []
        for (objectID, centroid) in objects.items():
            list_of_indexes.append(objectID)
            list_of_centroids.append((centroid[0], centroid[1]))
        array_of_centroids = np.array(list_of_centroids)
        pos_clic = np.array(_pos)
        distances = np.linalg.norm(array_of_centroids-pos_clic, axis=1)
        closest_index = np.argmin(distances)
        print("\n\nclic: el objeto más cercano es {} at {}\n\n".format(list_of_indexes[closest_index], list_of_centroids[closest_index]))
    """
    return

def check_buttons(_pos):
    #global source_mode, img_stream, 
    global f_count, probe_mode, obj_type, img_stream, video_stream, source_mode, cursor, past_cursor, i_lt, i_ht, low_thresh, hi_thresh, i_blur, cont_rev, cont_view, objects, linked_id
    print ("click on {}".format([_pos[0]-80,_pos[1]-80]))
    was_button = False
    # check for clic buttons
    for j,bt in enumerate(buttons):
        if (bt.collidepoint(_pos)):
            was_button = True
    # if not
    if not was_button and obj_type==3 and _pos[0]>80 and _pos[0]<80+CAM_SIZE[0] and _pos[1]>80 and _pos[1]<80+CAM_SIZE[1] :
        #si no fue un boton, entonces revisa cuál es el objeto más cercano
        list_of_indexes = []
        list_of_centroids = []
        for (objectID, centroid) in objects.items():
            list_of_indexes.append(objectID)
            list_of_centroids.append((centroid[0], centroid[1]))
        if (len(list_of_centroids)>0):
            array_of_centroids = np.array(list_of_centroids)
            pos_clic = np.array([_pos[0]-80, _pos[1]-80])
            distances = np.linalg.norm(array_of_centroids-pos_clic, axis=1)
            closest_index = np.argmin(distances)
            if (distances[closest_index]<100):            
                print("\n\nclic: el objeto más cercano es {} at {}, dist:{}\n\n".format(list_of_indexes[closest_index], list_of_centroids[closest_index], distances[closest_index]))
                linked_id = list_of_indexes[closest_index]
                linked_ids[insert_index-1] = list_of_indexes[closest_index]
    return
# --------------------------------------------------------------------

# f
def handle_events():
    global source_mode, img_stream, video_stream, ffcc
    event_dict = {
        pygame.QUIT: exit_,
        pygame.KEYDOWN: handle_keys,
        TIC_EVENT: tic,
        pygame.MOUSEBUTTONUP: handle_unclicks,
        pygame.MOUSEBUTTONDOWN: handle_clicks
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
                try:
                    CAM.stop()
                    print ("[camera]: OFF")
                except:
                    print ("can't stop camera")
                # load an IMAGE
                try:
                    img_stream = pygame.image.load(path)
                    source_mode = 0
                except:
                    print ("There are errors loading image.")
            elif (exten in [".mp4", ".mpeg", ".avi"]):
                try:
                    CAM.stop()
                    print ("[camera]: OFF")
                except:
                    print ("can't stop camera")
                # load a VIDEO
                try:
                    video_stream = cv2.VideoCapture(path)
                    success, video_image = video_stream.read()
                    fps = video_stream.get(cv2.CAP_PROP_FPS)
                    v_clock = pygame.time.Clock()
                    run = success
                    ffcc = 0
                    source_mode = 1
                except:
                    print ("There are errors loading video.")
            print("\n\n---------------------------------------------------")

    return

# f
def handle_keys(event):
    global capture, cursor, past_cursor, act_synth, past_synth, send_all_probes, insert_index
    code = 0
    if event.key == K_q:
        capture = False
    if event.key == K_a:
        send_all_probes = not send_all_probes
    #elif event.key == K_s:
    #    pygame.image.save (DISPLAY, FILENAME)
    #elif event.key == K_f:
    #    pygame.display.toggle_fullscreen()
    # the part of the codes
    #elif event.key == K_i: #UP
    #    code=1
    elif event.key == K_l: #RIGTH
        code=2
    #elif event.key == K_k: #DOWN
    #    code=3
    elif event.key == K_j: #LEFT
        code=4
    elif event.key == K_1: #insert on linked_ids[0]
        insert_index = 1
    elif event.key == K_2: #insert on linked_ids[1]
        insert_index = 2
    elif event.key == K_3: #insert on linked_ids[2]
        insert_index = 3
    # check the codes
    if (code>0):
        # send the messahe
        # serialEvent_data_send(code)
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
def handle_unclicks():
    pos = pygame.mouse.get_pos()
    check_unbuttons(pos)
    return

def handle_clicks():
    pos = pygame.mouse.get_pos()
    check_buttons(pos)
    return

# f tic for the timer
def tic():
    global ii
    if obj_type == 1:
        if (send_all_probes):
            update_data_send_m1_all()
        else:
            update_data_send_m1()
    elif obj_type==2:
        update_data_send_m2()
    elif obj_type==3:
        update_data_send_m3()
    ii = ii+1
    #print ("\t\t -->   [OSC]")
    return

# f exit
def exit_():
    global capture, serial_read, t
    capture = False
    serial_read = False
    return

def put_alpha(Dest, Src): 
    """ write alpha values """
    ref = pygame.surfarray.pixels_alpha(Dest)
    np.copyto(ref, Src) 
    del ref



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
    global BASE, OVERLAY, DISPLAY, current_set, ffcc, send_all_probes
    # update frame
    if source_mm == 2:
        BASE = CAM.get_image(BASE)
    elif source_mm == 0:
        BASE = img_stream
    elif source_mm ==1:
        success, video_image = video_stream.read()
        if success:
            BASE =pygame.image.frombuffer(video_image.tobytes(), video_image.shape[1::-1], "BGR")
            ffcc+=1
            if (ffcc == video_stream.get(cv2.CAP_PROP_FRAME_COUNT)-2):
                print("-----------------------------------------------------restarting")
                ffcc = 0
                video_stream.set(cv2.CAP_PROP_POS_FRAMES, 0)
                success, video_image = video_stream.read()
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
        if send_all_probes:
            pygame.draw.rect(OVERLAY, (0, 255, 0, 255), (of_base[0]+x-6, of_base[1]+y-6, 12,12), 3)
        else:
            if (i==cursor):
                pygame.draw.rect(OVERLAY, (0, 255, 0, 255), (of_base[0]+x-6, of_base[1]+y-6, 12,12), 3)
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
    global BASE, OVERLAY, DISPLAY, current_set, objects, lo_thresh, hi_thresh, i_lt, i_ht, big_blur, ffcc, video_image
    # update frame
    if source_mm == 2:
        BASE = CAM.get_image(BASE)
    elif source_mm == 0:
        BASE = img_stream
        BASE = pygame.Surface.convert_alpha(BASE)
    elif source_mm ==1:
        success, video_image = video_stream.read()
        if success:
            BASE = pygame.image.frombuffer(video_image.tobytes(), video_image.shape[1::-1], "BGR")
            BASE = pygame.Surface.convert_alpha(BASE)
            ffcc+=1
            if (ffcc == video_stream.get(cv2.CAP_PROP_FRAME_COUNT)-2):
                ffcc = 0
                video_stream.set(cv2.CAP_PROP_POS_FRAMES, 0)
                success, video_image = video_stream.read()
                BASE = pygame.image.frombuffer(video_image.tobytes(), video_image.shape[1::-1], "BGR")
                BASE = pygame.Surface.convert_alpha(BASE)
            #continue
    # update overlay
    OVERLAY.fill((0,0,0, 0))
    #pygame.draw.rect(OVERLAY, (255, 255, 255, 128), (0,0,CAM_SIZE[0], CAM_SIZE[1]), 1)
    # black rectangles
    pygame.draw.rect(OVERLAY, (0, 0, 0, 255), (of_base[0]+CAM_SIZE[0],2, of_base[0]-2, of_base[1]+CAM_SIZE[1]-2), 0)
    pygame.draw.rect(OVERLAY, (0, 0, 0, 255), (2, of_base[1]+CAM_SIZE[1], SIZE[0]-4, of_base[1]-20), 0)
    pygame.draw.rect(OVERLAY, (0, 0, 0, 255), (2, 2, SIZE[0]-4, of_base[1]-2), 0)
    # 
    # cast to ocv
    view = pygame.surfarray.array3d(BASE)
    view = view.transpose([1, 0, 2])
    frame = cv2.cvtColor(view, cv2.COLOR_RGB2BGR)

    # process on ocv
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5,5), 0)
    #gray= cv2.medianBlur(gray, 5)   #to remove salt and paper noise

    alpha = 1.5 # Contrast control (1.0-3.0)
    beta = 0 # Brightness control (0-100)
    gray = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)

    #to binary
    if (cont_rev==True):
        #gray = 255-gray
        ret,thresh = cv2.threshold(gray,low_thresh,hi_thresh,0)  #to detect white objects
    else:
        ret,thresh = cv2.threshold(gray,low_thresh,hi_thresh,1)  #to detect white objects
    #outer bound only 
    #thresh = cv2.morphologyEx(thresh, cv2.MORPH_GRADIENT, kernel)
    #to strength week pixels
    #thresh = cv2.dilate(thresh,kernel,iterations = 5)
    contours,hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    #contours, _ = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE) 
    contours = sorted(contours, key=cv2.contourArea, reverse=True) 
    if cont_view:
        nonview = cv2.bitwise_and(frame,frame, mask = thresh)
        BASE = pygame.image.frombuffer(nonview.tobytes(), nonview.shape[1::-1], "BGR")
        BASE = pygame.Surface.convert_alpha(BASE)
    #
 
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
    #DISPLAY.blit(non_view, (of_base))
    DISPLAY.blit(OVERLAY, (0,0))
    DISPLAY.blit(ECHO, (0,0))
    pygame.display.update()
    return



#
offset_cam = [80,80]
def update_graphics_channels(mode_select = 2, source_mm = source_mode):
    """ select some objects to channel"""
    global BASE, OVERLAY, DISPLAY, current_set, objects, lo_thresh, hi_thresh, i_lt, i_ht, big_blur, ffcc, video_image
    # 1. ----------------------------------------- update frame
    if source_mm == 2:
        BASE = CAM.get_image(BASE)
    elif source_mm == 0:
        BASE = img_stream
        BASE = pygame.Surface.convert_alpha(BASE)
    elif source_mm == 1:
        success, video_image = video_stream.read()
        if success:
            BASE = pygame.image.frombuffer(video_image.tobytes(), video_image.shape[1::-1], "BGR")
            BASE = pygame.Surface.convert_alpha(BASE)
            ffcc+=1
            if (ffcc == video_stream.get(cv2.CAP_PROP_FRAME_COUNT)-2):
                ffcc = 0
                video_stream.set(cv2.CAP_PROP_POS_FRAMES, 0)
                success, video_image = video_stream.read()
                BASE = pygame.image.frombuffer(video_image.tobytes(), video_image.shape[1::-1], "BGR")
                BASE = pygame.Surface.convert_alpha(BASE)
    OVERLAY.fill((0,0,0, 0))
    # black rectangles
    pygame.draw.rect(OVERLAY, (0, 0, 0, 255), (of_base[0]+CAM_SIZE[0],2, of_base[0]-2, of_base[1]+CAM_SIZE[1]-2), 0)
    pygame.draw.rect(OVERLAY, (0, 0, 0, 255), (2, of_base[1]+CAM_SIZE[1], SIZE[0]-4, of_base[1]-20), 0)
    pygame.draw.rect(OVERLAY, (0, 0, 0, 255), (2, 2, SIZE[0]-4, of_base[1]-2), 0)
    # 1. ----------------------------------------- end update frame
    # 2. ----------------------------------------- cast to ocv
    view = pygame.surfarray.array3d(BASE)
    view = view.transpose([1, 0, 2])
    frame = cv2.cvtColor(view, cv2.COLOR_RGB2BGR)

    # process on ocv
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5,5), 0)
    #gray= cv2.medianBlur(gray, 5)   #to remove salt and paper noise

    alpha = 1.5 # Contrast control (1.0-3.0)
    beta = 0 # Brightness control (0-100)
    gray = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)

    #to binary
    if (cont_rev==True):
        #gray = 255-gray
        ret,thresh = cv2.threshold(gray,low_thresh,hi_thresh,0)  #to detect white objects
    else:
        ret,thresh = cv2.threshold(gray,low_thresh,hi_thresh,1)  #to detect white objects
    #outer bound only 
    #thresh = cv2.morphologyEx(thresh, cv2.MORPH_GRADIENT, kernel)
    #to strength week pixels
    #thresh = cv2.dilate(thresh,kernel,iterations = 5)
    #contours,hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contours, _ = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE) 
    contours = sorted(contours, key=cv2.contourArea, reverse=True) 
    #
    if cont_view:
        nonview = cv2.bitwise_and(frame,frame, mask = thresh)
        BASE = pygame.image.frombuffer(nonview.tobytes(), nonview.shape[1::-1], "BGR")
        BASE = pygame.Surface.convert_alpha(BASE)
    # 2. ----------------------------------------- end cast to ocv
 
    # 3. ----------------------------------------- tracking
    for k,c in enumerate(contours[1:31]):
        rect = cv2.boundingRect(c)
        x, y, w, h = rect
        pygame.draw.rect(OVERLAY, (255, 255, 0,192), (offset_cam[0]+x, offset_cam[1]+y, w, h), 1)
    # UPDATE with current rectangles
    if (len(contours)>1):
        rects = [cv2.boundingRect(c) for c in contours[1:31]]
        objects = ct.update(rects)
    # loop over the tracked objects.items()
    id_min = 100
    id_max = 0
    for (objectID, centroid) in objects.items():
        if objectID<id_min: id_min = objectID
        if objectID>id_max: id_max = objectID
        # set text id
        text = "ID {}".format(objectID)
        # draw the marks
        coloro = (255, 255, 255, 255)
        colored = False
        for j, lid in enumerate(linked_ids):
            if objectID==lid:
                if (j==0):
                    colored = True
                    coloro = (255, 0, 0, 255)
                    pygame.draw.rect(OVERLAY, coloro, (offset_cam[0]+centroid[0], offset_cam[1]+centroid[1], 5, 5), 3)
                elif (j==1):
                    colored = True
                    coloro = (0, 255, 0, 255)
                    pygame.draw.rect(OVERLAY, coloro, (offset_cam[0]+centroid[0], offset_cam[1]+centroid[1], 5, 5), 3)
                elif (j==2):
                    colored = True
                    coloro = (0, 128, 255, 255)
                    pygame.draw.rect(OVERLAY, coloro, (offset_cam[0]+centroid[0], offset_cam[1]+centroid[1], 5, 5), 3)
                ID_LABEL = FONTbig.render(text, 1, coloro)
        if not colored:
            coloro = (255, 255, 255, 255)
            pygame.draw.rect(OVERLAY, coloro, (offset_cam[0]+centroid[0], offset_cam[1]+centroid[1], 5, 5), 3)
            ID_LABEL = FONT.render(text, 1, coloro)
        OVERLAY.blit(ID_LABEL, (offset_cam[0]+ centroid[0]+5, offset_cam[1]+ centroid[1]+5))
    # 3. ----------------------------------------- end tracking
    """
    i want to associate an ID to a fixed channel
    objects is an ordered dict, id(int): centroid([int, int])
    """
    #
    #print ("current objects: {}, min: {},{}, max: {},{}".format(len(objects.items()), id_min, objects[id_min],id_max, objects[id_max]))
    
    # render to display
    #DISPLAY.fill(0,0,0)
    DISPLAY.blit(BASE, (of_base))
    DISPLAY.blit(OVERLAY, (0,0))
    DISPLAY.blit(ECHO, (0,0))
    pygame.display.update()
    return


def update_text():
    """
    global nu_datos, serial_port    
    #incoming_line = serial_port.read_until().decode('ascii')
    incoming_line = serial_port.readline().decode('ascii')
    print("[incoming_serial]: {}".format(incoming_line))
    incoming_line.strip().rstrip()
    #vals = [float(v) for v in incoming_line.split(',')]
    if (incoming_line != ""):
        nu_datos = incoming_line
        print("[serial]: {}".format(nu_datos))
    """

    # slider bars
    #GUI.fill((0,0,0,0))
    pygame.draw.rect(GUI, colors[0], (buttons[7].x+1, buttons[7].y+1, buttons[7].w-2, buttons[7].h-2), 0)
    pygame.draw.rect(GUI, colors[-1], (buttons[7].x+1, buttons[7].y+1, i_lt*buttons[7].w-2, buttons[7].h-2), 0)
    pygame.draw.rect(GUI, colors[0], (buttons[8].x+1, buttons[8].y+1, buttons[8].w-2, buttons[8].h-2), 0)
    pygame.draw.rect(GUI, colors[-1], (buttons[8].x+1, buttons[8].y+1, i_ht*buttons[8].w-2, buttons[8].h-2), 0)
    if obj_type==1:
        pygame.draw.rect(GUI, colors[-1], (buttons[1].x+1, buttons[1].y+1, buttons[1].w-2, buttons[1].h-2), 0)
        pygame.draw.rect(GUI, colors[0], (buttons[2].x+1, buttons[2].y+1, buttons[2].w-2, buttons[2].h-2), 0)
        pygame.draw.rect(GUI, colors[0], (buttons[3].x+1, buttons[3].y+1, buttons[3].w-2, buttons[3].h-2), 0)
    elif obj_type==2:
        pygame.draw.rect(GUI, colors[0], (buttons[1].x+1, buttons[1].y+1, buttons[1].w-2, buttons[1].h-2), 0)
        pygame.draw.rect(GUI, colors[-1], (buttons[2].x+1, buttons[2].y+1, buttons[2].w-2, buttons[2].h-2), 0)
        pygame.draw.rect(GUI, colors[0], (buttons[3].x+1, buttons[3].y+1, buttons[3].w-2, buttons[3].h-2), 0)
    elif obj_type==3:
        pygame.draw.rect(GUI, colors[0], (buttons[1].x+1, buttons[1].y+1, buttons[1].w-2, buttons[1].h-2), 0)
        pygame.draw.rect(GUI, colors[0], (buttons[2].x+1, buttons[2].y+1, buttons[2].w-2, buttons[2].h-2), 0)
        pygame.draw.rect(GUI, colors[-1], (buttons[3].x+1, buttons[3].y+1, buttons[3].w-2, buttons[3].h-2), 0)
    if probe_mode==0:
        pygame.draw.rect(GUI, colors[-1], (buttons[4].x+1, buttons[4].y+1, buttons[4].w-2, buttons[4].h-2), 0)
        pygame.draw.rect(GUI, colors[0], (buttons[5].x+1, buttons[5].y+1, buttons[5].w-2, buttons[5].h-2), 0)
        pygame.draw.rect(GUI, colors[0], (buttons[6].x+1, buttons[6].y+1, buttons[6].w-2, buttons[6].h-2), 0)
    elif probe_mode==1:
        pygame.draw.rect(GUI, colors[0], (buttons[4].x+1, buttons[4].y+1, buttons[4].w-2, buttons[4].h-2), 0)
        pygame.draw.rect(GUI, colors[-1], (buttons[5].x+1, buttons[5].y+1, buttons[5].w-2, buttons[5].h-2), 0)
        pygame.draw.rect(GUI, colors[0], (buttons[6].x+1, buttons[6].y+1, buttons[6].w-2, buttons[6].h-2), 0)
    elif probe_mode==2:
        pygame.draw.rect(GUI, colors[0], (buttons[4].x+1, buttons[4].y+1, buttons[4].w-2, buttons[4].h-2), 0)
        pygame.draw.rect(GUI, colors[0], (buttons[5].x+1, buttons[5].y+1, buttons[5].w-2, buttons[5].h-2), 0)
        pygame.draw.rect(GUI, colors[-1], (buttons[6].x+1, buttons[6].y+1, buttons[6].w-2, buttons[6].h-2), 0)    
    if cont_rev:
        pygame.draw.rect(GUI, colors[-1], (buttons[9].x+1, buttons[9].y+1, buttons[9].w-2, buttons[9].h-2), 0)
    else:
        pygame.draw.rect(GUI, colors[0], (buttons[9].x+1, buttons[9].y+1, buttons[9].w-2, buttons[9].h-2), 0)        
    if cont_view:
        pygame.draw.rect(GUI, colors[-1], (buttons[10].x+1, buttons[10].y+1, buttons[10].w-2, buttons[10].h-2), 0)
    else:
        pygame.draw.rect(GUI, colors[0], (buttons[10].x+1, buttons[10].y+1, buttons[10].w-2, buttons[10].h-2), 0)
    for i,la in enumerate(labels):
        GUI.blit(la, (buttons[i].x+5, buttons[i].y+3))
    DISPLAY.blit(GUI, (0,0))
    return




# ---------------------------------------------------------------------------

# the loop from outside
def app_loop():
    global f_count, probe_mode, obj_type, img_stream, video_stream, source_mode, cursor, past_cursor
    while capture:
        handle_events()
        #handle_clicks()
        if obj_type == 0:
            update_graphics_void()
        elif obj_type == 1:
            update_graphics_pixels(probe_mode, source_mode)
        elif obj_type == 2:
            update_graphics_contours(ct_mode, source_mode)
        elif obj_type == 3:
            update_graphics_channels(ct_mode, source_mode)
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
