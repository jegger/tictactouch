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
from kivy.uix.gridlayout import GridLayout

import os

font_size=55
font_size_small=40
button_size=(500,100)

class Menu(Widget):
    def __init__(self, **kwargs):
        super(Menu, self).__init__(**kwargs)
        self.loaded=False
        self.first=True
        
        self.grid=GridLayout(cols=1, pos=(self.x, self.y), col_default_width=button_size[0], row_default_height=button_size[1])
        self.add_widget(self.grid)
        
        #Preload
        self.play=Button(text="- Play", font_name="fonts/bradley.TTF", halign="left", color=(0,0,0,1), size=button_size,  text_size=button_size, font_size=font_size, background_color=(0,0,0,0))
        self.play.bind(on_release=self.button_up)
        self.play.bind(on_press=self.button_down)
        self.play.bind(on_release=self.show_play)
        
        self.settings=Button(text="- Settings", font_name="fonts/bradley.TTF", color=(0,0,0,1), size=button_size,  text_size=button_size, font_size=font_size, background_color=(0,0,0,0))
        self.settings.bind(on_release=self.button_up)
        self.settings.bind(on_press=self.button_down)
        self.settings.bind(on_release=self.show_settings)
        
        self.var1=Button(text="- Variante1", font_name="fonts/bradley.TTF", color=(0,0,0,1), size=button_size,  text_size=button_size, font_size=font_size_small, background_color=(0,0,0,0))
        self.var1.bind(on_release=self.button_up)
        self.var1.bind(on_press=self.button_down)
        self.var1.bind(on_release=self.play_var1)
        
        self.var2=Button(text="- Variante2", font_name="fonts/bradley.TTF", color=(0,0,0,1), size=button_size,  text_size=button_size, font_size=font_size_small, background_color=(0,0,0,0))
        self.var2.bind(on_release=self.button_up)
        self.var2.bind(on_press=self.button_down)
        self.var2.bind(on_release=self.play_var2)
        
        self.main=Button(text="- Main Menu", font_name="fonts/bradley.TTF", color=(0,0,0,1), size=button_size,  text_size=button_size, font_size=font_size, background_color=(0,0,0,0))
        self.main.bind(on_release=self.button_up)
        self.main.bind(on_press=self.button_down)
        self.main.bind(on_release=self.show_main)
        
        self.stop=Button(text="- Stop game", font_name="fonts/bradley.TTF", color=(0,0,0,1), size=button_size,  text_size=button_size, font_size=font_size, background_color=(0,0,0,0))
        self.stop.bind(on_release=self.button_up)
        self.stop.bind(on_press=self.button_down)
        self.stop.bind(on_release=self.stop_game)
        
        self.show_main()
        self.first=False
        
    def show_main(self, *kwagrs):
        self.remove_from_grid()
        if not self.first:
            self.parent.unload_settings()
        self.grid.add_widget(self.play)
        self.grid.add_widget(self.settings)
    
    def show_play(self, *kwargs):
        self.remove_from_grid()
        self.grid.add_widget(self.main)
        self.grid.add_widget(self.var1)
        self.grid.add_widget(self.var2)
    
    def show_settings(self, *kwargs):
        self.remove_from_grid()
        self.grid.add_widget(self.main)
        self.parent.load_settings()
        
    def play_var1(self, *kwargs):
        self.remove_from_grid()
        self.grid.add_widget(self.stop)
        self.parent.new_game(var=1)
    
    def play_var2(self, *kwargs):
        self.remove_from_grid()
        self.grid.add_widget(self.stop)
        self.parent.new_game(var=2)
    
    def remove_from_grid(self):
        self.grid.clear_widgets()
    
    def stop_game(self, *kwagrs):
        self.parent.stop_game()
        self.show_main()
    
    def button_down(self, *kwargs):
        kwargs[0].color=(0,0,0,0.5)
             
    def button_up(self, *kwargs):
        kwargs[0].color=(0,0,0,1)
        
        
class TicTacTouch(App):
    def build(self):
        return Menu()
        
if __name__ == '__main__':
    TicTacTouch().run()