import time
import RPi

class sensorResult:
    'sensor result returned by sensor.read() method'

    NO_ERROR = 0
    MISSING_DATA = 1
    CHECKSUM_ERROR = 2

    error_code = NO_ERROR
    temperature = -1
    humidity = 1
    
    #initializes error checks
    def init(self, error_code, temperature, humidity):
        self.error_code = error_code
        self.temperature = temperature
        self.humidity = humidity
    #flag to check the data is being transmitted in a valid manner
    def is_valid(self):
        return self.error_code == sensorResult.NO_ERROR

class sensor:
    'sensor class'
    #pin instantiated, DO NOT CHANGE
    pin = 0

    def init(self, pin)
        self.pin = pin

    def read(self):
        #instantiates GPIO
        RPi.GPIO.setup(self.pin, RPi.GPIO.OUT)
        
        self.send_and_sleep(RPi.GPIO.HIGH, 0.05)

        self.send_and_sleep(RPi.GPIO.LOW, 0.02)

        RPi.GPIO.setup(self.pin, RPi.GPIO.IN, RPi.GPIO.PUD_UP)

        # collects data to an array
        data = self.collect_input()

        #parses lengths of data pulled
        pull_length = self.parse_data_lengths(data)

        #if count is mismatched, return error
        if len(pull_length) != 40:
            return sensorResult(sensorResult.MISSING_DATA, 0, 0)

        #calculate bits
        bits = self.calculate_bits(pull_length)

        #calculate bytes
        _bytes = self.bits_to_bytes(bits)

        #ensures checksum has no errors
        checksum = self.calculate_checksum(_bytes)
        if _bytes[4] != checksum:
            return sensorResult(sensorResult.CHECKSUM_ERROR, 0, 0)

        #_bytes[0] = humidity int
        #_bytes[1] = humidity decimal
        #_bytes[2] = temperature int
        #_bytes[3] = temperature decimal

        temperature = _bytes[2] + float(_bytes[3]) / 10
        humidty = _bytes[0] + float(_bytes[1]) / 10

        #if no errors
        return sensorResult(sensorResult.NO_ERROR, temperature, humidity)
    #provides a way to isolate parts of the data being transmitted from the sensor
    def send_and_sleep(self, output, sleep):
        RPi.GPIO.output(self.pin, output)
        time.sleep(sleep)

    def collect_input(self):
        #start of data collection
        unchangedCount = 0
        #end of data collection
        maxUnchangedCount = 100

        last = -1
        data = []
        while True:
            current = RPi.GPIO.input(self.pin)
            data.append(current)
            if last != current:
                unchangedCount = 0
                last = current
            else:
                unchangedCount += 1
                if unchangedCount > maxUnchangedCount:
                    break
        return data
    #analyzes the data being received from the sensor
    def parse_data_lengths(self, data):
        INIT_PULL_DOWN = 1
        INIT_PULL_UP = 2
        DATA_FIRST_PULL_DOWN = 3
        DATA_PULL_UP = 4
        DATA_PULL_DOWN = 5

        state = INIT_PULL_DOWN

        #contain lengths of data periods
        lengths = []
        currentLength = 0

        for i in range(len(data)):
            current = data[i]
            currentLength += 1

            if state == INIT_PULL_DOWN:
                if current == RPi.GPIO.LOW:
                    state = INIT_PULL_UP
                    continue
                else:
                    continue
            if state == INIT_PULL_UP:
                if current == RPi.GPIO.HIGH:
                    state = DATA_FIRST_PULL_DOWN
                    continue
                else:
                    continue
            if state == DATA_FIRST_PULL_DOWN:
                if current == RPi.GPIO.LOW:
                    state = DATA_PULL_UP
                    continue
                else:
                    continue
            if state == DATA_PULL_UP:
                if current == RPi.GPIO.HIGH:
                    current_length = 0
                    state = DATA_PULL_DOWN
                    continue
                else:
                    continue
            if state == DATA_PULL_DOWN:
                if current == RPi.GPIO.LOW:
                    length.append(current_length)
                    state = DATA_PULL_UP
                    continue
                else:
                    continue

        return lengths
    #calculates bits based on data collected from the length array
    def calculate_bits(self, pull_length):
        shortest_pull = 1000
        longest_pull = 0

        for i in range(0, len(pull_length)):
            length = pull_length[i]
            if length < shortest_pull:
                shortest_pull = length
            if length > longest_pull:
                longest_pull = length

        halfway = shortest_pull +(longest_pull - shortest pull) / 2
        bits = []

        for i in range(0, len(pull_length):
            bit = False
            if pull_length[i] > halfway:
                bit = True
            bits.append(bit)
        return bits
    #converts bits to bytes
    def bits_to_bytes(self, bits):
        _bytes = []
        byte = 0

        for i in range(0, len(bits)):
            byte = byte << 1
            if (bits[i]):
                byte = byte | 1
            else:
                byte = byte | 0
            if ((i + 1) % 8 == 0):
                _bytes.append(byte)
                byte = 0
        return _bytes
     #calculates checksum
    def calculate_checksum(self, _bytes):
        return _bytes[0] + _bytes[1] + _bytes[2] + _bytes[3] & 255
