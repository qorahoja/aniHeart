import json

class Setting:
    def __init__(self, file : str = 'data/settings.json'):
        self.file = file

        js = open(file, 'r')
        self.data = json.loads(js.read())
        js.close()

        # data = {'forced_chanels' : [], 'pasword' : '1234'}
        # js.write(json.dumps(data))

    def update(self):
        js = open(self.file, 'w')
        js.write(json.dumps(self.data))

        # print("Settings updated           ", end = '\r')