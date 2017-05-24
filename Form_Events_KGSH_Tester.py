# -*- encoding: utf-8 -*-

import KGSH_Tester
from PyQt5 import QtWidgets

# соответствие битов в байте с порядковым номером checkBox_LED_x
leds_bit = [ 2, 3, 4, 5, 1, 0 ]
BAUDRATES = ['1200', '9600', '19200', '38400', '57600', '115200']    #возможные значения скоростей для RS-232

class Form_Events_KGSH_Tester(object):

    def __init__(self, main_app: KGSH_Tester):
        self.app = main_app


    def Init_Widgets(self):
        '''
        #настройка действий по кнопкам
        :return:
        '''
        #настройка списка для выбора порта
        self.app.ui.comboBox_COM.addItems(self.app.rs.scan_COM_ports())
        self.app.ui.comboBox_COM.setCurrentIndex(0)
        #добавляем нужные скорости в comboBox_Baudrate
        self.app.ui.comboBox_Baudrate.addItems(BAUDRATES)
        self.app.ui.comboBox_Baudrate.setCurrentIndex(1)        #добавляем нужные скорости в comboBox_Baudrate
        # добавляем уровни тестового сигнала в comboBox_Sinus
        ch_list = [str(list_item) for list_item in range(1,7)]
        self.app.ui.comboBox_Sinus.addItems(ch_list)
        self.app.ui.comboBox_Sinus.setCurrentIndex(0)

        # обработчики для кнопок
        self.app.ui.pushButton_open_COM.clicked.connect(self.pb_Open_COM_Header)
        self.app.ui.pushButton_close_COM.clicked.connect(self.pb_Close_COM_Header)
        self.app.ui.pushButton_WDT.clicked.connect(self.pb_WDT_Header)
        self.app.ui.Slider_Volume.valueChanged.connect(self.Slider_Volume_Header)
        self.app.ui.pushButton_Sinus.clicked.connect(self.cb_Sinus_Header)


    def pb_Open_COM_Header(self):
        '''
        :return:
        '''
        self.app.ui.comboBox_COM.setDisabled(1)
        self.app.ui.comboBox_Baudrate.setDisabled(1)
        baudrate = int(self.app.ui.comboBox_Baudrate.currentText())
        nom_com_port = self.app.ui.comboBox_COM.currentText()
        # конфигурируем RS
        self.app.rs.Serial_Config(baudrate, nom_com_port)
        self.app.rs.Init_RS_Var(baudrate)
        # изменяем видимость кнопок
        self.Enable_Widgets()
        # try:
        if self.app.rs.Send_Command_KGSH(self.app.cur_cmd['IDLE']):
            #запускаем таймер до отправки
            self.app.timer_RX_RS.start(self.app.rs.time_to_rx, self.app) #отправляем запрос защитного кода через self.time_to_rx мс
        # except:
        #     pass
            # self.app.ui.QtWidgets.QMessageBox.warning(self.app, 'Ошибка', "Ошибка передачи", QtWidgets.QMessageBox.Ok)


    def pb_Close_COM_Header(self):
        '''
        #*********************************************************************
        # активация кнопок после выбора порта и скорости
        #*********************************************************************
        :return:
        '''
        # self.pb_Stop_Polling_Header()
        self.app.rs.Recieve_RS_Data()
        # закрываем порт
        self.app.rs.Serial_Close()
        self.app.ui.comboBox_COM.setDisabled(1)
        self.app.ui.comboBox_Baudrate.setDisabled(1)
        self.app.ui.comboBox_COM.setEnabled(1)
        self.app.ui.comboBox_Baudrate.setEnabled(1)
        # изменяем видимость кнопок
        self.Disable_Widgets()


    def Enable_Widgets(self):
        '''
        #*********************************************************************
        # активация кнопок после выбора порта и скорости
        #*********************************************************************
        :return:
        '''
        self.app.ui.pushButton_open_COM.setDisabled(1)
        self.app.ui.pushButton_close_COM.setEnabled(1)
        self.app.ui.Slider_Volume.setEnabled(1)
        self.app.ui.comboBox_Sinus.setEnabled(1)
        for i in range ( 1, 7 ):
            eval('self.app.ui.checkBox_LED_%i.setEnabled(1)'%i)
        self.app.ui.Label_LED_Red.setEnabled(1)
        self.app.ui.Label_LED_Green.setEnabled(1)
        self.app.ui.pushButton_WDT.setEnabled(1)
        self.app.ui.pushButton_Sinus.setEnabled(1)


    def Disable_Widgets(self):
        '''
        #*********************************************************************
        # деактивация кнопок после выбора порта и скорости
        #*********************************************************************
        :return:
        '''
        self.app.ui.pushButton_open_COM.setEnabled(1)
        self.app.ui.pushButton_close_COM.setDisabled(1)
        self.app.ui.Slider_Volume.setDisabled(1)
        self.app.ui.comboBox_Sinus.setDisabled(1)
        for i in range ( 1, 7 ):
            eval('self.app.ui.checkBox_LED_%i.setDisabled(1)'%i)
        self.app.ui.Label_LED_Red.setDisabled(1)
        self.app.ui.Label_LED_Green.setDisabled(1)
        self.app.ui.pushButton_WDT.setDisabled(1)
        self.app.ui.pushButton_Sinus.setDisabled(1)


    def Check_cb_LEDs(self):
        '''
        формирование данных о состоняии светодиодов
        :return:
        '''
        ret_val = 0
        for i in range ( 1, 7 ):
            val = eval('self.app.ui.checkBox_LED_%i.checkState()'%i)
            if val == 2:
                ret_val = self.app.app.Set_Bit(ret_val, leds_bit[i-1])
        return ret_val


    def Slider_Volume_Header(self):
        '''
        Обработчик изменения значения в Slider_Volume
        :return:
        '''
        self.app.Set_Status_KGSH(self.app.cur_cmd["VOLUME"])
        self.app.ui.Label_Volume.setText(str(self.app.ui.Slider_Volume.value()))


    def cb_Sinus_Header(self):
        '''
        Обработчик изменения состояния pushButton_Sinus
        :return:
        '''
        if self.app.ui.Slider_Volume.isEnabled():
            self.app.Set_Status_KGSH(self.app.cur_cmd["SINUS"])
            self.app.ui.Slider_Volume.setDisabled(1)
        else:
            self.app.ui.Slider_Volume.setEnabled(1)


    def pb_WDT_Header(self):
        '''
        Обработчик нажатия кнопки pushButton_WDT
        :return:
        '''
        self.app.Set_Status_KGSH(self.app.cur_cmd["WDT"])

