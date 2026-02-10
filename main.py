from src.pomodoro import PomodoroWindow, TimerTypeNames
from src import data, config 
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Slot, QThread
from PySide6.QtGui import QAction
from playsound3 import playsound, PlaysoundException

class ChimeThread(QThread):
    def __init__(self, audio_name):
        super().__init__()
        self.audio_name = audio_name 

    @Slot()
    def run(self):
        try:
            playsound(f"audio/{self.audio_name}.wav")
        except PlaysoundException:
            pass # Do nothing if playsound fail 


class PomodoroMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_filename = "./files/config.json"
        self.focus = True # To determine whether to update csv when timer completes 
        self.configs = config.read_config(self.config_filename)
        self.chime_thread = ChimeThread(self.configs[config.ConfigKeys.alarm])

        self.setWindowTitle("Pomodoro")
        self.pomo_window = PomodoroWindow(self.configs[config.ConfigKeys.timer][TimerTypeNames.focus_s]) # Default is short focus timer 
        self.setCentralWidget(self.pomo_window)

        self.pomo_window.main_timer.timeout.connect(self.timer_complete)
        self.pomo_window.timer_type_buttons.button_clicked_type.connect(self.switch_timer_type)

        timer_setting_action = QAction("Timer", self)
        timer_setting_action.triggered.connect(self.show_timer_settings)

        alarm_setting_action = QAction("Alarm", self)
        alarm_setting_action.triggered.connect(self.show_alarm_settings)

        menu = self.menuBar()
        setting_menu = menu.addMenu("&Settings") 
        setting_menu.addAction(timer_setting_action)
        setting_menu.addAction(alarm_setting_action) 

    @Slot()
    def timer_complete(self):
        if self.focus:
            data.add_row_to_csv("./files/pomodoro_data.csv", (self.pomo_window.minutes))
        self.chime_thread.audio_name = self.configs[config.ConfigKeys.alarm]
        self.chime_thread.start()

    @Slot()
    def switch_timer_type(self, new_timer_type: str):
        if "focus" in new_timer_type.lower():
            self.focus = True
        else:
            self.focus = False

        self.pomo_window.update_timer_and_display(self.configs[config.ConfigKeys.timer][new_timer_type]) 

    @Slot()
    def show_timer_settings(self):
        dialog = config.TimerSettingDialog(self.configs[config.ConfigKeys.timer])
        dialog.new_timer_dict_signal.connect(self.update_timer)
        dialog.exec() 

    @Slot()
    def show_alarm_settings(self):
        dialog = config.AlarmSettingDialog(config.get_audio_choices("audio"), self.configs[config.ConfigKeys.alarm])
        dialog.new_alarm.connect(self.update_alarm_setting)
        dialog.audio_choices_combo_box.currentTextChanged.connect(self.play_alarm)
        dialog.exec() 

    @Slot()
    def update_timer(self, new_timer_dict):
        """Triggered when new timer settings are saved. update the main timer and json file"""

        self.configs[config.ConfigKeys.timer] = new_timer_dict
        config.write_config(self.config_filename, self.configs)

        # Update display if timer not running otherwise update minute attribute to refresh display when timer completes 
        if not self.pomo_window.timer_ongoing:
            self.pomo_window.update_timer_and_display(new_timer_dict[self.pomo_window.timer_type_buttons.current_button_type])
        else:
            self.pomo_window.minutes = new_timer_dict[self.pomo_window.timer_type_buttons.current_button_type]

    @Slot()
    def update_alarm_setting(self, new_alarm):
        self.configs[config.ConfigKeys.alarm] = new_alarm
        self.chime_thread.audio_name = new_alarm
        config.write_config(self.config_filename, self.configs)

    @Slot()
    def play_alarm(self, audio_name):
        self.chime_thread.audio_name = audio_name
        self.chime_thread.start()


if __name__ == "__main__":
    app = QApplication([])
    window = PomodoroMainWindow()
    window.show()
    app.exec()