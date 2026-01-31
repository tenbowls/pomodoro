from src.pomodoro import PomodoroWindow
from src import data_manager
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Slot

class PomodoroMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro")
        self.window = PomodoroWindow(0, 10)
        self.setCentralWidget(self.window)
        self.window.main_timer.timeout.connect(self.update_csv)

    @Slot()
    def update_csv(self):
        data_manager.add_row_to_csv("pomodoro_data.csv", (self.window.minutes * 60 + self.window.seconds))

if __name__ == "__main__":
    app = QApplication([])
    window = PomodoroMainWindow()
    window.show()
    app.exec()