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
from kivy.properties import ListProperty
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle


import os
import libnodave

class PLCTest(Widget):
    def __init__(self, **kwargs):
        super(PLCTest, self).__init__(**kwargs)
        self.connected=False
        self.load()
        self.dave=Libnodave()
        
    def load(self):
        #add Grid
        self.grid = GridLayout(cols=2, rows=2)
        self.add_widget(self.grid)
        #Add buttons
        self.butt_start=Button(text="Start PLC", size_hint=(None,None))
        self.butt_start.bind(on_press = self.start)
        self.grid.add_widget(self.butt_start)
        self.butt_stop=Button(text="Stop PLC", size_hint=(None,None))
        self.butt_stop.bind(on_press=self.stop)
        self.grid.add_widget(self.butt_stop)
        self.butt_byte=Button(text="Write", size_hint=(None,None))
        self.butt_byte.bind(on_press=self.write_byte)
        self.grid.add_widget(self.butt_byte)
        #connect/disconnect
        self.butt_conn=Button(text="Connect/Disconnect", size_hint=(None,None))
        self.butt_conn.bind(on_press=self.connect)
        self.grid.add_widget(self.butt_conn)
        #slider
        self.s = Slider(min=-127, max=127, value=25, pos=(300,300), width=300)
        self.s.bind(value=self.write_byte)
        self.add_widget(self.s)
        #slider_ist
        self.s_ist = Slider(min=-127, max=127, value=25, pos=(300,400), width=300)
        self.add_widget(self.s_ist)
        #Value ist
        self.label_ist=Label(pos=(300,200))
        self.add_widget(self.label_ist)
        
    
    def stop(self, *kwargs):
        if self.connected:
            self.dave.stop_PLC()

    def connect(self, *kwargs):
        if not self.connected:
            ret_val=self.dave.eth_connection(ip="192.168.1.20")
            if ret_val:
                self.butt_conn.text="Connected"
            else:
                self.butt_conn.text="Error:", ret_val
        else:
            self.dave.disconnect()
            self.butt_conn.text="Disconnected"
        
    
    def start(self, *kwargs):
        if self.connected:
            self.dave.start_PLC()
            
    def read_byte(self, *kwargs):
        if self.connected:
            value=self.dave.get_marker_byte(marker=3)
            if value>127:
                value=value-256
            self.s_ist.value=value
            self.label_ist.text=str(self.s_ist.value)
    
    def write_byte(self, *kwargs):
        if self.connected:
            self.dave.write_marker_byte(marker=3, value=self.s.value)
            self.read_byte()
    
    def unload(self):
        self.clear_widgets()

class PLC(App):
    def build(self):
        return PLCTest()
        
if __name__ == '__main__':
    PLC().run()