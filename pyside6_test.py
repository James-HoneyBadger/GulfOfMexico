# Minimal PySide6 test script to check if Qt works at all
from PySide6.QtWidgets import QApplication, QLabel
import sys

app = QApplication([])
label = QLabel('PySide6 is working!')
label.resize(300, 100)
label.show()
sys.exit(app.exec())
