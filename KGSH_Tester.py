# -*- encoding: utf-8 -*-

from PyQt5.QtCore import QBasicTimer
from PyQt5 import QtWidgets
import Form_Events_KGSH_Tester
import Application_KGSH_Tester
import Ui_KGSH_Tester
import RS_Commands_KGSH_Tester
import sys

pars_status = (1, 2, 3, 4) # соответствие бит полученного байта status с frame_х
pars_keys = (1, 2, 3, 4, 5, 6, 7, 8, 9) # соответствие бит полученного байта keys с frame_Key_х

class KGSH_Tester(QtWidgets.QMainWindow):
    # инициализация окна
    # pyuic5 KGSH_Tester.ui -o Ui_KGSH_Tester.py
    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self, parent)
        self.MODE = 'TEST'
        # self.MODE = 'WORK'
        # словарь для CMD
        self.cur_cmd = {
            "IDLE" : 0,
            "VOLUME" : 1,
            "WDT" : 2,
            "SINUS" : 3,
            }
        self.status_new = self.cur_cmd["IDLE"] #текущее состояние
        self.status_old = self.cur_cmd["IDLE"] #текущее состояние
        # инициализация интерфейса
        self.ui = Ui_KGSH_Tester.Ui_KGSH_Tester()      #инициализация графического интерфейса
        self.ui.setupUi(self)
        # определяем таймер
        self.timer_RX_RS = QBasicTimer()
        self.timer_RX_RS.stop()
        # # подключаем модули
        self.rs = RS_Commands_KGSH_Tester.RS_Commands_KGSH_Tester(self)      #подключение функций работы по RS
        self.event = Form_Events_KGSH_Tester.Form_Events_KGSH_Tester(self)   #определение обработчиков событий
        self.app = Application_KGSH_Tester.Application_KGSH_Tester(self)
        # настройка действий по кнопкам
        self.event.Init_Widgets()


    def Set_Status_KGSH(self, new_status):
        '''
        # установка нового значения переменным STATUS
        :param new_status:
        :return:
        '''
        self.status_old = self.status_new
        self.status_new = new_status


    def analyze_pack(self):
        '''
        #*********************************************************************
        # анализ принятых данных из RS
        #*********************************************************************
        :return:
        '''
        #проверка на стартовую посылку
        if self.rs_receive_pack[:1] == self.rs.rs_start:
            #показать принятые данные
            if self.MODE == 'TEST':
                self.rs.Show_RX_DATA()
            #производим рассчет CRC16 для self.rs_send_pack без последних двух байт
            keys, status, u_pow, u_ampl, i_ampl, err = self.app.Parsing_Rx_Pack(self.rs_receive_pack)
            # проверка была ли ошибка длины в принятых данных
            if err == True:
                return ['Error']
            for i in range(4):
                # устанавливаем значения форм отображения состяния CAN, RS, Codek, PA и кнопок
                if self.app.Check_Bit(status, i):
                    self.app.Set_Frame_Color('green', pars_status[i])
                    self.app.Set_Label_Text( 'включен',  pars_status[i])
                else:
                    self.app.Set_Frame_Color('red', pars_status[i])
                    self.app.Set_Label_Text( 'не работает',  pars_status[i])
            for i in range(8):
                # устанавливаем значения форм отображения состяния кнопок и входов
                if self.app.Check_Bit(keys, i):
                    widg_name = '_Key_%d' % pars_keys[i]
                    self.app.Set_Frame_Color('green', widg_name[1:])
                    if i<4:
                        # кнопка
                        self.app.Set_Label_Text( 'нажата', widg_name)
                    else:
                        # вход
                        self.app.Set_Label_Text( 'замкнут', widg_name)
                else:
                    widg_name = '_Key_%d' % pars_keys[i]
                    self.app.Set_Frame_Color('red', widg_name[1:])
                    if i<4:
                        # кнопка
                        self.app.Set_Label_Text( 'не нажата', widg_name)
                    else:
                        # вход
                        self.app.Set_Label_Text( 'разомкнут', widg_name)

            # текст надписи индикации входного напряжения
            self.ui.label_U_in.setText("U_пит = %1.2f В"%(u_pow/10))
            # текст надписи индикации выходного напряжения
            self.ui.label_U_out.setText("U_вых = %1.2f В"%(u_ampl/10))
            # текст надписи индикации выходного тока
            self.ui.label_I_out.setText("I_вых = %d мА"%i_ampl)
            return 'Ok'
        else:
            return 'Error'


    def timerEvent(self, e):
        '''
        #*********************************************************************
        # обработка событий по таймеру
        #*********************************************************************
        :param e:
        :return:
        '''
        self.result_analyze = None
        self.timer_RX_RS.stop() #выключаем таймер
        if self.rs.Check_Serial():
            # порт окрыт
            self.rs_receive_pack = self.rs.Recieve_RS_Data()    #получаем аднные
            # есть ли принятые данные
            if self.rs_receive_pack != '':
                # анализируем полученные данные
                self.result_analyze = self.analyze_pack()
                # данные есть, проверяем что с ними нужно сделать
                if self.result_analyze == 'Ok' and self.status_new != self.cur_cmd["IDLE"]:
                    # отправляем нужную команду в зависимости от занчения self.status
                    if self.status_new == self.cur_cmd["VOLUME"]:
                        if self.rs.Send_Command_KGSH(self.cur_cmd['VOLUME'], value_tx = self.ui.Slider_Volume.value(),
                                                     leds_tx = self.event.Check_cb_LEDs() ):
                            self.Set_Status_KGSH(self.cur_cmd["IDLE"])
                            # запускаем таймер ожидания ответа
                            self.timer_RX_RS.start(self.rs.time_to_rx, self) 
                            return
                        else:
                            self.result_analyze = 'Error_TX'
                    elif self.status_new == self.cur_cmd["SINUS"]:
                        if self.ui.pushButton_Sinus.isChecked():
                            # кнопка Генератор нажата
                            if self.rs.Send_Command_KGSH(self.cur_cmd['SINUS'], ampl_sin_tx = (self.ui.comboBox_Sinus.currentIndex()+1),
                                                         leds_tx = self.event.Check_cb_LEDs(),
                                                         value_tx = 1):
                                # запускаем таймер ожидания ответа
                                self.timer_RX_RS.start(self.rs.time_to_rx, self) 
                                return
                            else:
                                self.result_analyze = 'Error_TX'
                        else:
                            # кнопка Генератор отжата
                            if self.rs.Send_Command_KGSH(self.cur_cmd['SINUS'], ampl_sin_tx = (self.ui.comboBox_Sinus.currentIndex()+1),
                                                         leds_tx = self.event.Check_cb_LEDs(),
                                                         value_tx = 0):
                                # установка уровня звука на нужном уровне
                                self.Set_Status_KGSH(self.cur_cmd["VOLUME"])
                                # запускаем таймер ожидания ответа
                                self.timer_RX_RS.start(self.rs.time_to_rx, self) 
                                return
                            else:
                                self.result_analyze = 'Error_TX'
                    elif self.status_new == self.cur_cmd["WDT"]:
                        # кнопка Генератор отжата
                        if self.rs.Send_Command_KGSH(self.cur_cmd['WDT']):
                            # установка уровня звука на нужном уровне
                            self.Set_Status_KGSH(self.cur_cmd["VOLUME"])
                            # запускаем таймер ожидания ответа
                            self.timer_RX_RS.start(self.rs.time_to_rx, self)
                            return
                        else:
                            self.result_analyze = 'Error_TX'
                else:
                    # передаем исходный пакет в состояние IDLE
                    if self.rs.Send_Command_KGSH( self.cur_cmd['IDLE'], leds_tx = self.event.Check_cb_LEDs() ):
                        # запускаем таймер ожидания ответа
                        self.timer_RX_RS.start(self.rs.time_to_rx, self) 
                        return
                    else:
                        self.result_analyze = 'Error_TX'

            # обработка ошибок
            if self.result_analyze == 'Error_TX':
                # ответ не получен
                QtWidgets.QMessageBox.warning(self, 'Ошибка',"Ошибка передачи.", QtWidgets.QMessageBox.Ok)

            # принятых данных нет
            # устанавливаем значения форм отображения состяния CAN, RS, Codek, PA и кнопок
            for i in range(4):
                self.app.Set_Frame_Color('red', pars_status[i])
                self.app.Set_Label_Text( 'не работает',  pars_status[i])
            # отправляем соответствующий пакет в зависимости от значения self.status_new
            if self.status_new == self.cur_cmd["IDLE"]:
                # отправляем маркер
                if self.rs.Send_Command_KGSH(self.cur_cmd['IDLE'], leds_tx = self.event.Check_cb_LEDs() ):
                    # запускаем таймер ожидания ответа
                    self.timer_RX_RS.start(self.rs.time_to_rx, self) 
                else:
                    # ответ не получен
                    QtWidgets.QMessageBox.warning(self, 'Ошибка',"Ошибка передачи.", QtWidgets.QMessageBox.Ok)
            elif self.status_new == self.cur_cmd["VOLUME"]:
                if self.rs.Send_Command_KGSH(self.cur_cmd['VOLUME'], value_tx = self.ui.Slider_Volume.value(),
                                             leds_tx = self.event.Check_cb_LEDs() ):
                    # запускаем таймер ожидания ответа
                    self.timer_RX_RS.start(self.rs.time_to_rx, self) 
                else:
                    # ответ не получен
                    QtWidgets.QMessageBox.warning(self, 'Ошибка',"Ошибка передачи.", QtWidgets.QMessageBox.Ok)
            elif self.status_new == self.cur_cmd["SINUS"]:
                if self.rs.Send_Command_KGSH(self.cur_cmd['SINUS'], ampl_sin_tx = (self.ui.comboBox_Sinus.currentIndex()+1),
                                                         leds_tx = self.event.Check_cb_LEDs(),
                                                         value_tx = 1):
                    # запускаем таймер ожидания ответа
                    self.timer_RX_RS.start(self.rs.time_to_rx, self) 
                else:
                    # ответ не получен
                    QtWidgets.QMessageBox.warning(self, 'Ошибка',"Ошибка передачи.", QtWidgets.QMessageBox.Ok)
            else:
                # ответ не получен
                QtWidgets.QMessageBox.warning(self, 'Ошибка',"Нет ответа от модуля.", QtWidgets.QMessageBox.Ok)
                # переходим в IDLE
                self.Set_Status_KGSH(self.cur_cmd["IDLE"])
            return


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = KGSH_Tester()
    myapp.show()
    sys.exit(app.exec_())
