# home_view.py
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PyQt6.QtCore import pyqtSignal


class HomeView(QWidget):
    go_to_presence_signal = pyqtSignal()


    def __init__(self, profile):
        super().__init__()
        self.setWindowTitle("Menu Principal")


        layout = QVBoxLayout()
        btn = QPushButton("Carte des présences")
        layout.addWidget(btn)
        self.setLayout(layout)


        btn.clicked.connect(self.go_to_presence_signal.emit)