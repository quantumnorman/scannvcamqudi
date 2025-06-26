arduinoport = "COM4"
keithleyname = "ASRL3::INSTR"

import serial
import time
import sys
import math as np
import pyvisa as visa
rm = visa.ResourceManager()


def initializerelay(port):
    try:
        arduino = serial.Serial(port=port, baudrate=9600, timeout=3) 
        arduino.flush()
        print("Arduino relay initialized")
        return arduino
    except:
        return print("Already initialized")

arduino = initializerelay(arduinoport)


def initializecoil(port):

    keithley = rm.open_resource(port)
    keithley.read_terloweration = "\n"
    keithley.write_termination = '\n'
    keithley.query("*IDN?")
    keithley.write("SYST:REM")
    keithley.write("OUTP:STAT:ALL OFF")
    keithley.write('APP:VOLT 3.000000,3.000000,3.000000')
    keithley.write("APP:CURR 0.000000,0.000000,0.000000")
    print("Keithley Initialized")
    return keithley

keithley = initializecoil(keithleyname)


fieldcoeffs = {
    'X' : [1.36932, -0.0174511], ##slope, intercept
    'Y' : [2.13605, 0.0259495],
    'Z' : [1.24437, -0.0123547],
}

###Keithley controls
def querychannel(inst, channel): ##inst is almost always going to be Keithley
    "Returns a dictionary, dat, with the channel number, current set, and voltage set off the current source"
    inst.write("INST:NSEL " + str(channel))
    dat = {}
    dat['channel'] = inst.query("INST?")
    dat['current'] = inst.query("MEAS:CURR?")
    dat['voltage'] = inst.query("MEAS:VOLT?")
    return dat

def query3channels(inst):
    "Returns a dictionary of the current and voltage set on all three x,y,z channels off the current source"
    dat = {}
    dat["X"] = querychannel(inst, 1)
    dat["Y"] = querychannel(inst, 2)
    dat["Z"] = querychannel(inst, 3)
    return dat

def write3channels(inst, TYPE, x, y, z):
    "Writes the TYPE (CURR or VOLT) to all three channels x, y, z on the current source"
    s = "APP:" + TYPE + " " + str(abs(x)) + ","+str(abs(y))+"," + str(abs(z))
    inst.write(s)
    return s

def fieldtocurrent(B, phi, theta, fieldcoeffs, lower, upper):
    "Converts the Bnorm, phi, and theta input values into x, y, z, current values using calibration parameters in fieldcoeffs"
    x, errx = calibbfieldtocurr(fieldcoeffs['X'], B * np.sin(theta)* np.cos(phi), lower, upper)
    y, erry = calibbfieldtocurr(fieldcoeffs['Y'], B * np.sin(theta) * np.sin(phi), lower, upper)
    z, errz = calibbfieldtocurr(fieldcoeffs['Z'], B * np.cos(theta), lower, upper)
    if errx==erry==errz==None: return x,y,z, None
    else: return x,y,z, [errx, erry, errz]

def calibbfieldtocurr(fieldcoeffs, x, lower, upper):
    "Calibrates the field to current conversion using parameters in fieldcoeffs"
    y = (x - fieldcoeffs[1])/fieldcoeffs[0]
    if lower<=y<=upper:
        return y, None
    elif y>upper: return upper, "Current clipped to " + str(upper) + "A"
    elif y<lower: return lower, "Current clipped to " + str(lower) + "A"

def setpolarity(x,y,z):
    "Determines the 3-bit polarity string to send to the Arduino Relay. 0 for positive polarity, 1 for negative polarity"
    pols = []
    if abs(x) == x: pols.append(0)
    else: pols.append(1)

    if abs(y) == y: pols.append(0)
    else: pols.append(1)

    if abs(z) == z: pols.append(0)
    else: pols.append(1)
    pols = "".join(str(pol) for pol in pols)
    setbfieldpol(pols)
    output, d = getbfieldpol()

    return d, pols


def currenttofield(fieldcoeffs, x1, y1, z1):
    "Converts the x,y,z current input values into bnorm, phi, and theta values using calibration parameters in fieldcoeffs"

    x = calibcurrtobfield(fieldcoeffs["X"], x1)
    y = calibcurrtobfield(fieldcoeffs["Y"], y1)
    z = calibcurrtobfield(fieldcoeffs["Z"], z1)

    bnorm = np.sqrt(x**2 + y**2 + z**2)
    phi = np.atan(y/x)
    theta = np.acos(z/bnorm)
    return bnorm, phi, theta

def calibcurrtobfield(fieldcoeffs, x):
    "Calibrates the current to field conversion using parameters in fieldcoeffs"
    return (x * fieldcoeffs[0]) + fieldcoeffs[1]
    

def keithleyoff():
    keithley.write("OUTP:STAT:ALL OFF")
    if keithley.query("OUTP:STAT:ALL?")== '0\n':
        print("Keithley outputs disabled")
    else: print("Error, outputs may not be disabled")


###Arduino controls
def setbfieldpol(pols): ####neg = 1, pos = 0
    "Writes the polarity to the Arduino relay. Must be a 3-bit string made of 0s and 1s"
    settings = "set " + pols + '\n'
    arduino.write(bytes(settings, 'utf-8'))
    time.sleep(.1)
    d = arduino.readline()
    arduino.flush()
    arduino.sendBreak()
    arduino.flush()
    return d

def getbfieldpol():
    "Reads the field polarities from the Arduino relay"
    settings = 'get \n'
    arduino.write(bytes(settings, 'utf-8'))
    time.sleep(.1)
    output = {}
    d1 = arduino.readline()
    d = int(d1)
    op1 = np.floor(d/100)
    if op1 == 0: output['op1'] = 'out'
    else: output['op1'] = 'in'
    op2 = np.remainder(d, 100)
    if np.floor(op2) == 0: output['op2'] = 'out'
    else: output['op2'] = 'in'
    op3 = np.remainder(d,10)
    if np.floor(op3) == 0: output['op3'] = 'out'
    else: output['op3'] = 'in'
    arduino.flush()
    arduino.sendBreak()
    arduino.flush()    
    return output, d1

def setfield(bnorm, phi, theta, magneton):
    if magneton == True:
        keithley.write("OUTP:STAT:ALL ON")

    x,y,z, errs = fieldtocurrent(bnorm, phi, theta, fieldcoeffs, -3., 3.) ## Step 1 Convert input B field values to current values
    print("Any clipped currents? ", errs)

    d,pols = setpolarity(x,y,z) ##Step 2 set the Arduino relay polarities
    print("String sent to Arduino relay and string read from Arduino: ", d, pols) ###d and pols should be the same (pols is what you're trying to set, d is what is read out)


    s = write3channels(keithley, "CURR", x,y,z) ##Step 3 sets the current (using absolute values since this is setting to the Keithley and the Arduino will deal with the polarities)
    print("String sent to kethiley: ", s)
    dat = query3channels(keithley)
    print("Final readings from Keithley: ", dat)
    xf = float(dat["X"]["current"])
    yf = float(dat["Y"]["current"])
    zf = float(dat["Z"]["current"])

    bnormf, phif, thetaf = currenttofield(fieldcoeffs, xf, yf, zf) ##Convert read values to field values
    print("Field set. Magnetic field readings:")
    print("Set Bnorm", bnorm, "\t", "Read Bnorm", bnormf)
    print("Set phi", phi, "\t", "Read phi", phif)
    print("Set theta", theta, "\t", "Read theta", thetaf)


bnorm = 0.5 ## in mT
phi = 0.7
theta = 1.57
magneton = True

setfield(bnorm, phi, theta, magneton)