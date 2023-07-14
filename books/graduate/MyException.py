import os
import sys
script_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_path)


class MyException(Exception):
    def __init__(self, message):
        super(MyException, self).__init__()
        self.message = message

    def __str__(self):
        return self.message
        