import os
import yaml
import sys
import subprocess
import json



class Housekeeping:
    def __init__(self, yaml_path=None):
        self.yaml_path = yaml_path
        with open(self.yaml_path, 'r') as f:
            data= yaml.load(f, Loader=yaml.SafeLoader)
        #need to send this data to DAQ6510_Scanning_Resistors_Using_4W_Measurement_SCPI.py
        #send data to DAQ6510_Scanning_Resistors_Using_4W_Measurement_SCPI.py
        data_str = json.dumps(data)
        # Pass the JSON string to the subprocess
        subprocess.Popen([sys.executable, 'DAQ6510_Scanning_Resistors_Using_4W_Measurement_SCPI.py', data_str])
        
       # print(data)

        pass

    def start(self, filename):
        pass

    def switch(self, filename):
        pass

    def stop(self):
        pass

Housekeeping(yaml_path='config.yml')

