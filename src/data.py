from PySide6.QtWidgets import QDialog, QComboBox, QVBoxLayout, QLabel, QDateEdit, QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import QDate, Slot, Signal, Qt
import pandas as pd 
import matplotlib
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from datetime import datetime, timedelta

date_format = "%d/%m/%Y"

matplotlib.use("QtAgg")
plt.style.use("seaborn-v0_8-darkgrid")


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=8, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes=self.fig.add_subplot(111)
        super().__init__(self.fig)
        

class CustomDateEditor(QWidget):
    def __init__(self, today_date: datetime):
        super().__init__()
        self.my_layout = QHBoxLayout(self)
        q_date_today = QDate(today_date.year, today_date.month, today_date.day)

        self.start_date_editor = QDateEdit(q_date_today)
        self.start_date_editor.setMaximumDate(q_date_today)
        self.end_date_editor = QDateEdit(q_date_today)
        self.end_date_editor.setMaximumDate(q_date_today)

        self.refresh_button = QPushButton("Refresh")

        self.my_layout.addWidget(QLabel("Start:"), alignment=Qt.AlignmentFlag.AlignRight)
        self.my_layout.addWidget(self.start_date_editor, alignment=Qt.AlignmentFlag.AlignLeft)
        self.my_layout.addWidget(QLabel("End:"), alignment=Qt.AlignmentFlag.AlignRight)
        self.my_layout.addWidget(self.end_date_editor, alignment=Qt.AlignmentFlag.AlignLeft)
        self.my_layout.addWidget(self.refresh_button)


class DataDialog(QDialog):
    new_date_range = Signal(datetime, datetime)

    def __init__(self, df, parent=None):
        super().__init__(parent=parent)
        self.df = df 
        self.new_date_range.connect(self.update_plot)

        datetime_today = datetime.now()
        self.datetime_today_date = datetime(datetime_today.year, datetime_today.month, datetime_today.day)
        
        self.choices_dropdown = QComboBox()
        self.choices_dropdown.insertItems(0, ["Last 7 days", "Last 30 days", "Custom"])
        self.choices_dropdown.currentTextChanged.connect(self.dropdown_selection_changed)

        self.custom_date_editor = CustomDateEditor(datetime_today)
        self.custom_date_editor.hide()
        self.custom_date_editor.refresh_button.released.connect(self.custom_date_range)

        self.total_label = QLabel("")
        self.avg_label = QLabel("")

        self.sc = MplCanvas(self)
        self.update_plot(self.datetime_today_date + timedelta(-6), self.datetime_today_date) # Show last 7 days by default 

        self.dialog_layout = QVBoxLayout(self)
        self.dialog_layout.addWidget(self.choices_dropdown)
        self.dialog_layout.addWidget(self.custom_date_editor)
        self.dialog_layout.addWidget(self.sc)
        self.dialog_layout.addWidget(self.total_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.dialog_layout.addWidget(self.avg_label, alignment=Qt.AlignmentFlag.AlignCenter)
        

    def filter_df_by_date(self, startdate: datetime, enddate: datetime):
        filtered_df = self.df[(self.df.index >= startdate) & (self.df.index <= enddate)]

        while startdate <= enddate:
            if not startdate in filtered_df.index:
                filtered_df.loc[startdate] = 0 
            startdate += timedelta(1)

        filtered_df = filtered_df.sort_index()
        filtered_df.index = filtered_df.index.strftime(f"{date_format} (%a)")

        return filtered_df, filtered_df["Minutes"].sum(), round(filtered_df["Minutes"].mean()) 
    

    @Slot()
    def dropdown_selection_changed(self, new_text: str):
        if new_text == "Custom":
            self.custom_date_editor.show()
            q_start_date = self.custom_date_editor.start_date_editor.date()
            q_end_date = self.custom_date_editor.end_date_editor.date()
            self.new_date_range.emit(datetime(*q_start_date.getDate()), datetime(*q_end_date.getDate()))

        elif new_text == "Last 30 days":
            self.new_date_range.emit(self.datetime_today_date - timedelta(29), self.datetime_today_date)
            self.custom_date_editor.hide() 
        
        elif new_text == "Last 7 days":
            self.new_date_range.emit(self.datetime_today_date - timedelta(6), self.datetime_today_date)
            self.custom_date_editor.hide()

    
    @Slot()
    def custom_date_range(self):
        q_start_date = self.custom_date_editor.start_date_editor.date()
        q_end_date = self.custom_date_editor.end_date_editor.date()
        self.new_date_range.emit(datetime(*q_start_date.getDate()), datetime(*q_end_date.getDate()))


    @Slot()
    def update_plot(self, start_date: datetime, end_date: datetime):
        filtered_df, total_mins, avg_mins = self.filter_df_by_date(start_date, end_date)
        x_size = filtered_df.index.size
        
        self.sc.axes.cla()
        filtered_df.plot(ax=self.sc.axes, marker="o")
        self.sc.axes.set_xticks(range(x_size))
        self.sc.axes.set_xticklabels(filtered_df.index, rotation=45, ha='right', rotation_mode='anchor')
        self.sc.axes.set_xlabel(None)
        self.sc.axes.set_ylabel("Minutes")
        self.sc.axes.get_legend().remove()
        for x, y in enumerate(filtered_df["Minutes"]):
            self.sc.axes.annotate(f"{y}", (x, y), textcoords='data', fontsize=12)
        self.sc.fig.tight_layout()
        self.sc.draw()

        total_string = f"Total: {total_mins} mins"
        if total_mins > 60:
            total_string += " / "
            hrs = total_mins // 60
            mins = total_mins % 60 
            total_string += f"{hrs} hrs " if hrs > 1 else f"{hrs} hr "
            total_string += f"{mins} mins"

        avg_string = f"Average: {avg_mins} mins"
        if avg_mins > 60:
            avg_string += " / "
            hrs = avg_mins // 60
            mins = avg_mins % 60 
            avg_string += f"{hrs} hrs " if hrs > 1 else f"{hrs} hr "
            avg_string += f"{mins} mins"

        self.total_label.setText(total_string)
        self.avg_label.setText(avg_string)


def add_row_to_csv(filename: str, duration_min: int):
    with open(filename, "a") as f:
        f.write(f"{datetime.now().strftime(f"{date_format},%H:%M:%S")},{duration_min}\n")


def get_df_from_csv(filename: str):
    df = pd.read_csv(filename, names=["Date", "Time", "Minutes"]) # Assumes the columns are in this order with no header
    df["Date"] = pd.to_datetime(df["Date"], format=date_format)
    df = df.pivot_table(values="Minutes", index="Date", aggfunc="sum") 
    return df 
