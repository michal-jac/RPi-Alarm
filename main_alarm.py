import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# Output pins
sirene = 18			# sirene loudspeeker
led_light = 15		# LED lights
photo_switch = 14	# photo switch device
radio_selector = 13 # came radio device

#In/Out config
GPIO.setup(sirene, GPIO.OUT) 		#sirene as out
GPIO.setup(led_light, GPIO.OUT) 	#led otuput (relay for switching)
GPIO.setup(photo_switch, GPIO.IN)	#photo switch input
GPIO.setup(radio_selector, GPIO.IN) #came radio device input

GPIO.add_event_detect(photo_switch, GPIO.FALLING) 	#add falling edge detection to the photoelectric switch
GPIO.add_event_detect(radio_selector, GPIO.FALLING)	#add falling edge detecion to the came radio switch

# PWM configuration
p = GPIO.PWM(sirene, 750) 	#set sirene channel to PWM with 750 Hz frequency
p.start(50) 				#start PWM on sirene with 50% duty cycle


# Functions
# Turn on sirene signal
def StartSirene():
	for freq in range(750, 2000, 10):
		p.ChangeFrequency(freq)
		time.sleep(0.01)
	time.sleep(0.5)
	for freq in range(2000, 750, -10):
		p.ChangeFrequency(freq)
		time.sleep(0.01)

# Turn output to ON
def TurnON(OutputPin):
	GPIO.output(OutputPin, True)

# Turn output to OFF
def TurnOFF(OutputPin):
	GPIO.output(OutputPin, False)

# Blink LED desired number of times
def BlinkLED(LED_Channel, HowManyTimes):
	for x in xrange(HowManyTimes):
		TurnON(LED_Channel)
		time.sleep(5)
		TurnOFF(LED_Channel)


# Check if falling edge on Input (Device)
def CheckInput(Device):
	if GPIO.event_detected(Device) == True:
		print("Action detected!")
		return True
	else: return False

# Machine Case: AlarmOFF
def AlarmOFF():
	TurnOFF(led_light)		#Turn OFF LEDs
	p.stop()				#stop PWM on Sirene channel
	time.sleep(3)			#wait 3 s
	BlinkLED(led_light, 1)	#Blink LED light once
	CaseCounter = 0			#Reset Counter
	AlarmReady = False		#Reset Ready Flag
	print('Alarm Turned OFF completely')

# Machine Case: Active
def AlarmON():
		TurnON(led_light)
		StartSirene()
		
		
# Machine Case : AlarmInit
def AlarmInit():
	p.start(50)					#Init PWM
	BlinkLED(led_light, 2)		#Blink LED twice
	AlarmReady = True			#Set ready flag to True
	CaseCounter = 0				#go to stanby
	print('Alarm Turned ON')


def StandBy():
		CaseCounter = 0
	
#Dictionary definition as case selector
CaseSelector = {	0 : StandBy,
					1 : AlarmInit,
					2 : AlarmON
					3 : AlarmOFF
				}


CaseCounter = 0
AlarmReady = False

try:
	while 1:
		if CheckInput(radio_selector) == True :
				if AlarmReady == True:
					CaseCounter = 3		#Turn alarm completely OFF if AlarmFlag was set up
				else:
					CaseCounter = 1		#Init Alarm, if AlarmFlag wasn't set up

		if CheckInput(photo_switch) == True and AlarmReady == True:
			CaseCounter = 2				#Activate Alarm if photoelectric switch activated and AlarmReady flag is set up
		CaseSelector[CaseCounter]()


except KeyboardInterrupt:
	p.stop()
	GPIO.cleanup()


