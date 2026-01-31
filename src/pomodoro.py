from PySide6.QtWidgets import QMainWindow, QWidget, QLCDNumber, QPushButton, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import QSize, QTimer, Slot, Qt


def convert_to_msec(mm: int, ss: int) -> int:
    return (mm * 60 + ss) * 1000


class MainTimer(QTimer):
    def __init__(self, msec):
        super().__init__()
        self.setSingleShot(True)
        self.setInterval(msec)


# Timer to trigger display update every second 
class OneSecTimer(QTimer):
    def __init__(self):
        super().__init__()
        self.setSingleShot(False)
        self.setInterval(500)
        self.setTimerType(Qt.PreciseTimer)


class TimerDisplay(QLCDNumber):
    def __init__(self, min: int, sec=0):
        super().__init__(5) # Only 5 characters, timer cannot display > 60mins 
        self.display(f"{min:02d}:{sec:02d}")
        self.setMinimumSize(QSize(300, 130))


class TimerButtons(QWidget):
    def __init__(self):
        super().__init__()
        self.start_pause_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")
        self.buttons_not_start_state()
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.start_pause_btn)
        self.layout.addWidget(self.stop_btn)

    def buttons_not_start_state(self):
        self.start_pause_btn.setText("Start")
        self.stop_btn.setEnabled(False)

    def buttons_started_state(self):
        self.start_pause_btn.setText("Pause")
        self.stop_btn.setEnabled(True)

    def buttons_paused_state(self):
        self.start_pause_btn.setText("Resume")
        self.stop_btn.setEnabled(True)


class PomodoroWindow(QWidget):
    def __init__(self, minutes: int, seconds=0):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.timer_ongoing = False
        self.minutes = minutes
        self.seconds = seconds

        self.timer_display = TimerDisplay(minutes, seconds)
        self.main_timer = MainTimer(convert_to_msec(minutes, seconds))
        self.main_timer.timeout.connect(self.timer_complete)

        self.update_display_timer = OneSecTimer()
        self.update_display_timer.timeout.connect(self.update_display)

        self.buttons = TimerButtons()
        self.buttons.start_pause_btn.released.connect(self.start_or_pause_timer)
        self.buttons.stop_btn.released.connect(self.reset_timer)

        self.layout.addWidget(self.timer_display)
        self.layout.addWidget(self.buttons)
    
    @Slot()
    def update_display(self):
        remaining_time = max(0, self.main_timer.remainingTime()) // 1000 
        minutes = remaining_time // 60 
        seconds = remaining_time % 60 
        self.timer_display.display(f"{minutes:02d}:{seconds:02d}")

    @Slot()
    def start_or_pause_timer(self):
        if not self.timer_ongoing:
            self.update_display_timer.start()
            self.main_timer.start()
            self.buttons.buttons_started_state()
            self.timer_ongoing = True
            
        else:
            remaining_time = self.main_timer.remainingTime()
            self.update_display_timer.stop()
            self.main_timer.stop()
            self.main_timer.setInterval(remaining_time)
            self.buttons.buttons_paused_state()
            self.timer_ongoing = False

    @Slot()
    def timer_complete(self):
        self.reset_timer()

        # TODO: Add beep
        # TODO: Add update to db 

    @Slot()
    def reset_timer(self):
        self.update_display_timer.stop()
        self.main_timer.setInterval(convert_to_msec(self.minutes, self.seconds))
        self.timer_display.display(f"{self.minutes:02d}:{self.seconds:02d}")
        self.buttons.buttons_not_start_state()
        self.timer_ongoing = False 