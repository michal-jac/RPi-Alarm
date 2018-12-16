import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# Output pins
sirene = 18			# sirene loudspeeker
led_light = 19		# LED lights
photo_switch = 12	# photo switch device
radio_selector = 16 # came radio device

#In/Out config
GPIO.setup(sirene, GPIO.OUT) 		#sirene as out
GPIO.output(sirene, False)
GPIO.setup(led_light, GPIO.OUT) 	#led otuput (relay for switching)
GPIO.output(led_light, False)
GPIO.setup(photo_switch, GPIO.IN)	#photo switch input
GPIO.setup(radio_selector, GPIO.IN) #came radio device input

GPIO.add_event_detect(photo_switch, GPIO.FALLING) 	#add falling edge detection to the photoelectric switch
GPIO.add_event_detect(radio_selector, GPIO.FALLING)	#add falling edge detecion to the came radio switch

# PWM configuration
p = GPIO.PWM(sirene, 750) 	#set sirene channel to PWM with 750 Hz frequency
#p.start(50) 				#start PWM on sirene with 50% duty cycle



# Functions
# Turn on sirene signal
def StartSirene(PWM_Channel):
	PWM_Channel.start(50)
	for freq in range(750, 2000, 10):
		PWM_Channel.ChangeFrequency(freq)
		time.sleep(0.01)
	time.sleep(0.5)
	for freq in range(2000, 750, -10):
		PWM_Channel.ChangeFrequency(freq)
		time.sleep(0.01)

# Turn output to ON
def TurnON(OutputPin):
	GPIO.output(OutputPin, True)

# Turn output to OFF
def TurnOFF(OutputPin):
	GPIO.output(OutputPin, False)

# Blink LED desired number of times
def BlinkLED(LED_Channel, HowManyTimes):
	for x in range(HowManyTimes):
		TurnON(LED_Channel)
		time.sleep(1)
		TurnOFF(LED_Channel)
		time.sleep(1)


# Check if falling edge on Input (Device)
def CheckInput(Device):
	if GPIO.event_detected(Device) == True:
		#print("Action detected!")
		return True
	else: return False

# Machine Case: AlarmOFF
def AlarmOFF(LED_Channel, PWM_Channel):
	TurnOFF(LED_Channel)		#Turn OFF LEDs
	PWM_Channel.stop()				#stop PWM on Sirene channel
	time.sleep(1)			#wait 3 s
	BlinkLED(LED_Channel, 1)	#Blink LED light once
	print('Alarm Turned OFF completely')
	

# Machine Case: Active
def AlarmON(LED_Channel, PWM_Channel):
		TurnON(LED_Channel)
		StartSirene(PWM_Channel)
		
		
# Machine Case : AlarmInit
def AlarmInit(LED_Channel,PWM_Channel):
	PWM_Channel.start(50)					#Init PWM
	BlinkLED(LED_Channel, 2)		#Blink LED twice
	print('Alarm Turned ON')


def StandBy(CaseCounter):
    CaseCounter = 0
    return CaseCounter
        
	
#Dictionary definition as case selector
CaseSelector = {	0 : StandBy,
					1 : AlarmInit,
					2 : AlarmON,
					3 : AlarmOFF
				}


#Variables
CaseCounter = 0
AlarmReady = False

#PROBLEM DO ROZWIAZANIA: PIN INPUT DEBOUNCE
#POWODUJE TO WYKONANIE KODU NA ZBOCZE OPODAJACE PRZY ZALACZANIU STYKOW

#DLUGOSC TRWANIA OPADAJACEGO ZBOCZA - KILKUKROTNE ODCZYTANIE TEJ SAMEJ WARTOSCI
#(delay 0.1s poprawil sprawe)



try:
    while 1:
	time.sleep(0.1)
        if CheckInput(radio_selector) == True:
			if AlarmReady == True:
				AlarmOFF(led_light,p)
				AlarmReady = False
				CaseCounter = 0
				print("Deactivated")
			else:
				print(CaseCounter)
				print("Activated")
           		AlarmInit(led_light,p)        #Init Alarm (blink twice)
          		AlarmReady = True           #and set as ready

         if CheckInput(photo_switch) == True and AlarmReady == True:
         	CaseCounter = 2
        while CaseCounter == 2:
        	AlarmON(led_light,p)
        	if CheckInput(radio_selector) == True:
        		CaseCounter = 1
        	time.sleep(0.05)



except KeyboardInterrupt:
	p.stop()
	GPIO.cleanup()


