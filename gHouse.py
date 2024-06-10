""" Greenhouse.py
Vietnamese-German University
Nguyen Trung Tin, Team 03
Read data received from 3 sensors: temp, light, soi-moisture sensor.
Based on codes from WriteTempLDR.py, PrintTempLDR.py, weblamp.py,
and a lot more from lecture notes and ppt files of Mr. Richard G. Bradley, MAL, MSM
connections:
Light Sensor (LDR) connected to A0 (14)
Temperature Sensor connected to A1 (15)
Soil-moisture Sensor connected to A2 (16)"""

#########################################
#         Import Libraries              #
#########################################
import time
import datetime
import math
from flask import Flask, render_template    # for website
import smtplib                              # for email
from email.mime.text import MIMEText        #for email
from wiringx86 import GPIOGalileo as GPIO
gpio = GPIO(debug=False)
#########################################
"""---------END of "Import Libraries" section-------"""


#########################################
#           Global Variables            #
#########################################
#
""" Light Sensor """
LDRpin = 14
MaxIllum = 800            # Reading from LDR under bright light
#########################################
#
""" Temperature Sensor""" #based on Mr.Bradley's PrintTempLDR.py
TempPin = 15
ThermValue = 3975;        #value of the thermistor
#########################################
#
""" Soil Moisture"""
SoilPin = 16
#
""" for email """
USERNAME = "gali.greenhouse.noreply"
PASSWORD = "tindeptrai123@"
MAILTO  = ""
#
""" Trigger-relay pins """
lightBulb = 8 
CPUfan = 9
waterPump = 10
#############3###########################
"""--------END of "Global Variables" section---------"""

# Set pins to be used as an ANALOG input GPIO pin.
gpio.pinMode(LDRpin, gpio.ANALOG_INPUT)  # Grove Light Sensor
gpio.pinMode(TempPin, gpio.ANALOG_INPUT) # Grove Temperature Sensor
gpio.pinMode(SoilPin, gpio.ANALOG_INPUT) # Grove Soil Moisture Sensor

# Set pins to be used as an DIGITAL input GPIO pin.
gpio.pinMode(lightBulb, gpio.OUTPUT)
gpio.pinMode(CPUfan, gpio.OUTPUT)
gpio.pinMode(waterPump, gpio.OUTPUT)


########################################
#             Functions                #
########################################

""" Get HostName """
def GetHostName(): #fruitful function
    fout = open('/etc/hostname', 'r')
    HostName = fout.read() #print entire file
    fout.close()
    x = len(HostName)
    HostName = HostName[0:x-1]
    print "Readings from: " + HostName
    return HostName

""" Get TimeZone Offset """
def GetOffset(): #fruitful function
    offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
    offset = offset / 60 / 60 * -1
    print "TimeZone Offset: " + str(offset)
    return offset

""" Get Readings """
def GetLDR(): #fruitful function
    LDRValue = 100 * gpio.analogRead(LDRpin) /MaxIllum
    #print "LDR Value " + str(LDRValue) + "%"
    return LDRValue

def GetTemp(): #based on Mr.Bradley's PrintTempLDR.py #fruitful function
	TempValue = float(gpio.analogRead(TempPin))
	resistValue = float((1023.0-TempValue)/TempValue) # get the resistance of the sensor; 
	HouseTemp=1/(math.log(resistValue)/ThermValue+1/298.15)-273.15 # convert to temperature per datasheet ;
	#print ("House Temp %.2f"  % HouseTemp)
	return HouseTemp

def GetSoil(): #fruitful function
 SoilMoisture = gpio.analogRead(SoilPin)
 #print 'Soil Moisture value: ' + str(SoilMoisture)
 return SoilMoisture

""" email """
def email_for_LDR():
    msg = MIMEText('Hello,\nGreenhouse assistant here !!, \nEmergency!!!, \nSomething covered the Greenhouse')
    msg['Subject'] = 'Hoo Lee Sheet!!! LDR'
    msg['From'] = USERNAME
    msg['To'] = MAILTO

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo_or_helo_if_needed()
    server.starttls()
    server.ehlo_or_helo_if_needed()
    server.login(USERNAME,PASSWORD)
    server.sendmail(USERNAME, MAILTO, msg.as_string())
    server.quit()

def email_for_Temp():
    msg = MIMEText('Hello,\nGreenhouse assistant here !!, \nEmergency!!!,\nSomething wrong with the Temperatue happened')
    msg['Subject'] = 'Hoo Lee Sheet!!! Temperature'
    msg['From'] = USERNAME
    msg['To'] = MAILTO

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo_or_helo_if_needed()
    server.starttls()
    server.ehlo_or_helo_if_needed()
    server.login(USERNAME,PASSWORD)
    server.sendmail(USERNAME, MAILTO, msg.as_string())
    server.quit()

def email_for_Mois():
    msg = MIMEText('Hello,\nGreenhouse assistant here !!, \nEmergency!!!,\nSomething wrong with the soil !!!')
    msg['Subject'] = 'Hoo Lee Sheet!!! Soil'
    msg['From'] = USERNAME
    msg['To'] = MAILTO

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo_or_helo_if_needed()
    server.starttls()
    server.ehlo_or_helo_if_needed()
    server.login(USERNAME,PASSWORD)
    server.sendmail(USERNAME, MAILTO, msg.as_string())
    server.quit()

""" trigger Light bulb """
def light_ON():
	gpio.digitalWrite(lightBulb, gpio.HIGH)

def light_OFF():
	gpio.digitalWrite(lightBulb, gpio.LOW)

""" trigger CPU fan """
def fan_ON():
	gpio.digitalWrite(CPUfan, gpio.HIGH)

def fan_OFF():
	gpio.digitalWrite(CPUfan, gpio.LOW)

""" trigger water pump """
def pump_ON():
	gpio.digitalWrite(waterPump, gpio.HIGH)

def pump_OFF():
	gpio.digitalWrite(waterPump, gpio.LOW)

#########################################
#               *Main*                  #
# Based on Mr.Bradley's WriteTempLDR.py #
#########################################

""" Creates file """
fout = open('Readings.txt', 'w')

""" Write Host Name """
Hostname = GetHostName()
fout.write("Readings from: " + Hostname) 
fout.write('\n') # end line 

""" Write Date of Reading """
#
# Day/Month/Year
LocalDate = time.strftime("%d/%m/%Y")
fout.write("Date of Reading: " + LocalDate) 
fout.write('\n') # end line 
#
# Write Local Time Zone Offset
Offset = GetOffset()
fout.write("Time ZOne Offset: " + str(Offset)) 
fout.write('\n') # end line 
#
""" Take Readings over time """
x = 0      #period counter
LDR = 0    #LDR value before the loop (value at 0-th loop)
Temp = 0   #Temperature value before the loop (value at 0-th loop)

try:
	while (True):

		#Readings from last period to compare 
		preLDR = LDR
		preTemp = Temp
	
	
		# Write "updates"
		x += 1
		print ' '
		print '### Loop: %d-th ###' % x
		fout.write('### Loop: ' + str(x) + '-th ###')
		fout.write('\n') # end line 
		
		# Write local time of Reading
		LocalTime = time.strftime("%H:%M:%S")
		fout.write('Time of Reading: ' + LocalTime) 
		fout.write('\n') # end line
	
		# Write Illumination
		LDR = GetLDR()
		fout.write('Illumination: ' + str(LDR) + '%' )
		fout.write('\n') # end line 
		
		# Write Temp
		Temp = GetTemp()
		fout.write("Greenhouse temperature: " + str(Temp) + ' Celsius degree')
		fout.write('\n') # end line 

		# Write Soil-moisture
		Mois = GetSoil()
		fout.write ("Soil Moisture value: " + str(Mois))
		fout.write('\n') #end line 
  
		#COntroller system initiated
		fout.write ("------Status of the fan, light, pump-----")
		fout.write('\n') #end line 
  
		""" Ligth controller sub-system """
		compareLDR = preLDR - LDR
		if LDR < 10:              # the sky is dark
			light_ON()
		
			fout.write ("- The sky is dark")
			fout.write('\n') #end line 	
			fout.write ("lightbulb: ON")
			fout.write('\n') #end line 	
		elif compareLDR >= 30:    # to see if Something cover the light sensor
			fout.write ("WARNING: Sth cover the Greenhouse")
			fout.write('\n') #end line 
			
			email_for_LDR()
			time.sleep(5)
		else:
			light_OFF()
		
			fout.write ("- The sky is bright")
			fout.write('\n') #end line 	
			fout.write ("lightbulb: OFF")
			fout.write('\n') #end line 	
  
		""" Temperature controller sub-system """
		#The allowed range is 25-30 Celsius degree
		if Temp < 25:
			light_ON()
			fan_OFF()
			
			fout.write ("- Tempeture is under 25 degree")
			fout.write('\n') #end line 	
			fout.write ("lightbulb: ON")
			fout.write('\n') #end line
			fout.write ("fan: OFF")
			fout.write('\n') #end line 	
		
		elif Temp > 30:
			light_OFF()
			fan_ON()
		
			fout.write ("- Tempeture is over 30 degree")
			fout.write('\n') #end line 	
			fout.write ("lightbulb: OFF")
			fout.write('\n') #end line
			fout.write ("fan: ON")
			fout.write('\n') #end line 	
		
		else:
			fout.write ("- The temperature is in the allowed range (25-30 Celsius)")
			fout.write('\n') #end line
			fout.write ("fan: OFF")
			fout.write('\n') #end line

		# Check if the Green house is hot or cold suddenly
		if x == 1:
			pass
		else:
			compareTemp = preTemp - Temp
			if compareTemp < -1:    # The Greenhouse get hot suddenly
				fout.write ("WARNING: the Greenhouse get hot suddenly")
				fout.write('\n') #end line 	
			
				email_for_LDR()
	
			elif compareTemp > 1:   # The Greenhouse get cold suddenly
				fout.write ("WARNING: the Greenhouse get cold suddenly")
				fout.write('\n') #end line 	
			
				email_for_LDR()

		

		### Soil Moisture controller sub-system ###
		if 0 < Mois < 300:
			pump_ON()
			time.sleep(3)
			pump_OFF()
			
			fout.write ("The soil is dry")
			fout.write('\n') #end line
			fout.write ("FIRST ATTEMP turn the pump ON for 3 second")
			fout.write('\n') #end line 	
			
			# See if the water pump is working 2nd attemp
			time.sleep(3)
			Mois = GetSoil()        #update Soil Moisture again
			if 0 < Mois < 300:
				pump_ON()
				time.sleep(3)
				pump_OFF()
				fout.write ("SECOND ATTEMP turn the pump ON for 3 second")
				fout.write('\n') #end line
		
				#Send email if water pump not working 
				time.sleep(3)
				Mois = GetSoil()    #update SOil Moisture again
				if 0 < Mois < 300:
					email_for_Mois()
			
					fout.write ("WARNING: water pump not working")
					fout.write('\n') #end line 	
	
		elif 300 <= Mois < 700:
			pump_OFF()
			
			fout.write ("-The soil is humid")
			fout.write('\n') #end line 	
			fout.write ("Water Pump: OFF")
			fout.write('\n') #end line 	
		
		else:
			email_for_Mois()
	
			fout.write ("WARNING: too much water in soil !!!")
			fout.write('\n') #end line 	

		

		# Write "end-line" indication
		print ' '
		fout.write('\n') # Writes carriage return
		
		#delay 3 seconds
		time.sleep(3)
 
except KeyboardInterrupt:
	print '\nCleaning up...'
	light_OFF()
	fan_OFF()
	pump_OFF()
	fout.close()
	gpio.cleanup()


