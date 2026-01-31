from PySide6.QtWidgets import QWidget, QLCDNumber, QPushButton, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import QSize, QTimer, Slot, Qt, Signal 


def convert_mins_to_msec(mm: int) -> int:
    return mm * 60 * 1000


class TimerTypeNames(enumerate):
    """For reading keys from json config"""
    focus_s = "Focus (Short)"
    focus_l = "Focus (Long)"
    break_s = "Break (Short)"
    break_l = "Break (Long)"


class MainTimer(QTimer):
    def __init__(self, msec):
        super().__init__()
        self.setSingleShot(True)
        self.setInterval(msec)


# Timer to trigger display update every 0.5s
class OneSecTimer(QTimer):
    def __init__(self):
        super().__init__()
        self.setSingleShot(False)
        self.setInterval(500)
        self.setTimerType(Qt.PreciseTimer)


class TimerDisplay(QLCDNumber):
    def __init__(self, mins: int):
        super().__init__(5) # Only 5 characters, timer cannot display > 60mins 
        self.update_display(mins)
        self.setMinimumSize(QSize(300, 130))

    def update_display(self, minutes: int, seconds=0):
        self.display(f"{minutes:02d}:{seconds:02d}")


class TimerTypeButtons(QWidget):
    button_clicked_type = Signal(str)

    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.short_focus_btn = QPushButton("Focus (S)")
        self.long_focus_btn = QPushButton("Focus (L)")
        self.short_break_btn = QPushButton("Break (S)")
        self.long_break_btn = QPushButton("Break (L)")

        self.short_focus_btn.setEnabled(False)

        self.short_focus_btn.released.connect(self.short_focus_clicked)
        self.long_focus_btn.released.connect(self.long_focus_clicked)
        self.short_break_btn.released.connect(self.short_break_clicked)
        self.long_break_btn.released.connect(self.long_break_clicked)

        self.layout.addWidget(self.short_focus_btn)
        self.layout.addWidget(self.long_focus_btn)
        self.layout.addWidget(self.short_break_btn)
        self.layout.addWidget(self.long_break_btn)
        self.layout.setContentsMargins(0,0,0,0)

    def enable_all_buttons(self):
        self.short_focus_btn.setEnabled(True)
        self.long_focus_btn.setEnabled(True)
        self.short_break_btn.setEnabled(True)
        self.long_break_btn.setEnabled(True)

    def disable_all_buttons(self):
        self.short_focus_btn.setEnabled(False)
        self.long_focus_btn.setEnabled(False)
        self.short_break_btn.setEnabled(False)
        self.long_break_btn.setEnabled(False)

    @Slot()
    def short_focus_clicked(self):
        self.button_clicked_type.emit(TimerTypeNames.focus_s)
        self.enable_all_buttons()
        self.short_focus_btn.setEnabled(False)

    @Slot()
    def long_focus_clicked(self):
        self.button_clicked_type.emit(TimerTypeNames.focus_l)
        self.enable_all_buttons()
        self.long_focus_btn.setEnabled(False)

    @Slot()
    def short_break_clicked(self):
        self.button_clicked_type.emit(TimerTypeNames.break_s)
        self.enable_all_buttons()
        self.short_break_btn.setEnabled(False)

    @Slot()
    def long_break_clicked(self):
        self.button_clicked_type.emit(TimerTypeNames.break_l)
        self.enable_all_buttons()
        self.long_break_btn.setEnabled(False)


class TimerCtrlButtons(QWidget):
    def __init__(self):
        super().__init__()
        self.start_pause_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")
        self.buttons_not_start_state()
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.start_pause_btn)
        self.layout.addWidget(self.stop_btn)
        self.layout.setContentsMargins(0,0,0,0)

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
    def __init__(self, minutes):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.timer_ongoing = False
        self.minutes = minutes

        # Display Widget and Main Timer Widget
        self.timer_display = TimerDisplay(minutes)
        self.main_timer = MainTimer(convert_mins_to_msec(minutes))
        self.main_timer.timeout.connect(self.timer_complete)

        # Timer to update display 
        self.update_display_timer = OneSecTimer()
        self.update_display_timer.timeout.connect(self.update_display)

        # Buttons for timer types 
        self.timer_type_buttons = TimerTypeButtons()

        # Buttons to control main timers
        self.timer_ctrl_buttons = TimerCtrlButtons()
        self.timer_ctrl_buttons.start_pause_btn.released.connect(self.start_or_pause_timer)
        self.timer_ctrl_buttons.stop_btn.released.connect(self.reset_timer)

        # Layout
        self.layout.addWidget(self.timer_type_buttons)
        self.layout.addWidget(self.timer_display)
        self.layout.addWidget(self.timer_ctrl_buttons)
    
    @Slot()
    def update_display(self):
        remaining_time = max(0, self.main_timer.remainingTime()) // 1000 
        minutes = remaining_time // 60 
        seconds = remaining_time % 60 
        self.timer_display.update_display(minutes, seconds)

    @Slot()
    def start_or_pause_timer(self):
        if not self.timer_ongoing:
            self.update_display_timer.start()
            self.main_timer.start()
            self.timer_ctrl_buttons.buttons_started_state()
            self.timer_type_buttons.disable_all_buttons()
            self.timer_ongoing = True
            
        else:
            remaining_time = self.main_timer.remainingTime()
            self.update_display_timer.stop()
            self.main_timer.stop()
            self.main_timer.setInterval(remaining_time)
            self.timer_ctrl_buttons.buttons_paused_state()
            self.timer_ongoing = False

    @Slot()
    def timer_complete(self):
        self.reset_timer()

    @Slot()
    def reset_timer(self):
        self.update_display_timer.stop()
        self.main_timer.setInterval(convert_mins_to_msec(self.minutes))
        self.timer_display.update_display(self.minutes)
        self.timer_ctrl_buttons.buttons_not_start_state()
        self.timer_type_buttons.enable_all_buttons()
        self.timer_ongoing = False 

    def update_timer_and_display(self, new_minutes: int):
        self.minutes = new_minutes
        self.timer_display.update_display(new_minutes)
        self.main_timer.setInterval(new_minutes * 60 * 1000)