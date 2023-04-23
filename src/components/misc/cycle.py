import time

DAY_LENGTH = 24 * 3600
HOUR_LENGTH = 3600
MINUTE_LENGTH = 60


class GameTime:
    def __init__(self, main_window, scene, ratio=1.0):
        self.window = main_window
        self.scene = scene
        self.start_time = None
        self.started = False
        self.ratio = ratio
        self.ingame = "00:00:00:00"
        self.realtime = "00:00:00:00"
        self.time_offset = 0
        self.real_elapsed = 0
        self.in_game_elapsed = 0
        self.real_days = 0
        self.in_game_days = 0
        self.real_hours = 0
        self.in_game_hours = 0
        self.real_minutes = 0
        self.in_game_minutes = 0
        self.real_seconds = 0
        self.in_game_seconds = 0
        self.paused = False

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def start(self):
        self.started = True
        self.__setattr__("start_time", time.time())

    def advance_time(self, seconds):
        self.time_offset += seconds

    def advance_days(self, count = 1):
        self.advance_time(DAY_LENGTH * count)

    def advance_hours(self, count = 1):
        self.advance_time(HOUR_LENGTH * count)

    def advance_eighthours(self):
        self.advance_hours(8)

    def current_time(self, real=False):
        elapsed = time.time() - self.start_time
        if real:
            return elapsed
        return elapsed * self.ratio + self.time_offset

    def is_day(self):
        cycle = self.current_time() / (24 * 3600)
        return cycle % 2 < 1

    def update_time(self):
        """Updates the time variables"""
        self.real_elapsed = self.current_time(True)  # in seconds
        self.in_game_elapsed = self.current_time(False) # in seconds

        self.real_days = int(self.real_elapsed / (24 * 3600))  # in days
        self.in_game_days = int(self.in_game_elapsed / (24 * 3600))  # in days

        self.real_hours = int((self.real_elapsed % (24 * 3600)) / 3600)  # in hours
        self.in_game_hours = int((self.in_game_elapsed % (24 * 3600)) / 3600)  # in hours

        self.real_minutes = int((self.real_elapsed % 3600) / 60)  # in minutes
        self.in_game_minutes = int((self.in_game_elapsed % 3600) / 60)  # in minutes

        self.real_seconds = int(self.real_elapsed % 60)  # in seconds
        self.in_game_seconds = int(self.in_game_elapsed % 60)  # in seconds

        self.realtime = f"{self.real_days:02d}:{self.real_hours:02d}:{self.real_minutes:02d}:{self.real_seconds:02d}"
        self.ingame = f"{self.in_game_days:02d}:{self.in_game_hours:02d}:{self.in_game_minutes:02d}:{self.in_game_seconds:02d}"
        
    def transfer_day(self):
        if self.ingame[3:] == "23:59:59":
            return True            

    def get_ingame_time(self):
        return int(self.current_time())

    def update(self):
        self.paused = self.scene.paused
        if self.started and not self.paused:
            self.update_time()
