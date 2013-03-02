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
from kivy.uix.scatter import Scatter
from kivy.clock import Clock

import os
import ctypes
import threading

import libnodave

plc=False
plc_working=False

class Stone(Scatter):
    def __init__(self, color, def_pos, id_, **kwargs):
        super(Stone, self).__init__(**kwargs)
        self.loaded=False
        self.last_pos=(-2000,-2000)
        self.def_pos=def_pos
        self._id=id_
        
        self.size=(200,200)
        
        self.is_placed=False
        self.do_rotation=False
        self.do_scale=False
        
        self.color=color
        
        if self.color=="white":
            self.image=Image(source=os.path.join("images/white.png"), size=self.size)
        else:
            self.image=Image(source=os.path.join("images/black.png"), size=self.size)
        
        self.load()
        
    def load(self):
        if not self.loaded:
            self.add_widget(self.image)
            self.loaded=True
    
    def unload(self):
        if self.loaded:
            self.clear_widgets()
            del self.image
            self.loaded=False
        
    def check_pos(self, x, y):
        if self.last_pos==(x,y):
            return
        self.last_pos=(x,y)
        space=40
        for pos_given in self.parent.coordinates:
            if (x>=pos_given[0]-space and x<=pos_given[0]+(space*5)) and (y>=pos_given[1]-space and y<=pos_given[1]+(space*5)):
                counter=0
                for i in self.parent.coordinates:
                    if i==pos_given:
                        if self.parent.positions[counter]=="":
                            self.pos_temp=pos_given
                            Clock.schedule_once(self.animate_prepare, 0.7)
                            return
                    counter+=1
        Clock.schedule_once(self.animate_back, 0.7)
    
    def animate_prepare(self, *kwargs):
        if self.loaded:
            self.animate_to_point(self.pos_temp)
    
    def placed(self, numb):
        self.do_translation=False
        self.is_placed=True
        self.parent.positions[numb]=self.color
    
    def fix_stone(self, *kwargs):
        self.is_placed=True
        self.do_translation=False
    
    def release_stone(self, *kwargs):
        if not self.is_placed:
            self.do_translation=True
    
    def animate_back(self, *kwargs):
        self.do_translation=False
        back_ani=Animation(pos=self.def_pos, duration=0.5, t='in_quad')
        back_ani.bind(on_complete=self.back_completed)
        back_ani.start(self)
    
    def animate_to_point(self, pos):
        ani=Animation(pos=(pos), duration=0.2)
        ani.stone_pos=pos
        ani.stone_color=self.color
        ani.bind(on_complete=self.parent.stone_placed)
        ani.start(self)
        counter=-1
        for i in self.parent.coordinates:
            counter+=1
            if i==pos:
                self.placed(numb=counter)
                self.parent.plc.move_to_pos(counter, self.color)
                print "human set:", counter
    
    def back_completed(self, *kwargs):
        self.do_translation=True
        try:
            for i in self.parent.stones:
                self.parent.stones[i].release_stone()
        except:
            pass
    
    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            Clock.unschedule(self.animate_back)
            Clock.unschedule(self.animate_prepare)
            print "touch:", self.do_translation
            if self.do_translation_y:
                for i in self.parent.stones:
                    if not i==self._id:
                        self.parent.stones[i].do_translation=False
                        print "id:", self._id , "index:", i
        return super(Stone, self).on_touch_down(touch)
    
    def on_touch_move(self, touch):
        if self.collide_point(touch.x, touch.y):
            pass
        return super(Stone, self).on_touch_move(touch)
    
    def on_touch_up(self, touch):
        if self.collide_point(touch.x, touch.y):
            if not self.is_placed:
                self.check_pos(touch.x, touch.y)
        return super(Stone, self).on_touch_up(touch)
        
    
class PlayBoard(Widget):
    def __init__(self, **kwargs):
        super(PlayBoard, self).__init__(**kwargs)
        #make library ready
        self.livio=ctypes.CDLL(os.path.join(os.getcwd(), "c_code/main.so"))
        #rest
        self.loaded=False
        self.positions=["", "", "", "", "", "", "", "", ""]
        self.coordinates=((self.x+20, self.y+522+20), (self.x+249+30, self.y+522+20), (self.x+498+20, self.y+522),
                          (self.x+20, self.y+261+20), (self.x+249+30, self.y+261+20), (self.x+498+20, self.y+261+20),
                          (self.x+20, self.y+20), (self.x+249+30, self.y+20), (self.x+498+20, self.y+20)
                          )
        #Preload
        self.plc=PLCCommand()
        self.plc.connect_plc()
        self.cross=Image(source=os.path.join("images/cross.png"), pos=(self.x, self.y), size=(747,785))
        self.result_label=Label(text="", pos=(500,10), font_size=70, font_name="fonts/bradley.TTF", color=(0,0,0,1))
        try:
            self.reset_button=Button(text="Drive to Home", pos=(1300,400), size=(300,100), font_size=30)
            self.reset_button.bind(on_press=self.plc.grundstellung)
        except:
            pass
        self.finished=False
                
    def load(self):
        if not self.loaded:
            self.plc.grundstellung()
            
            self.add_widget(self.plc)
            self.positions=["", "", "", "", "", "", "", "", ""]
            self.add_widget(self.cross)
            self.add_widget(self.reset_button)
            
            self.stones={}
            pos_y=self.y
            for i in range(5):
                self.stones[i]=Stone(color="black", pos=(self.x+750, pos_y), def_pos=(self.x+750, pos_y), id_=i)
                self.add_widget(self.stones[i])
                pos_y+=150
            
            self.stones_pc={}
            pos_y=self.y
            for i in range(5):
                self.stones_pc[i]=Stone(color="white", pos=(self.x+900, pos_y), def_pos=(self.x+900, pos_y), do_translation=False, id_=i)
                self.add_widget(self.stones_pc[i])
                pos_y+=150
            
            self.loaded=True
    
    def unload(self):
        if self.loaded:
            for i in self.stones:
                self.stones[i].unload()
                self.remove_widget(self.stones[i])
            self.stones.clear()
            self.clear_widgets()
            self.loaded=False
            plc_working=False
    
    def place_stone(self, pos_numb):
        for i in self.stones_pc:
            if not self.stones_pc[i].is_placed:
                place_ani=Animation(pos=self.coordinates[pos_numb])
                place_ani.bind(on_completed=self.stone_placed)
                place_ani.start(self.stones_pc[i])
                self.stones_pc[i].is_placed=True
                self.positions[pos_numb]="white"
                self.plc.move_to_pos(pos_numb, "white")
                return
    
    def stone_placed(self, *kwargs):
        try:
            stone_pos=kwargs[0].stone_pos
            stone_color=kwargs[0].stone_color
            pos=self.coordinates.index(stone_pos)
            self.positions[pos]=stone_color
        except:
            pass
        if not plc_working:
            self.send_livio()
            self.check_win()
    
    def send_livio(self):
        list=[]
        for i in self.positions:
            if i=="white":
                pos=1
            elif i=="black":
                pos=4
            elif i=="":
                pos=0
            list.append(pos)
        place_pc=self.livio.main(list[0],list[1],list[2],list[3],list[4],list[5],list[6],list[7],list[8])
        #4=PC
        #1=Player
        #0=nix
        print "livio say:", place_pc
        self.place_stone(place_pc)
    
    def check_win(self):
        list=[]
        for i in self.positions:
            if i=="white":
                pos=1
            elif i=="black":
                pos=4
            elif i=="":
                pos=0
            list.append(pos)
        win=self.livio.checkwin(list[0],list[1],list[2],list[3],list[4],list[5],list[6],list[7],list[8])
        if win==10:
            self.result="Tie"
            self.result_label.text="Unentschieden"
            self.won()
        elif win==14:
            self.result="Player won"
            self.result_label.text="Sie haben gewonnen"
            self.won()
        elif win==11:
            self.result="PC won"
            self.result_label.text="Sie haben verloren"
            self.won()
        return False
    
    def won(self, *kwargs):
        self.add_widget(self.result_label)
        for i in self.stones:
            self.stones[i].do_translation=False
            self.stones[i].fix_stone()
        self.plc.grundstellung()
        print "plc_working:", plc_working
    
class PLCCommand(Widget):
    def __init__(self, **kwargs):
        super(PLCCommand, self).__init__(**kwargs)
        self.connected=False
        self.dave=libnodave.Libnodave()
        self.last_pos=-2
    
    def move_to_pos(self, pos, color):
        if self.connected:
            global plc_working
            plc_working=True
            self.last_pos=pos
            print "write:", pos
            self.color=color
            for i in self.parent.stones:
                self.parent.stones[i].do_translation=False
            self.temp_pos=pos
            Clock.schedule_once(self.send_pos, 0.5)
            Clock.schedule_interval(self.check_done, 0.2)
    
    def send_pos(self, pos1=12, pos=88, *kwagrs):
        if pos==88:
            self.dave.write_marker_byte(marker=13, value=self.temp_pos)
        else:
            print "write a byte", pos
            self.dave.write_marker_byte(marker=13, value=pos)
    
    def check_done(self, pos1=12, pos=88, *kwargs):
        if self.connected:
            pos5=self.dave.get_marker_byte(marker=16)
            if pos==88:
                print pos5, "=", self.last_pos
                if pos5==self.last_pos:
                    Clock.unschedule(self.check_done)
                    self.done_positioning()
            else:
                print "getbyte:", pos5, "old:", pos
                if pos5==pos:
                    return True
                else:
                    return False
    
    def done_positioning(self, *kwargs):
        global plc_working
        plc_working=False
        try:
            for i in self.parent.stones:
                self.parent.stones[i].release_stone()
            if self.color=="black":
                self.parent.stone_placed()
        except:
            pass

    def connect_plc(self):
        if not self.connected:
            ret_val=self.dave.eth_connection(ip="192.168.1.20")
            if ret_val:
                self.connected=True
                print "Connected"
            else:
                print "Error:", ret_val
    
    def disconnect_plc(self):
        if self.connected:
            self.dave.disconnect()
            self.connected=False
    
    def grundstellung(self, *kwargs):
        if not plc_working:
            self.dave.write_marker_byte(marker=13, value=9)
    
    def reconnect(self, *kwargs):
        self.disconnect_plc()
        self.connect_plc()

class Settings_1(Widget):
    def __init__(self, **kwargs):
        super(Settings_1, self).__init__(**kwargs)
        self.loaded=False
        self.button=Button(font_size=25, pos=self.pos, size=(300,100), text="Reconnect with PLC")
        self.test_run_button=Button(font_size=25, pos=(self.pos[0], self.pos[1]-150), size=(300,100), text="Run Test")
        self.test_running=False
        self.test_pos_old=0
        self.test_index=0
        
    def load(self):
        if not self.loaded:
            self.add_widget(self.button)
            self.button.bind(on_release=self.parent.playboard.plc.reconnect)
            self.add_widget(self.test_run_button)
            self.test_run_button.bind(on_release=self.test_run)
            self.loaded=True
    
    def unload(self):
        if self.loaded:
            self.clear_widgets()
            self.loaded=False
    
    def test_run(self, *kwagrs):
        if  self.test_running:
            #STOP
            self.test_run_button.text="Start Testrun"
            self.test_running=False
        else:
            #START
            self.test_index=0
            self.test_run_button.text="Stop Testrun"
            self.test_running=True
            self.checker()
    
    def checker(self, *kwagrs):
        if self.test_running:
            print "start clock"
            Clock.schedule_once(self.test_run_set, 0)
            self.test_pos_old=self.test_index
            Clock.schedule_interval(self.test_run_read, 0)
        
    def test_run_read(self, *kwargs):
        ret_val=self.parent.playboard.plc.check_done(pos=self.test_index)
        if ret_val:
            Clock.unschedule(self.test_run_read)
            self.test_index+=1
            if self.test_index==9:
                self.test_index=0
            self.checker()
        
    def test_run_set(self, *kwagrs):
        print "test_run:_set"
        self.parent.playboard.plc.send_pos(pos=self.test_index)
        
class TicTacTouch(App):
    def build(self):
        return PlayBoard()
        
if __name__ == '__main__':
    TicTacTouch().run()
