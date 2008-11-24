#! /usr/bin/env python

#Python imports
import sys, os
import math, random

#Import le pygame
import pygame
from pygame.locals import *

#Import the best gl library ever :-D
import pyggel
from pyggel import *

#Import local modules
from objects import *

#You're on the GRID! :-O
GRID = [
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
[1,1,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1],
[1,1,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1],
[1,1,0,0,0,0,0,0,2,0,1,0,0,2,0,1,0,2,0,0,0,1],
[1,1,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1],
[1,1,0,0,0,1,0,1,0,0,1,0,0,0,0,1,0,0,0,2,0,1],
[1,0,0,2,0,1,0,1,0,0,1,0,0,0,0,1,0,0,0,0,0,1],
[1,0,0,0,0,0,0,1,1,0,1,0,1,1,0,1,0,2,0,0,0,1],
[1,0,0,0,0,1,0,1,0,0,1,0,1,0,0,1,0,0,0,0,0,1],
[1,1,0,0,1,1,0,1,0,0,1,0,1,0,0,1,0,0,0,2,0,1],
[0,1,0,0,0,1,0,0,0,0,1,1,1,0,1,1,0,0,0,0,0,1],
[0,1,0,0,0,1,0,0,2,0,0,0,0,0,0,1,0,2,0,0,0,1],
[0,1,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1],
[0,1,0,0,0,0,1,0,1,1,1,0,0,2,0,1,0,0,0,2,0,1],
[1,1,0,0,1,1,0,0,0,0,1,0,0,0,0,1,0,1,0,1,0,1],
[1,1,0,2,0,1,0,0,0,0,1,0,1,1,1,1,1,1,0,1,1,1],
[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]]

#Level parsing function parsing levels
def level_parse(scene):
    
    #Static objects. Woo woo, built for speeeeeeed
    static = []
    walls = []
    x = y = 0 #OMGZ!
    for row in GRID:
        for column in row:
            
            #Floor tiles
            quad = pyggel.geometry.Quad(4.55, pos=[x*5, 0, y*5], facing="bottom", texture=pyggel.image.Texture("data/floor.png"))
            static.append(quad)
            
            #Ceiling tiles
            quad = pyggel.geometry.Quad(4.55, pos=[x*5, 0, y*5], facing="top", texture=pyggel.image.Texture("data/ceiling.png"))
            static.append(quad)
            
            #Walls
            if column == 1:
                box = pyggel.geometry.Cube(4.55, texture=[image.Texture("data/%s" % random.choice(["wall.png", "door.png", "wall.png", "wall.png"]))]*6)
                box.pos=(x*5,0,y*5)
                static.append(box)
                walls.append(Wall([box.pos[0], box.pos[2]]))
            
            #Robo Baddies. OoOoOoOoOo...
            if column == 2:
                RoboBaddie(scene, [x*5, y*5])
        
        #Positioning
            x += 1
        y += 1
        x = 0
    return static, walls

class Game(object):
    
    def __init__(self):

        #Vee must handle ze FPS for ze FPS!
        self.clock = pygame.time.Clock()
        
        #Disable fog. We ain't in a blasted harbor, RB[0]!
        #pyggel.view.set_fog(False)
        pyggel.view.set_fog_color((0, .6, .5, .5))
        pyggel.view.set_fog_depth(5, 150)
        
        #Create a First Person camera
        self.camera = pyggel.camera.LookFromCamera((0,0,-10))
        
        #Create a light. All good little GL apps should have light.
        light = pyggel.light.Light((50,300,50), (0.5,0.5,0.5,1),
                                  (1,1,1,1), (50,50,50,10),
                                  (0,0,0), True)
        
        #Create the scene, and apply the light to it.
        self.scene = pyggel.scene.Scene()
        self.scene.add_light(light)

        #Keep the mouse in the window, and make it disssssappear! Mwahahaha!
        self.grabbed = 1
        pygame.event.set_grab(self.grabbed)
        pygame.mouse.set_visible(0)
        
        #Create starting objects
        self.objects = Group()
        self.shots = Group()
        self.baddies = Group()
        self.walls = Group()
        Player.groups = [self.objects]
        Shot.groups = [self.objects, self.shots]
        RoboBaddie.groups = [self.objects, self.baddies]
        Explosion.groups = [self.objects]
        Wall.groups = [self.objects, self.walls]
        GunFlash.groups = [self.objects]
        
        self.player = Player(self.scene)
        self.overlay = pyggel.image.Image("data/screen.png", pos=[0, 0])
        self.overlay.colorize = [0, 1, 1, 0.1]
        self.scene.add_2d(self.overlay)
        self.targeter = pyggel.image.Image("data/target.png", pos=[320-32, 240-32])
        self.scene.add_2d(self.targeter)
        self.font = pyggel.font.Font("data/DS-DIGI.ttf", 32)
        self.text1 = self.font.make_text_image("||||||||||            Score: 00925675            Lives x3", (0, 255, 0))
        self.text1.pos = (10, 10)
        self.scene.add_2d(self.text1)
        
        #self.sky = pyggel.geometry.Skyball(texture=pyggel.image.Texture("data/ceiling.png")) #
        #self.scene.add_skybox(self.sky)
        
        #parse ze level
        static, self.walls._objects = level_parse(self.scene)
        self.scene.add_3d(pyggel.misc.StaticObjectGroup(static))
        
        #Used for bobbing up and down. No I will not be less vague.
        self.frame = 0
    
    def update_camera_pos(self):
        amt = pygame.mouse.get_rel()
        self.player.angle += amt[0]/8.0
        self.camera.roty = self.player.angle
        self.camera.posz = self.player.pos[1]
        self.camera.posx = self.player.pos[0]
    
    def do_input(self):
        
        #Get input
        for e in pyggel.get_events():
            
            #OMGZ! YOU QUIT! You disappoint me... >(
            if e.type == QUIT:
                self.running = False
            
            if e.type == KEYDOWN:
                
                #YOU'RE AT IT AGAIN!! AUGGH!
                if e.key == K_ESCAPE:
                    self.running = False
                
                #Release the mouse from the window if you press space
                if e.key == K_SPACE:
                    self.grabbed ^= 1
                    pygame.event.set_grab(self.grabbed)

    def do_update(self):
        
        #Loop the frame at 360.
        self.frame += 1
        if self.frame > 360:
            self.frame = 0
        
        #Cap the FPS so the FPS runs smoothly. DOUBLE MEANING! Bwahaha!
        self.clock.tick(60)
        print self.clock.get_fps()
        
        self.update_camera_pos()
        self.player.update_gun_pos()
        for o in self.objects:
            o.update()
        for w in self.walls:
            r = [w.pos[0]-3.0, w.pos[1]-3.0, 6.0, 6.0]
            self.player.collide(r) 
        for s in self.shots:
            collidables = []
            for w in self.walls:
                area = [s.pos[0]-10, s.pos[1]-10, 20, 20]
                if collidepoint(w.pos, area):
                    collidables.append(w)
            for i in range(5):
                s.move()
                for w in collidables:
                    r = [w.pos[0]-3.0, w.pos[1]-3.0, 6.0, 6.0]
                    s.collide(r)
            for b in self.baddies:
                if b.collide(s.pos):
                    s.kill()

    def do_draw(self):
        
        #And pyggel doth draw.
        pyggel.view.clear_screen()
        self.scene.render(self.camera)
        pyggel.view.refresh_screen()

    def main_loop(self):
        
        #Loop de loop
        self.running = True
        while self.running:
            self.do_input()
            self.do_update()
            self.do_draw()

    def run(self):
        self.main_loop()