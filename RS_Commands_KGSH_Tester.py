# -*- coding: utf-8 -*-

import serial
import KGSH_Tester

MAX_WAIT_BYTES = 200    #максимальное количество байт в буфере порта на прием
NUMBER_SCAN_PORTS = 5  #количество портов для сканирования

class RS_Commands_KGSH_Tester(object):

    def __init__(self, in_app : KGSH_Tester):
        self.app = in_app


    def scan_COM_ports(self):
        """scan for available ports. return a list of tuples (num, name)"""
        # перечень доступных портов
        available = []
        for i in range(NUMBER_SCAN_PORTS):
            try:
                s = serial.Serial(i)
                available.append((s.portstr))
                s.close()   # explicit close 'cause of delayed GC in java
            except serial.SerialException:
                pass
        return available


    def Init_RS_Var(self, baudrate):
        '''
        Первичная инициализация переменных для RS
        :param baudrate:
        :return None:
        '''
        if baudrate == 115200:
            self.time_to_rx = 100#
        elif baudrate == 57600:
            self.time_to_rx = 100#
        elif baudrate == 38400:
            self.time_to_rx = 100#
        elif baudrate == 19200:
            self.time_to_rx = 200#
        elif baudrate == 9600:
            self.time_to_rx = 200#
        elif baudrate == 1200:
            self.time_to_rx = 400#
        #начальные данные для передатчика
        self.rs_start = bytearray([0x55])   #стартовая последовательность для RS
        self.cmd_tx = 0           #CMD передаваемой команды


    def Serial_Config(self, baudrate, nom_com):
        '''#*********************************************************************
        # настройка порта nom_com на скорость baudrate
        # {int} [baudrate] - скорость работы порта
        # {str} [nom_com] - номер ком порта
        #*********************************************************************'''
        self.ser = serial.Serial(nom_com,#'COM25',
                    baudrate=baudrate,#9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=0,
                    bytesize=serial.EIGHTBITS,
                    xonxoff=0)


    def Serial_Close(self):
        '''
        #*********************************************************************
        # закрыть порт
        #*********************************************************************
        :return:
        '''
        if self.ser.isOpen():
            self.ser.close()


    def Check_Serial(self):
        '''
        #*********************************************************************
        # проверка открыт ли порт
        #*********************************************************************
        :return:
        '''
        if self.ser.isOpen():
            return True
        else:
            return False


    def Recieve_RS_Data(self):
        '''
        #*********************************************************************
        #проверка наличия данных в буфере RS
        #*********************************************************************
        :return:
        '''
        RX_Data = ''  #данных нет
        while self.ser.inWaiting() > 0:
            RX_Data = self.ser.read(MAX_WAIT_BYTES)
        return RX_Data


    def Send_Command_KGSH(self, cmd_tx, leds_tx = 0, value_tx = 0, ampl_sin_tx = 0):
        '''
        #*********************************************************************
        # отправить запрос "обнуление каналов"
        #*********************************************************************
        :param cmd_tx:
        :param leds_tx:
        :param value_tx:
        :param ampl_sin__tx:
        :return:
        '''
        self.app.Set_Status_KGSH(cmd_tx)
        if self.ser.isOpen():
            #полезные данные для передачи
            useful_data =   leds_tx.to_bytes(1,'little') + \
                            cmd_tx.to_bytes(1,'little') + \
                            value_tx.to_bytes(1,'little') + \
                            ampl_sin_tx.to_bytes(1,'little')
            # все данные для передачи
            self.rs_send_pack = self.rs_start + \
                                useful_data
            self.ser.write(self.rs_send_pack)
            if self.app.MODE == 'TEST':
                self.Show_TX_DATA(self.rs_send_pack)
            return True


    def Show_RX_DATA(self):
        '''
        #*********************************************************************
        # вывести полученный пакет из rs_receive_pack
        #*********************************************************************
        :return:
        '''
        print("получен пакет")
        for i in range(0,len(self.app.rs_receive_pack)):
            print(i,': ', hex(self.app.rs_receive_pack[i]),' ;',chr(self.app.rs_receive_pack[i]))


    def Show_TX_DATA(self, data):
        '''
        #*********************************************************************
        # вывести отправленный пакет в RS
        #*********************************************************************
        :return:
        '''
        print("передан пакет")
        for i in range(0,len(data)):
            print(i,': ', hex(data[i]),' ;',chr(data[i]))
