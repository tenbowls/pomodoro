from src.pomodoro import PomodoroWindow, TimerTypeNames
from src import data, config 
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Slot 
from playsound3 import playsound, PlaysoundException

class PomodoroMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.focus = True # To determine whether to update csv when timer completes 
        self.timer_dict, self.alarm_name = config.read_config("./files/config.json")

        self.setWindowTitle("Pomodoro")
        self.window = PomodoroWindow(self.timer_dict[TimerTypeNames.focus_s]) # Default is short focus timer 
        self.setCentralWidget(self.window)

        self.window.main_timer.timeout.connect(self.timer_complete)
        self.window.timer_type_buttons.button_clicked_type.connect(self.switch_timer_type)

    @Slot()
    def timer_complete(self):
        if self.focus:
            data.add_row_to_csv("./files/pomodoro_data.csv", (self.window.minutes * 60))
        self.play_alarm()

    @Slot()
    def switch_timer_type(self, new_timer_type: str):
        if "focus" in new_timer_type.lower():
            self.focus = True
        else:
            self.focus = False

        self.window.update_timer_and_display(self.timer_dict[new_timer_type])

    def play_alarm(self):
        try:
            playsound(f"audio/{self.alarm_name}.wav")
        except PlaysoundException:
            pass # Do nothing if playsound fail 


if __name__ == "__main__":
    app = QApplication([])
    window = PomodoroMainWindow()
    window.show()
    app.exec()