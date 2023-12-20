# Smart Biometric Lock with Touchscreen Keypad

## Overview

This project involves the development of a Smart Biometric Lock system using an ESP32 or similar microcontroller. The system incorporates a touchscreen keypad interface with an ILI9341 TFT display and communicates over WiFi. Users can enter a 4-digit code using the touchscreen keypad, and the system communicates with a backend server for authentication.

## Components

![Block Diagram for project](https://github.com/cmartema/IoT-Project/src/BlockDiagram.png)

### Libraries:

- SPI
- Adafruit_GFX
- Adafruit_ILI9341
- Adafruit_TSC2007
- WiFi
- WiFiClient

### Hardware Components:

- TFT Display: ILI9341 (TFT_CS, TFT_DC)
- Touchscreen: Adafruit_TSC2007 (STMPE_CS)
- Built-in LED (ledPin)
- SD Card (SD_CS)

## Pin Configuration

### TFT Display:

- TFT_CS: 15
- TFT_DC: 33

### Touchscreen:

- STMPE_CS: 32

### SD Card:

- SD_CS: 14

### Built-in LED:

- ledPin: LED_BUILTIN

## Touchscreen Calibration

The touchscreen calibration values are set as follows:

- TSC_TS_MINX: 300
- TSC_TS_MAXX: 3800
- TSC_TS_MINY: 185
- TSC_TS_MAXY: 3700

## WiFi Configuration

The code connects to the WiFi network with the following credentials:
- SSID: "wifi_ssid"
- Password: "wifi_password"

## User Interface (Keypad)

The `keypad()` function is defined to draw a simple keypad on the TFT display. It includes keys for digits 0-9 and the letters A and E.

## Main Functionality

- Users can enter a 4-digit code using the touchscreen keypad.
- The entered digits are displayed on the TFT screen.
- The system establishes a TCP connection to a specified host (IP address and port) and sends/receives messages.
- Special actions are triggered when specific keys are pressed, such as sending a message to the host.
- Debugging information is provided through the built-in LED (LED_BUILTIN).

## How to Use

1. Set the WiFi credentials in the code.

2. Upload the code to an ESP32 or compatible microcontroller.

3. Connect the TFT display, touchscreen, and other required components.

4. Monitor the serial output for debugging information.

---

# Fingerprint Door Control System

## Hardware Components

- **Fingerprint Sensor:** The project utilizes a fingerprint sensor to capture and recognize fingerprints. The sensor communicates with the microcontroller over UART.

- **Microcontroller:** A microcontroller, likely an ESP32 or similar device, is used to control the overall system. It manages communication with the fingerprint sensor, handles door control logic, and communicates with a remote server for authentication.

- **Door Lock Mechanisms:** The system controls electronic door locks to secure or release doors based on successful authentication.

## Software Components

### Microcontroller Code



- **FingerPrintSensor Class:** Represents the interface to the fingerprint sensor, providing methods for fingerprint enrollment, authentication, and system parameter management.

- **Networking:** Manages the communication with a remote server for user authentication and door control decisions.

- **Door Control:** Logic for controlling the electronic door locks based on successful authentication.

### Server-side Code



## Usage

1. **Setup:** Connect the hardware components, including the fingerprint sensor, microcontroller, and electronic door locks.

2. **Configure Wi-Fi:** Update the Wi-Fi credentials in the microcontroller code to enable network connectivity.

3. **Run the Code:** Upload the MicroPython code to the microcontroller. Ensure the fingerprint sensor is correctly connected.

4. **Server Configuration:** Configure the server with the necessary databases for storing user information, fingerprints, and passcodes.

5. **User Interaction:** Users can either present a fingerprint or enter a passcode to unlock doors. For adding new fingerprints, a registration process is initiated.

**Contributors**
    https://github.com/AT-OY
    https://github.com/Kenliao0603
    https://github.com/cmartema
    
