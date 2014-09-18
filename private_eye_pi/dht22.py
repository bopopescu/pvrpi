#!/usr/bin/env python
"""
DHT22.py 9.00 temperature and humidity to PrivateEyePi
---------------------------------------------------------------------------------
 Works conjunction with host at www.privateeyepi.com                              
 Visit projects.privateeyepi.com for full details                                 
                                                                                  
 J. Evans February 2014       
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
 WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
 CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                                                       
                                                                                  
 Revision History                                                                  
 V1.00 - Created
 V1.01 - Fixed bug with Fahrenheit displaying as "C" not "F"    
 V9    - Rules Release                                                                                                       
-----------------------------------------------------------------------------------
"""

import time
import RPi.GPIO as GPIO
import urllib2
import subprocess
import globals
from alarmfunctionsr import UpdateHost
from alarmfunctionsr import GetDataFromHost

import re
#...

def GetData():
        global temp
        global humidity
        
        # This is the routine that interfaces with the sensor and
        # return a value that will get sent to the host and displayed  
        # onb the dashboard. 

        if globals.PrintToScreen: print "Reading DHT22 sensor"
        
        false_reading = False  
        while True:
                #Thanks to Adafruit for the DHT22 sensor interface written in c   
                output = subprocess.check_output(["/home/Adafruit-Raspberry-Pi-Python-Code/Adafruit_DHT_Driver/Adafruit_DHT", "2302", str(globals.dht22_gpio)]);
                humidity_matches = re.search("Hum =\s+([0-9.]+)", output)
                temp_matches = re.search("Temp =\s+([0-9.]+)", output)
                if (not temp_matches or not humidity_matches):
                        ++false_reading
                        if false_reading==5:
                                return(False)
                        else:
                                continue
                break;
            
        temp = float(temp_matches.group(1))
        
        if globals.PrintToScreen: print "Temperature = " + str(temp)
        
        # Do the Farenheit conversion if required
        if globals.Farenheit:
                temp=temp*1.8+32
  
        # search for humidity printout
        humidity_matches = re.search("Hum =\s+([0-9.]+)", output)
        
        humidity = float(humidity_matches.group(1))
        
        if globals.PrintToScreen: print "Humidity = " + str(humidity)
        
        return(True)

def fileexists(filename):
        try:
                with open(filename): pass
        except IOError:
                return False 
        return True
                                  
def NotifyHost():
        global temp
        global humidity
        
        TempBuffer = []
        rt=GetData()
        if rt==False: #fail
                return (0)
        TempBuffer.append(temp)
        if globals.Farenheit:
                TempBuffer.append(1)
        else:
                TempBuffer.append(0)
        TempBuffer.append(globals.dht22_pin_no)
        TempBuffer.append(humidity)
        UpdateHost(14, TempBuffer)
        return (0)
                   
def main():
        global start_time
        global elapsed_time
        
        globals.init()

        # Interval in seconds that temperature is sent to the server
        start_time = time.time()
        
        NotifyHost()
        
        #Main Loop
        while True:
             
                elapsed_time = time.time() - start_time
                
                if (elapsed_time > 300):
                        start_time = time.time()
                        # Get the latest temperature
                        NotifyHost()
                    
                time.sleep(.2)

if __name__ == "__main__":
        main()