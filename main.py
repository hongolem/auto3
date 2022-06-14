pin_L = DigitalPin.P13
pin_R = DigitalPin.P2
pin_Trig = DigitalPin.P8
pin_Echo = DigitalPin.P15   #piny

path = 1
connected = 0
modeSwitch = 0
crossroadSwitch = 0
ultrasonicSwitch = 0
counting = 0
speedFactor = 80    #switchable variables

pins.set_pull(pin_L, PinPullMode.PULL_NONE)
pins.set_pull(pin_R, PinPullMode.PULL_NONE)
bluetooth.start_uart_service()
basic.show_string("S")                               #less important code

def motor_run(right = 0, left = 0, speedFactor = 80):
    PCAmotor.motor_run(PCAmotor.Motors.M1, Math.map(Math.constrain(left * (speedFactor / 100), -100, 100), -100, 100, -255, 255))
    PCAmotor.motor_run(PCAmotor.Motors.M4, Math.map(Math.constrain(right * (speedFactor / 100), -100, 100), -100, 100, -255, 255))
    
def motor_stop():
    PCAmotor.motor_stop(PCAmotor.Motors.M1)
    PCAmotor.motor_stop(PCAmotor.Motors.M4)             #run/stop motors

def on_forever():
    global counting
    if modeSwitch == 0:
        sensor_L = pins.digital_read_pin(pin_L)
        sensor_R = pins.digital_read_pin(pin_R)
        obstacle_distance = sonar.ping(pin_Trig, pin_Echo, PingUnit.CENTIMETERS)
        if (sensor_L == path) and (sensor_R == path):
            if crossroadSwitch == 0:
                motor_run(50, 50)
                counting = 0
            elif crossroadSwitch == 1:
                motor_stop()
                counting = 0
        elif (sensor_L != path) and (sensor_R != path):
            motor_stop()
            if counting >= 10:
                motor_run(-50, 50)
                basic.pause(870)
                motor_stop()
                counting = 0
            elif counting < 10:
                counting = counting + 1
                motor_stop()
                motor_run(-50, 50)
                basic.pause(100)
                motor_run(50, -50)
                basic.pause(75)                    #když dlouho nevidí cestu udělá 180,
        elif (sensor_L == path) and (sensor_R != path):
            motor_run(50, 0)
            counting = 0                #jede vlevo
        elif (sensor_L != path) and (sensor_R == path):
            motor_run(0, 50)
            counting = 0                #jede vpravo

        if obstacle_distance < 10:
            if ultrasonicSwitch == 0:
                motor_stop()
                motor_run (50, -50, 80)
                basic.pause(870)
                motor_stop()
            elif ultrasonicSwitch == 1:
                pass
    elif modeSwitch == 1:
        pass                        #zapnuto manuální řízení
forever(on_forever)                                             #autonomní mód

def on_bluetooth_connected():
    global connected, modeSwitch, path, crossroadSwitch, ultrasonicSwitch
    basic.show_icon(IconNames.HEART)
    connected = 1
    while connected == 1:
        uartData = str(bluetooth.uart_read_until(serial.delimiters(Delimiters.HASH)))
        console.log_value("data", uartData)
        print(uartData)
        if uartData == "A":
            motor_run(50, 50)
            basic.pause(300)
            motor_stop()            #jízda rovně
        elif uartData == "B":
            motor_run(-50, -50)
            basic.pause(300)
            motor_stop()            #jízda zpět
        elif uartData == "C":
            motor_run(50, -50)
            basic.pause(300)
            motor_stop()            #jízda doleva
        elif uartData == "D":
            motor_run(-50, 50)
            basic.pause(300)
            motor_stop()            #jízda doprava
        elif uartData == "E":
            pass
        elif uartData == "F":
            pass
        elif uartData == "G":
            if path == 0:
                path = 1
            elif path == 1:
                path = 0            #přepínání barvy cesty
        elif uartData == "H":
            if crossroadSwitch == 0:
                crossroadSwitch = 1
            elif crossroadSwitch == 1:
                crossroadSwitch = 0         #přepínání z automatic voliče cesty na manuál
        elif uartData == "I":
            if modeSwitch == 0:
                modeSwitch = 1
            elif modeSwitch == 1:
                modeSwitch = 0                  #manuální/automatické řízení
        elif uartData == "J":
            motor_run (50, -50, 80)
            basic.pause(870)
            motor_stop()                        #180° otočka
        elif uartData == "K":
            if ultrasonicSwitch == 0:
                ultrasonicSwitch = 1
            elif ultrasonicSwitch == 1:
                ultrasonicSwitch = 0
        elif uartData == "0":
            pass
bluetooth.on_bluetooth_connected(on_bluetooth_connected)                    #bluetooth mód

def on_bluetooth_disconnected():
    global connected
    basic.show_icon(IconNames.SAD)
    connected = 0
bluetooth.on_bluetooth_disconnected(on_bluetooth_disconnected)
bluetooth.uart_write_number(0)