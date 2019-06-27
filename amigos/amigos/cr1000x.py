import datetime
from pycampbellcr1000 import CR1000
from gpio import cr1000_off, cr1000_on
from time import sleep


class cr1000x():
    def finddata(self):

        cr1000_on(1)
        sleep(90)
        device = CR1000.from_url('tcp:192.168.0.30:6785')
        Data = device.get_data('Public')
        # print(Data[0])
        data = str(Data)
        # finds strings inbetween parenthesis
        Timestamp = data[data.find("datetime(")+9:data.find(")")]
        RecNbr = data[data.find("RecNbr")+9:data.find('''), ("b'Batt_volt''')]
        batt_volt = data[data.find("Batt_volt")+13:data.find('''), ("b'Ptemp_C''')]
        Ptemp_C = data[data.find("Ptemp_C")+11:data.find('''), ("b'R6''')]
        R6 = data[data.find("R6")+6:data.find('''), ("b'R10''')]
        R10 = data[data.find("R10")+7:data.find('''), ("b'R20''')]
        R20 = data[data.find("R20")+7:data.find('''), ("b'R40''')]
        R40 = data[data.find("R40")+7:data.find('''), ("b'R2_5''')]
        R2_5 = data[data.find("R2_5")+8:data.find('''), ("b'R4_5''')]
        R4_5 = data[data.find("R4_5")+8:data.find('''), ("b'R6_5''')]
        R6_5 = data[data.find("R6_5")+8:data.find('''), ("b'R8_5''')]
        R8_5 = data[data.find("R8_5")+8:data.find('''), ("b'T6''')]
        T6 = data[data.find("T6")+6:data.find('''), ("b'T10''')]
        T10 = data[data.find("T10")+6:data.find('''), ("b'T20''')]
        T20 = data[data.find("T20")+6:data.find('''), ("b'T40''')]
        T40 = data[data.find("T40")+6:data.find('''), ("b'T2_5''')]
        T2_5 = data[data.find("T2_5")+8:data.find('''), ("b'T4_5''')]
        T4_5 = data[data.find("T4_5")+8:data.find('''), ("b'T6_5''')]
        T6_5 = data[data.find("T6_5")+8:data.find('''), ("b'T8_5''')]
        T8_5 = data[data.find("T8_5")+8:data.find('''), ("b'DT''')]
        DT = data[data.find("DT")+6:data.find('''), ('81''')]
        Q = data[data.find("'81'")+5:data.find('''), ("b'TCDT''')]
        TCDT = data[data.find("TCDT")+8:data.find(''')])''')]
        labels = ['Timestamp', 'RecNbr', 'batt_volt', 'Ptemp_C', 'R6', 'R10', 'R20', 'R2_5', 'R4_5',
                  'R6_5', 'R8_5', 'T6,', 'T10', 'T20', 'T40', 'T2_5', 'T4_5', 'T8_5', 'DT', 'Q', 'TCDT']
        values = [Timestamp, RecNbr, batt_volt, Ptemp_C, R6, R10, R20, R2_5,
                  R4_5, R6_5, R8_5, T6, T10, T20, T40, T2_5, T4_5, T8_5, DT, Q, TCDT]
        return labels, values

    def write_file(self):
        try:
            labels, values = self.finddata()
            print labels
        except:
            print('unable to locate device')
        else:
            with open("/media/mmcblk0p1/amigos/amigos/logs/thermdata.log", "a+") as therms:
                for i in range(len(labels)):
                    therms.write(labels[i] + ': ' + values[i] + "\n")
        finally:
            cr1000_off(1)

    # def test():
    #     device = CR1000.from_url('tcp:192.168.0.30:6785')
    #     data = device.get_data('Public')
    #     with open('media/mmcblk0p1/amigos/amigos/logs/cr100x.log', 'a+')as cr1000x:
    #         cr1000x.write(data)
    #         cr1000x.write('-'*50)


if __name__ == "__main__":
    # finddata()
    cr = cr1000x()
    cr.write_file()
