import json 
from PySide6.QtWidgets import QDialog, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QDialogButtonBox, QMessageBox, QComboBox
from PySide6.QtCore import Slot, Signal 
from PySide6.QtGui import QIntValidator
from src.pomodoro import TimerTypeNames
from os import listdir 

class ConfigKeys(enumerate):
    timer = "timer"
    alarm = "alarm"

class SettingSingleRowWidget(QWidget):
    def __init__(self, label, widget):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.addWidget(QLabel(label))
        layout.addWidget(widget)
        self.setContentsMargins(0, 0, 0, 0)

class TimerSettingDialog(QDialog):
    new_timer_dict_signal = Signal(dict)

    def __init__(self, timer_dict, parent=None):
        super().__init__(parent=parent)
        self.timer_edit_dict = {
            TimerTypeNames.focus_s: QLineEdit(validator=QIntValidator()), 
            TimerTypeNames.focus_l: QLineEdit(validator=QIntValidator()), 
            TimerTypeNames.break_s: QLineEdit(validator=QIntValidator()), 
            TimerTypeNames.break_l: QLineEdit(validator=QIntValidator())
        }

        # Populate qlineedit with default values
        for k, v in timer_dict.items():
            self.timer_edit_dict[k].setText(str(v))

        layout = QVBoxLayout(self)
        for k, v in self.timer_edit_dict.items():
            layout.addWidget(SettingSingleRowWidget(k, v))

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.save_settings)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox)

    @Slot()
    def save_settings(self):
        new_timer_dict = {}
        for k, v in self.timer_edit_dict.items():
            new_time = int(v.text())

            # Check input time is within range
            if new_time < 1 or new_time > 60:
                QMessageBox.warning(self, "Invalid input", f"{new_time} minutes for '{k}' not allowed")
                return
            
            new_timer_dict[k] = int(v.text())
        self.new_timer_dict_signal.emit(new_timer_dict)
        QDialog.accept(self)

class AlarmSettingDialog(QDialog):
    new_alarm = Signal(str)

    def __init__(self, choices, current, parent=None):
        super().__init__(parent=parent)
        self.audio_choices_combo_box = QComboBox()
        self.audio_choices_combo_box.addItems(choices)
        self.audio_choices_combo_box.setCurrentText(current)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.save_alarm)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(SettingSingleRowWidget("Alarm", self.audio_choices_combo_box))
        layout.addWidget(self.buttonBox) 

    @Slot()
    def save_alarm(self):
        self.new_alarm.emit(self.audio_choices_combo_box.currentText())
        QDialog.accept(self)


def read_config(json_file: str) -> dict:
    with open(json_file, "r") as f:
        configs = json.load(f)
    return configs


def write_config(json_file: str, configs_dict):
    with open(json_file, "w") as f:
        json.dump(configs_dict, f, indent=3)

def get_audio_choices(folder: str):
    return sorted([f.split(".")[0] for f in listdir(folder)])
