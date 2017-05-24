#coding: utf8

LENGTH = 7           # нормальная длина принимаемого пакета
KEYS_POS = 1         # номер байта CMD в пакете
STATUS_POS = 2       # номер байта num_chnl в пакете
U_POW_POS = 3        # номер байта param в пакете
U_AMPL_POS = 4       # номер байта hours в пакете
I_AMPL_LO_POS = 5      # номер байта minutes в пакете
I_AMPL_HI_POS = 6      # номер байта seconds в пакете

class Application_KGSH_Tester(object):

    def __init__(self, in_app):
        self.app = in_app


    def Parsing_Rx_Pack(self, data_in):
        """
        парсинг полученного пакета
        param: data_in: {bytes}
        return: [keys, status, u_pow, u_ampl, i_ampl, err]:
        """
        keys = status = u_pow = u_ampl = i_ampl = 0
        if len(data_in) != LENGTH:
            err = True
        else:
            err = False
            # выделяем данные из пакета
            keys = int.from_bytes(data_in[KEYS_POS: KEYS_POS+1], byteorder='little') #преобразуем в int
            status = int.from_bytes(data_in[STATUS_POS:STATUS_POS+1], byteorder='little') #преобразуем в int
            u_pow = int.from_bytes(data_in[U_POW_POS:U_POW_POS+1], byteorder='little') #преобразуем в int
            u_ampl = int.from_bytes(data_in[U_AMPL_POS:U_AMPL_POS+1], byteorder='little') #преобразуем в int
            i_ampl = int.from_bytes(data_in[I_AMPL_LO_POS:I_AMPL_HI_POS+1], byteorder='little') #преобразуем в int
        return (keys, status, u_pow, u_ampl, i_ampl, err)


    def Set_Frame_Color(self, color, num_chnl):
        '''
        прорисовка frame на форме красным цветом с номером num_chnl,
        если num_chnl = 0 - все
        param color - цвет 'green': зеленый, остальные - красный
        param num_chnl - номер канала для обнуления:
        return:
        '''
        if isinstance(num_chnl, int):
            num_chnl = str(num_chnl)
        if isinstance(num_chnl, str):
            if color == 'green':
                text_to_command = 'self.app.ui.frame_%s.setStyleSheet("background-color: rgb(0, 150, 53);")'
            elif color == 'red':
                text_to_command = 'self.app.ui.frame_%s.setStyleSheet("background-color: rgb(255, 117, 53);")'
            else:
                text_to_command = 'self.app.ui.frame_%s.setStyleSheet("background-color: rgb(150, 150, 150);")'
            eval(text_to_command % num_chnl)
            return 'Ok'
        return 'Error'


    def Set_Label_Text( self, text, num_chnl ):
        '''
        изменение надписи поля с описанием состояния канала с номером num_chnl,
        если num_chnl = 0 - изменить надпись на всех каналах
        param: text - текст который нужно вывести
        param: num_chnl - номер канала для обнуления:
        return: Ok или Error
        '''
        if isinstance(num_chnl, int):
            num_chnl = str(num_chnl)
        if isinstance(num_chnl, str):
            eval('self.app.ui.label_t%s.setText("%s")'%(num_chnl, text))
            return 'Ok'
        return 'Error'


    def Set_Bit(self, data, bit_num):
        '''
        #*********************************************************************
        # установка значения бита переменной int
        # [data] - данные
        # [bit_num] - номер бита для установки
        #*********************************************************************
        :param data:
        :param bit_num:
        :return: данные data с установленным битом
        '''
        if isinstance(data, int):
            return ( data | (1 << bit_num))
        elif isinstance(data, bytearray) or isinstance(data, bytes):
            data_len = len(data)
            data = int.from_bytes(data, byteorder='big') | (1 << bit_num)
            return data.to_bytes(data_len,'big')
        else:
            return None

    def Reset_Bit(self, data, bit_num):
        '''
        #*********************************************************************
        # установка значения бита переменной int и byte
        # [data] - данные
        # [bit_num] - номер бита для установки
        #*********************************************************************
        :param data:
        :param bit_num:
        :return: данные data с установленным битом
        '''
        mask = 0
        if isinstance(data, int):
            len_data_bin = len(bin(data))-2
            for i in range(len_data_bin):
                mask = (mask << 1)
                mask += 1
            mask = mask ^ ( 1 << bit_num)
            return (data & mask)
        elif isinstance(data, bytearray) or isinstance( data, bytes ):
            data_len = len(data)
            data = int.from_bytes(data, byteorder='big')
            len_data_bin = len(bin(data))-2
            for i in range(len_data_bin):
                mask = (mask << 1)
                mask += 1
            mask = mask ^ ( 1 << bit_num)
            return (data & mask).to_bytes(data_len,'big')
        else:
            return None

    def Check_Bit(self, data, bit_num):
        '''
        #*********************************************************************
        # проверка значения бита переменной int
        # [data] - данные
        # [bit_num] - номер бита для установки
        #*********************************************************************
        :param data:
        :param bit_num: начинается с 0
        :return: 1 если установлен, 0 если не установлен, None если данные не распознаны
        '''
        if isinstance(data, int):
            return (data >> bit_num) & 1
        elif isinstance(data, bytearray) or isinstance(data, bytes):
            return (int.from_bytes(data, byteorder='big') >> bit_num) & 1
        else:
            return None
