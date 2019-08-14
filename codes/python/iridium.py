from serial import Serial as ser
from time import sleep
from execp import printf
import os
from time import sleep
from monitor import reschedule
import traceback
from subprocess import call, Popen, PIPE


class dial():
    def __init__(self, *args, **kwargs):
        self.username = "amigos3"
        self.pwd = "zaehoD1a"
        self.hostname = "128.138.135.165"
        self.router_host = "http://192.168.0.1:8080/cgi-bin/menuform.cgi?"
        self.router_config = "ppp1_local_ip=192.168.0.1&ppp1_remote_ip=192.168.0.90&ppp1_override_remote_ip=enable"
        self.router_confirm = "form=form_activate_config"
        self.router_auth = ("admin", "")
        self.default_path = "/media/mmcblk0p1/"

    def list_files(self, folder):
        """List files in a directory recursively

        Arguments:
            folder {string} -- Path to the base directory

        Returns:
            [List] -- List of all file
        """
        walker = os.walk(folder)
        list_file = []
        for root, dirs, files in walker:
            for name in files:
                path = os.path.join(root, name)
                list_file.append(path)
        return list_file

    def test_connection(self):
        """Test up/down of server.

        Returns:
            FTP Instance -- FTP instance with connection to server
        """
        ftp = None
        from ftplib import FTP
        try:
            ftp = FTP(self.hostname, timeout=5*60)
        except:
            printf("FTP connection failed. Trying once more :(")
            try:
                ftp = FTP(self.hostname, timeout=5*60)
            except:
                pass
        try:
            welcome = ftp.getwelcome()
        except:
            reschedule(re="Out")
            printf("Can not connect to server 128.138.135.165. No more try")
            if ftp is not None:
                return ftp
            return None
        else:
            printf("Server sent a greeting :)")
            greeting = None
            try:
                welcome = welcome[welcome.find("*****"): welcome.find(" *** ")]
                greeting = []
                greeting = greeting.append(welcome)
            except:
                reschedule(re="Out")
                printf("Server sent no greetting")
            if greeting is not None:
                printf(greeting)
            return ftp
        return ftp

    def compress_file(self, file_name, own=False):
        """Compress file to tar.zip.

        Arguments:
            file_name {string} -- File + path

        Keyword Arguments:
            own {bool} -- Set if not auto generated by the software (default: {False})

        Returns:
            String or None -- Path to the new conpressed file, None if failure
        """
        try:
            folder_name = file_name
            from execp import amigos_Unit
            unit = amigos_Unit()
            if file_name.find(".log") != -1:
                folder_name = folder_name.replace(".log", '')
            elif file_name.find(".jpg") != -1:
                folder_name = folder_name.replace(".jpg", '')
            import datetime
            time_now = datetime.datetime.now()
            time_now = str(time_now.year) + "_" + str(time_now.month) + "_" + \
                str(time_now.day) + "_" + str(time_now.hour) + \
                "_" + str(time_now.minute) + "_"
            if file_name.find("\n") != -1:
                file_name = file_name.replace("\n", '')
                folder_name = folder_name.replace("\n", '')
            newname = folder_name.split("/")
            time_now = time_now+newname[-1]+unit
            newname[-1] = time_now
            try:
                folder_name = "/".join(newname)
            except:
                self.update_log(file_name)
                return None
            printf("zipping file ")
            p = Popen("tar czf {0} {1}".format(folder_name+".tar.gz", file_name),
                      stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
            out = p.communicate()
            # print(out)
            sleep(2)
            return folder_name+".tar.gz"
        except:
            printf("zipping failed :(")
            traceback.print_exc(
                file=open("/media/mmcblk0p1/logs/system.log", "a+"))
            return None

    def send(self, path_file, own=False):
        """Send ftp.

        Arguments:
            path_file {string} -- File + path

        Keyword Arguments:
            own {bool} -- Set if not auto generated by the software (default: {False})

        Returns:
            [Bool] -- If ftp is successful
        """
        try:
            printf("Getting server status")
            ftp = self.test_connection()
            if ftp is None:
                printf("Client server is down.")
                return False
            new = path_file
            path_file = self.compress_file(path_file, own)
            if path_file is None:
                printf("No {0} found".format(new.split("/")[-1]))
                return False
            printf("zipping done :)")
            # print(path_file)
            printf("Login into server ...")
            ftp.login(user=self.username, passwd=self.pwd)
            printf("Login successfully :)")
            printf("Starting {0} tranfer now!".format(path_file.split("/")[-1]))
            response = ftp.storbinary("STOR " + path_file.split("/")
                                      [-1], open(path_file, 'rb'), blocksize=1000)
            ftp.quit()
            if response.find("successfully") == -1:
                printf("Failed to transfere files :(")
                return False
            printf("Transfere finished successfully :)")
            printf(response.replace("\n", ""))
            printf("Backing up files now ...")
            from monitor import backup
            backup(path_file, own)
            return True
        except:
            reschedule(re="Out")
            printf("Dial out failed :(")
            traceback.print_exc(
                file=open("/media/mmcblk0p1/logs/system.log", "a+"))
            return False

    def clean_up(self, resp, name):
        """Delete a file after it is sent

        Arguments:
            resp {Boll} -- Return value from the sent
            name {String} -- Name + path to the file
        """
        try:
            if resp:
                call("rm  -rf {0}".format(name), shell=True)
            else:
                printf("Unknown error occurred. Dial out exit too soon :(")
                return
        except:
            pass

    def update_log(self, files, push=False):
        """Update the record on the dial out files

        Arguments:
            files {string or list} -- List of file to keep track of

        Keyword Arguments:
            push {bool} -- Generate a new list of files to keep track off (default: {False})

        Returns:
            bool -- True of success and false otherwise
        """
        if push:
            printf("Making record of dial out files")
            for index, fil in enumerate(files):
                file_path = self.default_path+fil
                if os.path.isdir(file_path):
                    files = self.list_files(file_path)
                    for index, item in enumerate(files):
                        with open(self.default_path+"logs/dialout_list.log", "a+") as listd:
                            listd.write(item + "\n")
                else:
                    with open(self.default_path+"logs/dialout_list.log", "a+") as listd:
                        listd.write(file_path + "\n")
            push = False
            return True
        printf("Updating dial out files record")
        in_waiting = ""
        pop = ""
        with open(self.default_path+"logs/dialout_list.log", "r") as listd:
            in_waiting = listd.readlines()
        from copy import deepcopy
        for index, item in enumerate(in_waiting):
            if item.find(files) != -1:
                new_waiting = deepcopy(in_waiting)
                pop = new_waiting.pop(index)
                with open(self.default_path+"logs/dialout_list.log", "w+") as listd:
                    listd.write("")
                for inde, ite in enumerate(new_waiting):
                    if ite not in ["", " ", None, " \n", "\n"]:
                        with open(self.default_path+"logs/dialout_list.log", "a+") as listd:
                            listd.write(ite)
                index = 0
                break
        return True

    def send_dir(self, files):
        """Send files in a directory.

        Arguments:
            files {String} -- files list in the directory
        """
        if not files:
            printf("This direcory is empty")
        else:
            for index, fil in enumerate(files):
                if fil.find("tar.gz") != -1:
                    self.clean_up(True, fil)
                    self.update_log(fil)

                else:
                    if fil in ["", " ", None, " \n", "\n"]:
                        return
                    self.print_queue(files, index, fil)
                    resp = self.send(fil)
                    if resp:
                        self.update_log(fil)
                        self.clean_up(resp, fil)

    def print_queue(self, filename, index, name):
        """Print the next element for dial out in queue

        Arguments:
            filename {list} -- all files to be send
            index {[type]} -- index of the current file that is been sent
            name {[type]} -- the name of the current file that is been sent
        """
        next_in = "Nothing"
        if index+1 < len(filename):
            next_in = filename[index+1]
            if next_in.find(".log") != -1 or next_in.find(".jpg") != -1:
                next_in = next_in.split("/")[-1]
        printf("Preparing {0} to be sent. Next in queue {1} ...".format(
            name.split("/")[-1], next_in))

    def send_fails(self):
        """send fails dial out files. Similar to send_leftover but do recursively

        Returns:
            Bool -- Return True if some tasks that fails has been sent or false otherwise
        """
        in_waiting = None
        try:
            with open(self.default_path+"logs/dialout_list.log", "r") as listd:
                in_waiting = listd.readline()
        except:
            return False
        if in_waiting not in ["", " ", None, " \n", "\n"]:
            print("Sending files that fails previously")
            self.Out()
        return True

    def send_leftover(self):
        """Send all failed dial out task

        Returns:
            Bool -- True if success false otherwise
        """
        in_waiting = []
        try:
            with open(self.default_path+"logs/dialout_list.log", "r") as listd:
                in_waiting = listd.readlines()
        except:
            return False
        if in_waiting:
            if in_waiting[0] in ["", " ", None, " \n", "\n"] and len(in_waiting) < 2:
                return False
            printf("Sending files that could not be sent")
            for index, item in enumerate(in_waiting):
                if item.find("tar.gz") != -1:
                    self.clean_up(True, item)
                    self.update_log(item)
                elif item not in ["", " ", None, " \n", "\n"]:
                    if os.path.isdir(item):
                        files = self.list_files(item)
                        self.send_dir(files)
                    else:
                        resp = self.send(item)
                        if resp:
                            print(item)
                            self.update_log(item)
                            self.clean_up(True, item)
            return True
        return False

    def Out(self, filename=None):
        """Dial out.

        Keyword Arguments:     filename {[type]} -- Path + file to dial
        out. Support list  (default: {None})
        """
        printf("Starting dial out session")
        from gpio import iridium_off, iridium_on, router_off, router_on, modem_off, modem_on
        from monitor import timing
        from timeit import default_timer as timer
        start = timer()
        iridium_on(1)
        router_on(1)
        modem_on(1)
        sleep(30)
        try:
            files_to_send = ["logs/gps_binex.log", "picture", "dts", "logs/system.log"]
            if filename != None:
                if isinstance(filename, basestring):
                    printf("Sending requested file {0} ...".format(filename))
                    self.send(filename, own=True)
            if not self.send_leftover():
                if filename is None:
                    filename = files_to_send
                printf("Start sending  files ...")
                self.update_log(filename, push=True)
                for index, name in enumerate(filename):
                    file_path = self.default_path+name
                    if os.path.isdir(file_path):
                        self.print_queue(filename, index, name)
                        printf("This file is a directory")
                        printf("Generating files list from this directory")
                        files = self.list_files(file_path)
                        self.send_dir(files)
                    else:
                        self.print_queue(filename, index, name)
                        resp = self.send(self.default_path+name)
                        self.update_log(file_path)
                        self.clean_up(resp, file_path)
            self.send_fails()
            from execp import welcome
            welcome()
            printf(
                "The state of the schedule so far is presented in the table below.", date=True)
            reschedule(run="Out")
            from monitor import get_stat
            get_stat()
            reschedule(start=True)
            end = timer()
            timing("Out", end-start)
            printf("All Done with dial out session")

        except:
            reschedule(re="Out")
            printf("Dial out failed ")
            traceback.print_exc(
                file=open("/media/mmcblk0p1/logs/system.log", "a+"))
        finally:
            iridium_off(1)
            router_off(1)
            modem_off(1)

    def In(self, time_out=20):
        """Execute dial in.

        Keyword Arguments:     time_out {int} -- dial in timeout
        (default: {20})
        """
        try:
            from requests import post
            from gpio import iridium_off, iridium_on, router_off, router_on, modem_off, modem_on
            from monitor import timing
            from timeit import default_timer as timer
            printf("Started dial in section")
            start = timer()
            iridium_on(1)
            router_on(1)
            modem_on(1)
            sleep(10)
            reply = post(self.router_host+self.router_config, auth=self.router_auth)
            if reply.status_code != 200:
                printf(
                    "Failed to configure the router ip6600. Exiting now, will try again shortly!")
                reschedule(re="In")
                return

            sleep(2)
            reply = post(self.router_host+self.router_confirm, auth=self.router_auth)
            if reply.status_code != 200:
                printf(
                    "Could not save the dial in conjuration. Exiting now, will try again shortly!")
                reschedule(re="In")
                return
            update = 0
            i = 0
            while time_out > 0:
                try:
                    with open("/media/mmcblk0p1/logs/dialin", "r") as d:
                        update = int(d.read())
                except:
                    pass
                sleep(60)
                time_out = time_out + update - i
                i = i+1
            printf("Dial in section timeout")
            reschedule(run="In")
            end = timer()
            timing("In", end-start)
        except Exception as err:
            printf("Dial out session failed with {0}".format(err))
            traceback.print_exc(
                file=open("/media/mmcblk0p1/logs/system.log", "a+"))
            reschedule(re="In")
        finally:
            iridium_off(1)
            router_off(1)
            modem_off(1)


class sbd():
    def __init__(self):
        self.port = ser('/dev/ttyS1')
        self.port.baudrate = 9600
        self.port.open()

    def SBD(self):
        from gpio import disable_serial, iridium_off, sbd_off, iridium_on, sbd_on, enable_serial
        from monitor import timing
        from timeit import default_timer as timer
        try:
            start = timer()
            iridium_on(1)
            sbd_on(1)
            sleep(1)
            enable_serial()
            sleep(10)
            self.solar_SBD()
            end = timer()
            timing("SBD", end-start)
            reschedule(run="SBD")
        except:
            reschedule(re="SBD")
        finally:
            disable_serial()
            sbd_off(1)
            iridium_off(1)

    def solar_SBD(self):
        # collect dictionary of solar data from other scripts
        from solar import solar_live
        solarclass = solar_live()
        solar = solarclass.solar_sbd()

        # Commands send to iridium solar data
        message_sent = False
        sbd_port = ser("/dev/ttyS1")
        sbd_port.flushInput()
        sbd_port.write("AT\r\n")
        sleep(2)
        check = sbd_port.read(sbd_port.inWaiting())
        if check.find("OK") != -1:
            sbd_port.write("AT&K0\r\n")
            sleep(2)
            check = sbd_port.read(sbd_port.inWaiting())
            if check.find("OK") != -1:
                sbd_port.write("AT+SBDWT={0}\r\n".format(solar))
                sleep(2)
                check = sbd_port.read(sbd_port.inWaiting())
                if check.find("OK") != -1:
                    sbd_port.write("AT+SBDIX\r\n")
                    sleep(15)
                    array = sbd_port.read(sbd_port.inWaiting())
                    array1 = array.split(":")[1].split(",")
                    if array1[0] == " 0":
                        message_sent = True
                else:
                    printf("AT+SBDWT message command did not work to the iridium (Solar)")
            else:
                printf("AT&K0 command did not work to the iridium (Solar)")
        else:
            printf("AT command did not work to the iridium (Solar)")

        # If solar message sent successfully, move on and call the vaisala funciton
        if message_sent is True:
            printf("Solar message successfuly sent, moving to iridium Vaisala")
            self.vaisala_SBD()
        else:
            printf("Solar message DID NOT SEND, still moving to iridium Vaisala")
            self.vaisala_SBD()

    def vaisala_SBD(self):
        # collect dictionary of vaisala data from other script
        from vaisala import Average_Reading
        vaisalaclass = Average_Reading()
        vaisala = vaisalaclass.vaisala_sbd()

        # Commands send to iridium vaisala data
        message_sent = False
        sbd_port = ser("/dev/ttyS1")
        sbd_port.flushInput()
        sbd_port.write("AT\r\n")
        sleep(2)
        check = sbd_port.read(sbd_port.inWaiting())
        if check.find("OK") != -1:
            sbd_port.write("AT&K0\r\n")
            sleep(2)
            check = sbd_port.read(sbd_port.inWaiting())
            if check.find("OK") != -1:
                sbd_port.write("AT+SBDWT={0}\r\n".format(vaisala))
                sleep(2)
                check = sbd_port.read(sbd_port.inWaiting())
                if check.find("OK") != -1:
                    sbd_port.write("AT+SBDIX\r\n")
                    sleep(15)
                    array = sbd_port.read(sbd_port.inWaiting())
                    array1 = array.split(":")[1].split(",")
                    if array1[0] == " 0":
                        message_sent = True
                else:
                    printf("AT+SBDWT message command did not work to the iridium (Vaisala)")
            else:
                printf("AT&K0 command did not work to the iridium (Vaisala)")
        else:
            printf("AT command did not work to the iridium (Vaisala)")

        # If vaisala message sent successfully, move on and call the cr funciton
        if message_sent == True:
            printf("Vaisala message successfuly sent, moving to iridium CR")
            self.cr_SBD()
        else:
            printf("Vaisala message DID NOT SEND, still moving to iridium CR")
            self.cr_SBD()

    def cr_SBD(self):
        # collect dictionary of CR data from other scripts
        from cr1000x import cr1000x
        crclass = cr1000x()
        cr = crclass.cr_sbd()

        # Commands send to iridium CR data
        message_sent = False
        sbd_port = ser("/dev/ttyS1")
        sbd_port.flushInput()
        sbd_port.write("AT\r\n")
        sleep(2)
        check = sbd_port.read(sbd_port.inWaiting())
        if check.find("OK") != -1:
            sbd_port.write("AT&K0\r\n")
            sleep(2)
            check = sbd_port.read(sbd_port.inWaiting())
            if check.find("OK") != -1:
                sbd_port.write("AT+SBDWT={0}\r\n".format(cr))
                sleep(2)
                check = sbd_port.read(sbd_port.inWaiting())
                if check.find("OK") != -1:
                    sbd_port.write("AT+SBDIX\r\n")
                    sleep(15)
                    array = sbd_port.read(sbd_port.inWaiting())
                    array1 = array.split(":")[1].split(",")
                    if array1[0] == " 0":
                        message_sent = True
                else:
                    printf("AT+SBDWT message command did not work to the iridium (CR)")
            else:
                printf("AT&K0 command did not work to the iridium (CR)")
        else:
            printf("AT command did not work to the iridium (CR)")

        # If CR message sent successfully, move on and call the seabird funciton
        if message_sent == True:
            printf("CR message successfuly sent, moving to iridium seabird")
            self.seabird_SBD()
        else:
            printf("CR message DID NOT SEND, still moving to iridium seabird")
            self.seabird_SBD()

    def seabird_SBD(self):
        # collect dictionary of seabird data from other scripts
        from seabird import seabird_sbd
        seabird = seabird_sbd

        # Commands send to iridium seabird data
        message_sent = False
        sbd_port = ser("/dev/ttyS1")
        sbd_port.flushInput()
        sbd_port.write("AT\r\n")
        sleep(2)
        check = sbd_port.read(sbd_port.inWaiting())
        if check.find("OK") != -1:
            sbd_port.write("AT&K0\r\n")
            sleep(2)
            check = sbd_port.read(sbd_port.inWaiting())
            if check.find("OK") != -1:
                sbd_port.write("AT+SBDWT={0}\r\n".format(seabird))
                sleep(2)
                check = sbd_port.read(sbd_port.inWaiting())
                if check.find("OK") != -1:
                    sbd_port.write("AT+SBDIX\r\n")
                    sleep(15)
                    array = sbd_port.read(sbd_port.inWaiting())
                    array1 = array.split(":")[1].split(",")
                    if array1[0] == " 0":
                        message_sent = True
                else:
                    printf("AT+SBDWT message command did not work to the iridium (seabird)")
            else:
                printf("AT&K0 command did not work to the iridium (seabird)")
        else:
            printf("AT command did not work to the iridium (seabird)")

        # If seabird message sent successfully, move on and call the aquadopp funciton
        if message_sent == True:
            printf("seabird message successfuly sent, moving to iridium aquadopp")
            self.aquadopp_SBD()
        else:
            printf("seabird message DID NOT SEND, still moving to iridium aquadopp")
            self.aquadopp_SBD()

    def aquadopp_SBD(self):
        # collect dictionary of aquadopp data from other scripts
        from aquadopp import aquadopp_sbd
        aquadopp = aquadopp_sbd

        # Commands send to iridium aquadopp data
        message_sent = False
        sbd_port = ser("/dev/ttyS1")
        sbd_port.flushInput()
        sbd_port.write("AT\r\n")
        sleep(2)
        check = sbd_port.read(sbd_port.inWaiting())
        if check.find("OK") != -1:
            sbd_port.write("AT&K0\r\n")
            sleep(2)
            check = sbd_port.read(sbd_port.inWaiting())
            if check.find("OK") != -1:
                sbd_port.write("AT+SBDWT={0}\r\n".format(aquadopp))
                sleep(2)
                check = sbd_port.read(sbd_port.inWaiting())
                if check.find("OK") != -1:
                    sbd_port.write("AT+SBDIX\r\n")
                    sleep(15)
                    array = sbd_port.read(sbd_port.inWaiting())
                    array1 = array.split(":")[1].split(",")
                    if array1[0] == " 0":
                        message_sent = True
                else:
                    printf("AT+SBDWT message command did not work to the iridium (aquadopp)")
            else:
                printf("AT&K0 command did not work to the iridium (aquadopp)")
        else:
            printf("AT command did not work to the iridium (aquadopp)")

        # If aquadopp message sent successfully, move on and call the (next device) funciton
        if message_sent == True:
            printf("aquadopp message successfuly sent, moving to iridium (next device)")
            # self.(next device)
        else:
            printf("aquadopp message DID NOT SEND, still moving to iridium (next device)")
            # self.(next device)

    def read(self):
        try:
            port = ser('/dev/ttyS1')
            port.baudrate = 9600
            port.timeout = 60
            port.open()
        except:
            printf('Unable to open port')
            return None
        rev = port.read(port.inWaiting())
        return rev


if __name__ == "__main__":
    sbd()
