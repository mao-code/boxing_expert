import serial


class SerialManager:
    def __init__(self, port="COM3", baud_rate=500000, timeout=0.1):
        """
        :param port:
        :param baud_rate:
        :param timeout:
        """
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.ser = serial.Serial(port, baud_rate, timeout=timeout)

    def cmd2send(self, command):
        if command in ['l', 'r']:
            self.ser.write(command.encode('ascii'))
            print(f"Command '{command}' sent.")

            # feedbacks = self.read_feedback()
            # print("Feedbacks:", feedbacks)
        else:
            print("Invalid command. Use 'l' or 'r' only.")

    def read_feedback(self):
        feedback = []
        while self.ser.in_waiting > 0:
            uno_feedback = self.ser.readline().decode('ascii').strip()
            feedback.append(uno_feedback)
        return feedback

    def close(self):
        """
        關閉串口。
        """
        if self.ser.is_open:
            self.ser.close()
            print("Serial port closed.")


if __name__ == "__main__":
    serial_manager = SerialManager(port="/dev/cu.usbmodem1101", baud_rate=500000)

    try:
        while True:
            user_input = input('Enter "l" for left or "r" for right: ').strip().lower()
            serial_manager.cmd2send(user_input)

            # feedbacks = serial_manager.read_feedback()
            # for feedback in feedbacks:

    except KeyboardInterrupt:
        print("Program interrupted by user.")
    finally:
        serial_manager.close()