import sys
from PyQt5.QtWidgets import * #QApplication, QWidget

class FenetreSimple(QWidget):
    def __init__(self):
        super().__init__()
        self.execute()

    def execute(self):
        self.resize(250, 300)
        self.move(50, 500)
        self.setWindowTitle("Exemple QLineEdit")

        label = QLabel("Nom : ", self)
        label.move(5, 5)

        line_edit = QLineEdit(self)
        line_edit.move(5, 30)
        line_edit.resize(150, 20)
        line_edit.setText("Valeur par défaut")

        button = QPushButton(self)
        button.move(5, 60)
        button.setText("Cliquez")

        cb = QCheckBox(self)
        cb.setText("Case à cocher")
        cb.setChecked(True)
        cb.move(5, 90)

        rb = QRadioButton(self)
        rb.setText("Bouton radio")
        rb.setChecked(True)
        rb.move(5, 110)

        if cb.isChecked() == True:
            label.setText("La case à cocher est cochée.")
        else:
            label.setText("La case à cocher n'est pas cochée.")

        self.show()

if __name__ == '__main__':
    application = QApplication(sys.argv)
    fenetre = FenetreSimple()
    sys.exit(application.exec_())