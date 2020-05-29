import pygame as p
import math   as m
from   PIL import Image, ImageDraw
from pygame import gfxdraw


FOV, FOV_STEP, LENGHT_STEP, MAX_LENGHT = 1., .00375, .01, 50.
prespeed   = .08
rotate     = .1
px, py, pa = 1.5, 2.5, 6.28
pspeed     = .25

WID, HEI = 320, 200
win = p.display.set_mode((WID, HEI), p.FULLSCREEN)

dWID   = 261
dHEI   = 160
dWIDs  = (WID - dWID) // 2
dHEIs  = 10
mulHEI = 1.5

FOV_STEP = FOV / (dWID + 1)

win.fill((50, 50, 50))

lighting       = True
dark_wall_side = 125
dark_wall_x    = True
lightQ         = 1.4

walls = {1 : 'data/stone_wall.bmp',
         2 : 'data/blue_wall.bmp',
         3 : 'data/brick_wall.bmp',
         4 : 'data/wood_wall.bmp'}

MAP = [[1, 1, 1, 1, 1, 2, 2, 2, 2, 2],
       [1, 0, 0, 0, 1, 2, 0, 0, 0, 2],
       [1, 0, 0, 0, 0, 0, 0, 0, 0, 2],
       [1, 0, 0, 0, 1, 2, 0, 0, 0, 2],
       [1, 1, 0, 1, 1, 2, 2, 0, 2, 2],
       [4, 4, 0, 4, 4, 3, 3, 0, 3, 3],
       [4, 0, 0, 0, 4, 3, 0, 0, 0, 3],
       [4, 0, 0, 0, 0, 0, 0, 0, 0, 3],
       [4, 0, 0, 0, 4, 3, 0, 0, 0, 3],
       [4, 4, 4, 4, 4, 3, 3, 3, 3, 3]]

roof_color, floor_color = (56, 56, 56), (112, 112, 112)

redraw = True

p.mouse.set_visible(False)
p.mouse.set_pos((dWIDs + dWID // 2, dHEIs + dHEI // 2))
mouse_speed = .001

def moving(x, y, ang):
    ystep = y + m.sin(ang) * (pspeed + .5)
    xstep = x + m.cos(ang) * (pspeed + .5)
    if MAP[int(ystep)][int(xstep)] == 0:
        return y + m.sin(ang) * pspeed, x + m.cos(ang) * pspeed

def wall_render(x, y, ang):
    screen = []
    angle  = ang - FOV / 2
    while angle < pa + FOV / 2:
        
        Cang  = m.cos(angle)
        Sang  = m.sin(angle)
        
        rstep = prespeed
        rfar  = 0
        
        obj   = 0
        
        while rfar < MAX_LENGHT and obj == 0:
            rfar += rstep

            rayy  = y + Sang * rfar
            rayx  = x + Cang * rfar
            
            obj   = MAP[int(rayy)][int(rayx)]

            if obj != 0:  # This method makes graphiks better. I created this)
                if rstep == prespeed:
                    rfar -= rstep
                    rstep = LENGHT_STEP
                    obj   = 0
                else:
                    break
                                    
        if obj != 0:
            
            if dark_wall_x:
                xside = True
                if MAP[int(rayy - Sang * rstep)][int(rayx)] ==\
                   MAP[int(rayy + Sang * rstep)][int(rayx)]:
                    xside = False

            else:
                xside = False
                if MAP[int(rayy)][int(rayx - Cang * rstep)] ==\
                   MAP[int(rayy)][int(rayx + Cang * rstep)]:
                    xside = True
                
            light = 255

            if xside:
                if dark_wall_x:
                    light = dark_wall_side
                if py > rayy: 
                    cut = 1 - rayx + int(rayx)
                else:
                    cut = rayx - int(rayx)

            else:
                if not dark_wall_x:
                    light = dark_wall_side
                if px < rayx: 
                    cut = 1 - rayy + int(rayy)
                else:
                    cut = rayy - int(rayy)
                
            screen.append(['wall', angle - ang, obj, cut, rfar, light])
                
        angle += FOV_STEP

    return screen

def rescreen(screen):
    if lighting:
        for i in range(dHEI // 2):
            recolor = list(roof_color)
            for clr in range(len(recolor)):
                recolor[clr] = int(recolor[clr] * lightQ * ((dHEI - i) / dHEI))
                if recolor[clr] > 255: recolor[clr] = 255
            p.draw.line(win,
                        tuple(recolor),
                        (dWIDs, dHEIs + i),
                        (dWIDs + dWID, dHEIs + i))
        
            recolor = list(floor_color)
            for clr in range(len(recolor)):
                recolor[clr] = int(recolor[clr] * lightQ * ((dHEI - i) / dHEI))
                if recolor[clr] > 255: recolor[clr] = 255
            p.draw.line(win,
                        tuple(recolor),
                        (dWIDs, dHEIs + dHEI - i - 1),
                        (dWIDs + dWID, dHEIs + dHEI - i - 1))
    else:
        p.draw.rect(win,
                    roof_color,
                    (dWIDs, dHEIs,
                    dWID + 1, dHEI // 2))
        p.draw.rect(win,
                    floor_color,
                    (dWIDs, dHEIs + dHEI // 2,
                    dWID + 1, dHEI // 2))
    
    old_path = None

    for i in screen:
        if i[0] == 'wall':
            i.pop(0)
            height = dHEI / (i[3] * m.cos(i[0])) * mulHEI
            
            start_draw = 0      if height > dHEI else int(dHEI - height) // 2
            start_cut  = 0      if height < dHEI else (height - dHEI) / 2
            end_cut    = height if height < dHEI else dHEI

            if old_path != walls.get(i[1]):
                nimg     = p.image.load(walls.get(i[1]))
                old_path = walls.get(i[1])
            
            img = p.transform.scale(nimg, (64, int(height)))

            if not lighting:
                img.set_alpha(i[4])
            else:
                img.set_alpha(i[4] * (end_cut / dHEI) * lightQ)
                
            p.draw.line(win,
                        (0, 0, 0),
                        (int((i[0] + FOV / 2) / FOV_STEP) + dWIDs, start_draw + dHEIs),
                        (int((i[0] + FOV / 2) / FOV_STEP) + dWIDs, start_draw + dHEIs + end_cut - 1))
            
            win.blit(img,
                     img.get_rect(topleft=(int((i[0] + FOV / 2) / FOV_STEP) + dWIDs, start_draw + dHEIs)),
                     (64 * i[2], start_cut, 1, end_cut))
            
    p.display.update()

while True:
    
    for e in p.event.get():
        if e == p.QUIT:
            break

    p.time.delay(30)
    
    if p.key.get_pressed()[p.K_ESCAPE]: break
    
    if p.key.get_pressed()[p.K_LEFT]:
        pa -= rotate
        if pa < 3.14: pa = 9.42
        redraw = True
        
    if p.key.get_pressed()[p.K_RIGHT]:
        pa += rotate
        if pa > 9.42: pa = 3.14
        redraw = True

    if p.key.get_pressed()[p.K_UP] or p.key.get_pressed()[p.K_w]:
        res = moving(px, py, pa)
        if res is not None:
            py, px = res
            redraw = True

    if p.key.get_pressed()[p.K_DOWN] or p.key.get_pressed()[p.K_s]:
        res = moving(px, py, pa - 3.14)
        if res is not None:
            py, px = res
            redraw = True

    if p.key.get_pressed()[p.K_a]:
        res = moving(px, py, pa - 1.57)
        if res is not None:
            py, px = res
            redraw = True

    if p.key.get_pressed()[p.K_d]:
        res = moving(px, py, pa + 1.57)
        if res is not None:
            py, px = res
            redraw = True

    if p.mouse.get_pos() != (dWIDs + dWID // 2, dHEIs + dHEI // 2):
        pa -= (dWIDs + dWID // 2 - p.mouse.get_pos()[0]) * mouse_speed
        if pa < 3.14: pa = 9.42
        if pa > 9.42: pa = 3.14
        redraw = True
        p.mouse.set_pos((dWIDs + dWID // 2, dHEIs + dHEI // 2))

    if redraw:

        redraw = False
        
        screen = []

        for i in wall_render(px, py, pa):
            screen.append(i)

        screen.sort(key=lambda x: x[4])
        screen = screen[::-1]
        
        rescreen(screen)
        
