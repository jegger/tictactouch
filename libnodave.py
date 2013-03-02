#!/usr/bin/python
# -*- coding: utf-8 -*-
#libnodave.py


import ctypes
import os
import time

# copie of all constants from nodave.h
#Protocol types to be used with newInterface:
daveProtoMPI  = 0    # MPI for S7 300/400 
daveProtoMPI2 = 1    # MPI for S7 300/400, "Andrew's version" without STX 
daveProtoMPI3 = 2    # MPI for S7 300/400, Step 7 Version, not yet implemented 
daveProtoMPI4 = 3    # MPI for S7 300/400, "Andrew's version" with STX 

daveProtoPPI  = 10    # PPI for S7 200 
daveProtoAS511 = 20    # S5 programming port protocol 
daveProtoS7online = 50    # use s7onlinx.dll for transport 
daveProtoISOTCP = 122    # ISO over TCP */
daveProtoISOTCP243 = 123 # ISO over TCP with CP243 */
daveProtoISOTCPR = 124   # ISO over TCP with Routing */

daveProtoMPI_IBH = 223   # MPI with IBH NetLink MPI to ethernet gateway */
daveProtoPPI_IBH = 224   # PPI with IBH NetLink PPI to ethernet gateway */

daveProtoNLpro = 230     # MPI with NetLink Pro MPI to ethernet gateway */

daveProtoUserTransport = 255    # Libnodave will pass the PDUs of S7 Communication to user */
                                      # defined call back functions. */
                    
#ProfiBus speed constants:
daveSpeed9k = 0
daveSpeed19k = 1
daveSpeed187k = 2
daveSpeed500k = 3
daveSpeed1500k = 4
daveSpeed45k = 5
daveSpeed93k = 6

#    S7 specific constants:
daveBlockType_OB = '8'
daveBlockType_DB = 'A'
daveBlockType_SDB = 'B'
daveBlockType_FC = 'C'
daveBlockType_SFC = 'D'
daveBlockType_FB = 'E'
daveBlockType_SFB = 'F'

daveS5BlockType_DB = 0x01
daveS5BlockType_SB = 0x02
daveS5BlockType_PB = 0x04
daveS5BlockType_FX = 0x05
daveS5BlockType_FB = 0x08
daveS5BlockType_DX = 0x0C
daveS5BlockType_OB = 0x10


#Use these constants for parameter "area" in daveReadBytes and daveWriteBytes  
daveSysInfo = 0x3      # System info of 200 family 
daveSysFlags = 0x5    # System flags of 200 family 
daveAnaIn = 0x6       # analog inputs of 200 family 
daveAnaOut = 0x7      # analog outputs of 200 family 

daveP = 0x80           # direct peripheral access 
daveInputs = 0x81    
daveOutputs = 0x82    
daveFlags = 0x83
daveDB = 0x84          # data blocks 
daveDI = 0x85          # instance data blocks 
daveLocal = 0x86       # not tested 
daveV = 0x87           # don't know what it is 
daveCounter = 28       # S7 counters 
daveTimer = 29         # S7 timers 
daveCounter200 = 30    # IEC counters (200 family) 
daveTimer200 = 31      # IEC timers (200 family) 
daveSysDataS5 = 0x86   # system data area ? 
daveRawMemoryS5 = 0    # just the raw memory 


def int_to_bitarr(integer):
    """
        get a list with 8 elements from a given integer.
        position in ret_list = positino on PLC  -> m0.0 = ret_list[0]
                                                -> m0.7 = ret_list[7]
    """
    temp = bin(integer)[2:]
    ret_list = list()
    
    for bit in xrange(8 - len(temp)):
        ret_list.append(0)   
    
    for bit in temp:
        ret_list.append(int(bit))    
    
    ret_list.reverse()
    return ret_list

def bitarr_to_int(bitarr):
    """
        convert a bitarr(ret value of int_to_bitarr) into a integer
    """
    str_bitarr = list()
    bitarr.reverse()
    for elem in bitarr:
        str_bitarr.append(str(elem))
    string = ''.join(str_bitarr)
    return int(string,2)


class _daveOSserialType(ctypes.Structure):
    #class to represent a C-struct
    _fields_ = [("rfd", ctypes.c_int),
                ("wfd", ctypes.c_int)]
    
class Libnodave(object):
    #wrapper for the libnodave dll
    def __init__(self):
        self.fds = _daveOSserialType()
        self.di = False                 #DaveInterface - will be set on first connection
        self.init_dll()
        self.buffer = ctypes.create_string_buffer('buffer')
        self.buffer_p = ctypes.pointer(self.buffer)
        self.connected = False          #bool value . connection is established?
        
    def get_dll_loc(self):
        """
            Get subfolder. Decide by OS. posix=UNIX/nt=Windows
        """ 
        APPDIR = os.path.dirname(os.path.abspath(__file__))
        if os.name == 'nt':
            return os.path.join(APPDIR, 'libnodave', 'win', 'libnodave.dll')
        if os.name == 'posix':
            return os.path.join(APPDIR, 'libnodave', 'libnodave.so')
        
    def init_dll(self):
        """
            initiate the os depending dll-File
            set argtypes and resttypes for used functions
        """
        if os.name == 'nt':
            self.dave = ctypes.windll.LoadLibrary(self.get_dll_loc())
        else:
            self.dave =  ctypes.cdll.LoadLibrary(self.get_dll_loc())
            
        self.dave.setPort.restype =  ctypes.c_int
        self.dave.setPort.argtypes = [ctypes.c_char_p,
                                      ctypes.c_char_p,
                                      ctypes.c_char]
        
        self.dave.daveNewInterface.resttype = ctypes.c_void_p
        self.dave.daveNewInterface.argtypes = [_daveOSserialType,
                                               ctypes.c_char_p,
                                               ctypes.c_int,
                                               ctypes.c_int,
                                               ctypes.c_int]
        
        self.dave.daveInitAdapter.resttype = ctypes.c_void_p
        self.dave.daveInitAdapter.argtypes = [ctypes.c_void_p]
        
        self.dave.daveNewConnection.resttype = ctypes.c_void_p
        self.dave.daveNewConnection.argtypes = [ctypes.c_void_p,
                                                ctypes.c_int,
                                                ctypes.c_int,
                                                ctypes.c_int]
        
        self.dave.daveConnectPLC.resttype = ctypes.c_int
        self.dave.daveConnectPLC.argtypes = [ctypes.c_void_p]
        
        self.dave.daveSetTimeout.resttype = ctypes.c_void_p
        self.dave.daveSetTimeout.argtypes = [ctypes.c_void_p, 
                                             ctypes.c_int]
        
        self.dave.daveGetU8.resttype = ctypes.c_int
        self.dave.daveGetU8.argtypes = [ctypes.c_void_p]
        
        self.dave.daveDisconnectPLC.resttype = ctypes.c_int
        self.dave.daveDisconnectPLC.argtypes = [ctypes.c_void_p]
        
        self.dave.daveFree.resttype = None
        self.dave.daveFree.argtypes = [ctypes.c_void_p]
        
        self.dave.daveDisconnectAdapter.resttype = ctypes.c_int
        self.dave.daveDisconnectAdapter.argtypes = [ctypes.c_void_p]
        
        self.dave.daveReadBytes.resttype = ctypes.c_int
        self.dave.daveReadBytes.argtypes = [ctypes.c_void_p,
                                            ctypes.c_int,
                                            ctypes.c_int,
                                            ctypes.c_int,
                                            ctypes.c_int,
                                            ctypes.c_void_p]
        
        self.dave.daveGetCounterValue.resttype = ctypes.c_int
        self.dave.daveGetCounterValue.argtypes = [ctypes.c_void_p,
                                                  ctypes.c_int,
                                                  ctypes.c_int,
                                                  ctypes.c_int,
                                                  ctypes.c_int,
                                                  ctypes.c_void_p]
        
        self.dave.daveWriteBytes.resttype = ctypes.c_int
        self.dave.daveWriteBytes.argtypes = [ctypes.c_void_p,
                                             ctypes.c_int,
                                             ctypes.c_int,
                                             ctypes.c_int,
                                             ctypes.c_int,
                                             ctypes.c_void_p]
        
    def set_port(self, port, baud='9600', parity = 'E'):
        """
            set a serial connection port
        """
        self.fds.rfd = self.dave.setPort(port, baud, parity)
        self.fds.wfd = self.fds.rfd
    
    def open_socket(self, IP="192.168.1.1", port=102):
        """
        Make socket connection over TCP.
        IP = IP address pf PLC
        port = Port number of the protocol. (ISO=102, IBH/MHJNetlink=1099)
        """
        self.fds.rfd = self.dave.openSocket(port, IP)
        self.fds.wfd = self.fds.rfd
        print "socket error:", self.fds.rfd
        
    def new_interface(self, name, localMPI, protocol, speed):
        """
            EXPORTSPEC daveInterface * DECL2 daveNewInterface(_daveOSserialType nfd,
                            char * nname, int localMPI, int protocol, int speed);
            name= a unique name for your interface (as a string)
            lovalMPI = localMPI number (0) / for TCP=0
            protocol = protokoll / ISOTCP=daveProtoISOTCP, MPI=daveProtoMPI, ISOTCP243=daveProtoISOTCP243
            speed = speed for MPI (TCP=daveSpeed187k)
            
        """
        self.di = self.dave.daveNewInterface(self.fds, name, localMPI, protocol, speed)
    
    def set_timeout(self, time):
        """
            set a new timeout
            EXPORTSPEC void DECL2 daveSetTimeout(daveInterface * di, int tmo);
        """
        self.dave.daveSetTimeout(self.di, time)
    
    def init_adapter(self):
        """
            initiate the configurated adapter
            EXPORTSPEC int DECL2 _daveInitAdapterNLpro(daveInterface * di);
        """
        self.dave.daveInitAdapter(self.di)
        
    def connect_plc(self, mpi, rack, slot):
        """
            connect to the plc
            daveConnection * DECL2 daveNewConnection(daveInterface * di, int MPI,int rack, int slot);
            mpi = MPI number (default 2) / tcp=0
            rack = Rack number (default 0)
            slot = slot number (default 2)
        """
        self.dc = self.dave.daveNewConnection(self.di, mpi, rack, slot)
        self.res = self.dave.daveConnectPLC(self.dc)
        if self.res == 0:
            self.connected = True
        return self.res

    def disconnect(self):
        """
            disconnect connection to PLC and Adapter 
            TODO:get rid of the print Statements
        """
        print self.dave.daveDisconnectPLC(self.dc)
        print self.dave.daveFree(self.dc)
        print self.dave.daveDisconnectAdapter(self.di)
        print self.dave.daveFree(self.di)
        print self.dave.closePort(self.fds.rfd)
        self.connected = False
        
    def read_bytes(self, area, db, start, len):
        """
        area= Kontante! - for the memory area in PLC
        DB = The number of data block. Only meaningful if area is dave DB. Otherwise = 0
        start = adress of first byte in block
        len = number of bytes to read
        -------------------------------
            int daveReadBytes(daveConnection * dc, int area, int DB, int start, int len, void * buffer);
            set the pointer to specified memory in the plc
            returns True if pointer is set
        """
        res = self.dave.daveReadBytes(self.dc, area, db, start, len, self.buffer)
        if res == 0:
            return True
        return False
    
    def get_counter_value(self, counter_number):
        """
            read a counter from the plc
        """
        self.read_bytes(daveCounter, 0, 0, 1)  
        counters = list()
        for val in xrange(16):
            counters.append(self.dave.daveGetCounterValue(self.dc)) 
        return counters[counter_number]
    
    def get_counters(self):
        """
            list of all counters on the plc
        """
        if self.read_bytes(daveCounter, 0, 0, 1):  
            counters = list()
            for val in xrange(16):
                counters.append(self.dave.daveGetCounterValue(self.dc)) 
            return counters
        return False
    
    def get_marker_byte(self, marker):
        """
            read one complete flag (8 bit) from the plc
            on connection error returnvalue is -1
        """
        if self.read_bytes(daveFlags, 0, marker, 1):
            return self.dave.daveGetU8(self.dc)
        return -1
    
    def get_marker(self, marker, byte):
        """
            read one bit from a flag from plc
            on connection error returnvalue is -1
        """
        m_byte = self.get_marker_byte(marker)
        if m_byte >= 0:
            byte_arr = int_to_bitarr(m_byte)
            return byte_arr[byte]
        return -1
    
    def get_marker_byte_list(self, marker):
        """
            read a flag(8 bit) from plc
            get a list with al bits representing all marker from read byte
        """   
        if self.read_bytes(daveFlags, 0, marker, 1):
            return int_to_bitarr(self.dave.daveGetU8(self.dc))
        return -1
    
    def get_marker_byte_dict(self, marker):
        """
            get a flag(8 bit) from plc as Dict
        """
        _l = self.get_marker_byte_list(marker)
        if _l == -1:
            return -1
        d = dict()
        for val in xrange(8):
            d[val]=_l[val]
        return d
        
    def write_marker_byte(self, marker, value):
        """
            EXPORTSPEC int DECL2 daveWriteBytes(daveConnection * dc, int area, int DB, int start,
                                                int len, void * buffer);
            write a flag (8-bit) to the plc
        """
        buffer = ctypes.c_byte(int(value))
        buffer_p =  ctypes.pointer(buffer)
        self.dave.daveWriteBytes(self.dc, daveFlags, 0, marker, 1, buffer_p)
    
    def stop_PLC(self):
        """
        Set PLC to STOP Mode
        """
        print self.dave.daveStop(self.dc)
    
    def start_PLC(self):
        """
        Set PLC to Start mode
        """
        print self.dave.daveStart(self.dc)
    
    def eth_connection(self, ip):
        """
        ip = IP adress (string)
        """
        self.open_socket(IP=ip)
        self.new_interface("IF1", 0, daveProtoISOTCP, daveSpeed187k)
        self.set_timeout(100)
        result = self.connect_plc(2, 0, 2)
        if result != 0:
            return result
        else:
            return True

  
def main():
    pass
    
if __name__ == '__main__':
    main()
