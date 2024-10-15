import machine
import time

# Constants for ACS721
VREF = 3.3  # Reference voltage of the Pico (3.3V)
SENSITIVITY = 100.0  # For ACS721-5A: 100 mV per A (Check the datasheet of your specific version)

# Setup ADC on GP26 (ADC0)
adc = machine.ADC(26)

def read_current():
    # Read raw ADC value (12-bit resolution, 0-4095)
    raw_value = adc.read_u16()  # Returns a value from 0 to 65535 (16-bit)
    
    # Convert raw value to voltage
    voltage = (raw_value / 65535) * VREF

    print(f"Voltage: {voltage} V")
    
    # Calculate the current based on the sensor's sensitivity
    current = (voltage - (VREF / 2)) / (SENSITIVITY / 1000)  # Convert mV to V and calculate current
    
    return current

# Main loop to read and print current
while True:
    current = read_current()
    print("Current: {:.2f} A".format(current))
    time.sleep(1)
