# Sid Arora
# UPDATED AS OF 6/25/19

# This Program will read in data from the Vaisala Weather Sensor
# It can read data over long periods of time and perform averages or can output live data

# Import Modules
import time
from time import sleep
import serial
import re
import datetime
import math
from gpio import weather_on
from gpio import weather_off
import subprocess as subprocess

# Class that will average the data for 2 minutes every 10 seconds at a speciic time every hour


class Average_Reading():
    def read_data(self):
        try:
            # Turn on Weather Station
            weather_on(1)
            sleep(10)
            # Read in the weather sensor data and write to an ascii text file
            port = serial.Serial("/dev/ttyS5")
            port.baudrate = 115200
        except:
            print("Problem with port 5 or problem with power to the vaisala")
        else:
            t = 0
            # Read composite data message (all readings) every 10 seconds for 2 minutes and write to temporary ascii text file
            while t <= 120:
                with open("/media/mmcblk0p1/amigos/amigos/logs/weather_data_ASCII.txt", "a+") as raw_data:
                    port.flushInput()
                    data = port.readline()
                    raw_data.write(data)
                    sleep(10)
                t = t+10
        finally:
            # Turn off Weather Station
            port.close()
            weather_off(1)

    def clean_data(self):
        try:
            # put all the mesaurements into a matrix (array of arrays)
            float_array_final = []
            string_array_final = []
            with open("/media/mmcblk0p1/amigos/amigos/logs/weather_data_ASCII.txt", "r") as f:
                for line in f:
                    if "0R0" in line:
                        string_array_raw = re.findall(
                            r"[-+]?\d*\.\d+|\d+", line)
                        for i in range(0, len(string_array_raw)):
                            string_array_raw[i] = float(string_array_raw[i])
                        string_array_final = string_array_raw[2:]
                        float_array_final.append(string_array_final)
        finally:
            # Erase the tempoerary ascii data file
            subprocess.call(
                "rm /media/mmcblk0p1/amigos/amigos/logs/weather_data_ascii.txt", shell=True)
        return string_array_final, float_array_final

    def average_data(self):
        # Call first two functions in correct order
        self.read_data()
        string_array_final, float_array_final = self.clean_data()
        # average the corresponding elements and output a sinlge array of numbers
        data_array_final = []
        for j in range(0, len(string_array_final)):
            numbers_sum = 0
            numbers_divide = 0
            for k in range(0, len(float_array_final)):
                numbers_sum = numbers_sum + float_array_final[k][j]
            numbers_divide = numbers_sum/(len(float_array_final))
            data_array_final.append(round(numbers_divide, 3))
        # Write the averaged array elements to a final log file - append
        now = datetime.datetime.now()
        with open("/media/mmcblk0p1/amigos/amigos/logs/weather_data.log", "a+") as hourly:
            hourly.write("Current Date and Time: " +
                         now.strftime("%Y-%m-%d %H:%M:%S\n"))
            hourly.write("Wind Direction Average (Degrees): " +
                         str(data_array_final[0]) + ".\n")
            hourly.write("Wind Speed Average (m/s): " +
                         str(data_array_final[1]) + ".\n")
            hourly.write("Air Temperature (C): " +
                         str(data_array_final[2]) + ".\n")
            hourly.write("Relative Humidity (%RH): " +
                         str(data_array_final[3]) + ".\n")
            hourly.write("Air Pressure (hPa): " +
                         str(data_array_final[4]) + ".\n")
            hourly.write("Rain Accumulation (mm): " +
                         str(data_array_final[5]) + ".\n")
            hourly.write("Rain Duration (s): " +
                         str(data_array_final[6]) + ".\n")
            hourly.write("Rain Intensity (mm/h): " +
                         str(data_array_final[7]) + ".\n")
            hourly.write("Rain Peak Intensity (mm/h): " +
                         str(data_array_final[11]) + ".\n")
            hourly.write("Hail Accumulation (hits/cm^2): " +
                         str(data_array_final[8]) + ".\n")
            hourly.write("Hail Duration (s): " +
                         str(data_array_final[9]) + ".\n")
            hourly.write("Hail Intensity (hits/cm^2/hour): " +
                         str(data_array_final[10]) + ".\n")
            hourly.write("Hail Peak Intensity (hits/cm^2/hour): " +
                         str(data_array_final[12]) + ".\n")
            hourly.write("Vaisala Heating Temperature (C): " +
                         str(data_array_final[13]) + ".\n")
            hourly.write("Vaisala Heating Voltage (V): " +
                         str(data_array_final[14]) + ".\n")
            hourly.write("Vaisala Supply Voltage (V): " +
                         str(data_array_final[15]) + ".\n\n\n")


# Class that will allow the user to access specific weather data points whenever needed
class Live_Data():
    def read_data(self):
        try:
            # Turn on Weather Station
            weather_on(1)
            sleep(10)
            # Read lines from port
            port = serial.Serial("/dev/ttyS5")
            port.baudrate = 115200
        except:
            print("Problem with port 5 or problem with power to the vaisala")
        else:
            t = 0
            # Take data for 5 seconds to make sure that a composite data message has time to send from the Vaisala
            while t <= 5:
                with open("/media/mmcblk0p1/amigos/amigos/logs/weather_data_ASCII.txt", "a+") as raw_data:
                    port.flushInput()
                    data = port.readline()
                    raw_data.write(data)
                    sleep(1)
                t = t+1
        finally:
            # Turn off Weather Station
            port.close()
            if is_on == False:
                weather_off(1)
            else:
                is_on = False

    def clean_data(self):
        try:
            self.read_data()
            string_array_final = []
            with open("/media/mmcblk0p1/amigos/amigos/logs/weather_data_ASCII.txt", "r") as f:
                # only take the last 0R0 line of the 5 - second data collection interval for translation
                for line in f:
                    if "0R0" in line:
                        string_array_raw = re.findall(
                            r"[-+]?\d*\.\d+|\d+", line)
                        for i in range(0, len(string_array_raw)):
                            string_array_raw[i] = float(string_array_raw[i])
                        string_array_final = string_array_raw[2:]
        finally:
            # Erase the temporary ascii text file
            subprocess.call(
                "rm /media/mmcblk0p1/amigos/amigos/logs/weather_data_ascii.txt", shell=True)
        return string_array_final

    def weather_all(self):
        # Print all the weather data
        string_array_final = self.clean_data()
        now = datetime.datetime.now()
        print("\nCurrent Date and Time: " + now.strftime("%Y-%m-%d %H:%M:%S"))
        print("Wind Direction Average (Degrees): " +
              str(string_array_final[0]) + ".")
        print("Wind Speed Average (m/s): " + str(string_array_final[1]) + ".")
        print("Air Temperature (C): " + str(string_array_final[2]) + ".")
        print("Relative Humidity (%RH): " + str(string_array_final[3]) + ".")
        print("Air Pressure (hPa): " + str(string_array_final[4]) + ".")
        print("Rain Accumulation (mm): " + str(string_array_final[5]) + ".")
        print("Rain Duration (s): " + str(string_array_final[6]) + ".")
        print("Rain Intensity (mm/h): " + str(string_array_final[7]) + ".")
        print("Rain Peak Intensity (mm/h): " +
              str(string_array_final[11]) + ".")
        print("Hail Accumulation (hits/cm^2): " +
              str(string_array_final[8]) + ".")
        print("Hail Duration (s): " + str(string_array_final[9]) + ".")
        print("Hail Intensity (hits/cm^2/hour): " +
              str(string_array_final[10]) + ".")
        print("Hail Peak Intensity (hits/cm^2/hour): " +
              str(string_array_final[12]) + ".")
        print("Vaisala Heating Temperature (C): " +
              str(string_array_final[13]) + ".")
        print("Vaisala Heating Voltage (V): " +
              str(string_array_final[14]) + ".")
        print("Vaisala Supply Voltage (V): " +
              str(string_array_final[15]) + ".\n")

    def wind_direction(self):
        string_array_final = self.clean_data()
        now = datetime.datetime.now()
        print("\nCurrent Date and Time: " + now.strftime("%Y-%m-%d %H:%M:%S"))
        print("Wind Direction Average (Degrees): " +
              str(string_array_final[0]) + ".\n")

    def wind_speed(self):
        string_array_final = self.clean_data()
        now = datetime.datetime.now()
        print("\nCurrent Date and Time: " + now.strftime("%Y-%m-%d %H:%M:%S"))
        print("Wind Speed Average (m/s): " +
              str(string_array_final[1]) + ".\n")

    def air_temperature(self):
        string_array_final = self.clean_data()
        now = datetime.datetime.now()
        print("\nCurrent Date and Time: " + now.strftime("%Y-%m-%d %H:%M:%S"))
        print("Air Temperature (C): " + str(string_array_final[2]) + ".\n")

    def humidity(self):
        string_array_final = self.clean_data()
        now = datetime.datetime.now()
        print("\nCurrent Date and Time: " + now.strftime("%Y-%m-%d %H:%M:%S"))
        print("Relative Humidity (%RH): " + str(string_array_final[3]) + ".\n")

    def pressure(self):
        string_array_final = self.clean_data()
        now = datetime.datetime.now()
        print("\nCurrent Date and Time: " + now.strftime("%Y-%m-%d %H:%M:%S"))
        print("Air Pressure (hPa): " + str(string_array_final[4]) + ".\n")

    def rain_accumulation(self):
        string_array_final = self.clean_data()
        now = datetime.datetime.now()
        print("\nCurrent Date and Time: " + now.strftime("%Y-%m-%d %H:%M:%S"))
        print("Rain Accumulation (mm): " + str(string_array_final[5]) + ".\n")

    def rain_duration(self):
        string_array_final = self.clean_data()
        now = datetime.datetime.now()
        print("\nCurrent Date and Time: " + now.strftime("%Y-%m-%d %H:%M:%S"))
        print("Rain Duration (s): " + str(string_array_final[6]) + ".\n")

    def rain_intensity(self):
        string_array_final = self.clean_data()
        now = datetime.datetime.now()
        print("\nCurrent Date and Time: " + now.strftime("%Y-%m-%d %H:%M:%S"))
        print("Rain Intensity (mm/h): " + str(string_array_final[7]) + ".\n")

    def rain_peak_intensity(self):
        string_array_final = self.clean_data()
        now = datetime.datetime.now()
        print("\nCurrent Date and Time: " + now.strftime("%Y-%m-%d %H:%M:%S"))
        print("Rain Peak Intensity (mm/h): " +
              str(string_array_final[11]) + ".\n")

    def hail_accumulation(self):
        string_array_final = self.clean_data()
        now = datetime.datetime.now()
        print("\nCurrent Date and Time: " + now.strftime("%Y-%m-%d %H:%M:%S"))
        print("Hail Accumulation (hits/cm^2): " +
              str(string_array_final[8]) + ".\n")

    def hail_duration(self):
        string_array_final = self.clean_dat a()
        now = datetime.datetime.now()
        print("\nCurrent Date and Time: " + now.strftime("%Y-%m-%d %H:%M:%S"))
        print("Hail Duration (s): " + str(string_array_final[9]) + ".\n")

    def hail_intensity(self):
        string_array_final = self.clean_data()
        now = datetime.datetime.now()
        print("\nCurrent Date and Time: " + now.strftime("%Y-%m-%d %H:%M:%S"))
        print("Hail Intensity (hits/cm^2/hour): " +
              str(string_array_final[10]) + ".\n")

    def hail_peak_intensity(self):
        string_array_final = self.clean_data()
        now = datetime.datetime.now()
        print("\nCurrent Date and Time: " + now.strftime("%Y-%m-%d %H:%M:%S"))
        print("Hail Peak Intensity (hits/cm^2/hour): " +
              str(string_array_final[12]) + ".\n")

    def vaisala_unit(self):
        # Print the 3 vaisala unit data points
        string_array_final = self.clean_data()
        now = datetime.datetime.now()
        print("\nCurrent Date and Time: " + now.strftime("%Y-%m-%d %H:%M:%S"))
        print("Vaisala Heating Temperature (C): " +
              str(string_array_final[13]) + ".")
        print("Vaisala Heating Voltage (V): " +
              str(string_array_final[14]) + ".")
        print("Vaisala Supply Voltage (V): " +
              str(string_array_final[15]) + ".\n")


# Main function
if __name__ == "__main__":
    # if script is called then start the data averaging process
    Avg_Reading = Average_Reading()
    Avg_Reading.average_data()