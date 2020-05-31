# coding=utf-8
# Benoetigte Module werden importiert und eingerichtet
import RPi.GPIO as GPIO
import time
 
GPIO.setmode(GPIO.BCM)
 
# Hier werden die Eingangs-Pins deklariert, an dem der Sensor angeschlossen ist.
PIN_CLK = 5
PIN_DT = 6
BUTTON_PIN = 13
 
GPIO.setup(PIN_CLK, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(PIN_DT, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(BUTTON_PIN, GPIO.IN, GPIO.PUD_UP)
 
# Benötigte Variablen werden initialisiert
Counter = 0
Richtung = True
PIN_CLK_LETZTER = 0
PIN_CLK_AKTUELL = 0
delayTime = 0.01
 
# Initiales Auslesen des Pin_CLK
PIN_CLK_LETZTER = GPIO.input(PIN_CLK)
 
# Diese AusgabeFunktion wird bei Signaldetektion ausgefuehrt
def ausgabeFunktion(null):
    global Counter
 
    PIN_CLK_AKTUELL = GPIO.input(PIN_CLK)
 
    if PIN_CLK_AKTUELL != PIN_CLK_LETZTER:
 
        if GPIO.input(PIN_DT) != PIN_CLK_AKTUELL:
            Counter += 1
            Richtung = True
        else:
            Richtung = False
            Counter = Counter - 1
 
        print ("Drehung erkannt: ")
 
        if Richtung:
            print ("Drehrichtung: Im Uhrzeigersinn")
        else:
            print ("Drehrichtung: Gegen den Uhrzeigersinn")
 
        print( "Aktuelle Position: ", Counter)
        print ("------------------------------")
 
def CounterReset(null):
    global Counter
 
    print ("Position resettet!")
    print ("------------------------------")
    Counter = 0
 
# Um einen Debounce direkt zu integrieren, werden die Funktionen zur Ausgabe mittels
# CallBack-Option vom GPIO Python Modul initialisiert
GPIO.add_event_detect(PIN_CLK, GPIO.BOTH, callback=ausgabeFunktion, bouncetime=1)
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=CounterReset, bouncetime=50)
 
 
print ("Sensor-Test [druecken Sie STRG+C, um den Test zu beenden]")
 
# Hauptprogrammschleife
try:
        while True:
            time.sleep(delayTime)
 
# Aufraeumarbeiten nachdem das Programm beendet wurde
except KeyboardInterrupt:
        GPIO.cleanup()