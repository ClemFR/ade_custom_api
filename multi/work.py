import uuid

class GenerateWeek:
    def __init__(self, ade_id, date, width=1280, height=720):
        self.ade_id = ade_id
        self.date = date
        self.width = 1280
        self.height = 720

        self.work_id = uuid.uuid4()


class EndThread:
    pass