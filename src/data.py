from PySide6.QtWidgets import QDialog, QComboBox, QVBoxLayout, QLabel, QDateEdit, QWidget, QHBoxLayout, QPushButton, QSizePolicy
from PySide6.QtCore import QDate
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
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes=self.fig.add_subplot(111)
        super().__init__(self.fig)
        

class CustomDateEditor(QWidget):
    def __init__(self, today_date: datetime):
        super().__init__()
        self.my_layout = QHBoxLayout(self)
        q_date_today = QDate(today_date.year, today_date.month, today_date.day)
        self.start_date_editor = QDateEdit(q_date_today)
        self.end_date_editor = QDateEdit(q_date_today)
        self.refresh_button = QPushButton("Refresh")
        self.my_layout.addWidget(QLabel("Start:"))
        self.my_layout.addWidget(self.start_date_editor)
        self.my_layout.addWidget(QLabel("End:"))
        self.my_layout.addWidget(self.end_date_editor)
        self.my_layout.addWidget(self.refresh_button)

class DataDialog(QDialog):
    def __init__(self, df, parent=None):
        super().__init__(parent=parent)
        self.df = df 

        datetime_today = datetime.now()
        datetime_date = datetime(datetime_today.year, datetime_today.month, datetime_today.day)
        filtered_df, total_mins, avg_mins = self.filter_df_by_date(datetime_date + timedelta(-6), datetime_date) # Show last 7 days by default 
        
        self.choices_dropdown = QComboBox()
        self.choices_dropdown.insertItems(0, ["Last 7 days", "Last 30 days", "Custom"])
        self.choices_dropdown.setEnabled(False) # Remove this once functionality is implemented 

        self.custom_date_editor = CustomDateEditor(datetime_today)
        self.custom_date_editor.hide()

        sc = MplCanvas(self)
        filtered_df.plot(ax=sc.axes, marker="o")
        sc.axes.set_xticklabels(sc.axes.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
        sc.axes.set_xlabel(None)
        sc.axes.set_ylabel("Minutes")
        sc.axes.get_legend().remove()
        for x, y in enumerate(filtered_df["Minutes"]):
            sc.axes.annotate(f"{y}", (x, y), textcoords='data', fontsize=12)
        sc.fig.tight_layout()
        
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

        self.total_label = QLabel(total_string)
        self.avg_label = QLabel(avg_string)

        self.dialog_layout = QVBoxLayout(self)
        self.dialog_layout.addWidget(self.choices_dropdown)
        self.dialog_layout.addWidget(self.custom_date_editor)
        self.dialog_layout.addWidget(sc)
        self.dialog_layout.addWidget(self.total_label)
        self.dialog_layout.addWidget(self.avg_label)
        

    def filter_df_by_date(self, startdate: datetime, enddate: datetime):
        filtered_df = self.df[(self.df.index >= startdate) & (self.df.index <= enddate)]

        while startdate <= enddate:
            if not startdate in filtered_df.index:
                filtered_df.loc[startdate] = 0 
            startdate += timedelta(1)

        filtered_df = filtered_df.sort_index()
        filtered_df.index = filtered_df.index.strftime(f"{date_format} (%a)")

        return filtered_df, filtered_df["Minutes"].sum(), round(filtered_df["Minutes"].mean())


def add_row_to_csv(filename: str, duration_min: int):
    with open(filename, "a") as f:
        f.write(f"{datetime.now().strftime(f"{date_format},%H:%M:%S")},{duration_min}\n")


def get_df_from_csv(filename: str):
    df = pd.read_csv(filename, names=["Date", "Time", "Minutes"]) # Assumes the columns are in this order with no header
    df["Date"] = pd.to_datetime(df["Date"], format=date_format)
    df = df.pivot_table(values="Minutes", index="Date", aggfunc="sum") 
    return df 
