import sys
from PyQt5.QtWidgets import QApplication, QWidget

application = QApplication(sys.argv)

widget = QWidget()

widget.resize(720, 720)
widget.setWindowTitle("Bonjour tout le monde !")
widget.show()

application.exec_()