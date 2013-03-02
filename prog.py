#!/usr/bin/env python
# -*- coding: UTF-8 -*-

##########################################
# Created by Rentouch                    #
# Copyright By Rentouch 2011             #
#                                        #
##########################################

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.animation import Animation

import os
import playboard
import menu

class TicTacTouch(Widget):
    def __init__(self, **kwargs):
        super(TicTacTouch, self).__init__(**kwargs)
        
        #Preload
        self.playboard=playboard.PlayBoard(pos=(100,100))
        self.menu=menu.Menu(pos=(1200,800))
        self.settings=playboard.Settings_1(pos=(1200,400))
        self.add_widget(self.settings)
        
        self.load()
        
    def load(self):
        self.add_widget(self.menu)
        pass
        
    def new_game(self, var=1):
        self.settings.unload()
        self.add_widget(self.playboard)
        self.playboard.load()
    
    def stop_game(self):
        self.settings.unload()
        self.playboard.unload()
        self.remove_widget(self.playboard)
    
    def load_settings(self, *kwargs):
        self.settings.load()
    
    def unload_settings(self, *kwargs):
        self.settings.unload()

class RunProg(Widget):
    def __init__(self, **kwargs):
        super(RunProg, self).__init__(**kwargs)
        #make layers
        self.root = Widget()
        
        self.background=Image(source=os.path.join("images/background.png"), size=Window.size)
        self.add_widget(self.background)
        
        self.tictac=TicTacTouch()
        self.add_widget(self.tictac)
        
        self.add_widget(self.root)
           
class TicTacTouch_app(App):
    def build(self):
        return RunProg()
        
if __name__ == '__main__':
    TicTacTouch_app().run()