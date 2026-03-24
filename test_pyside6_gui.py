from PySide6.QtWidgets import QApplication, QLabel
import sys

app = QApplication(sys.argv)
label = QLabel('PySide6 is working!')
label.resize(300, 100)
label.show()
app.exec()