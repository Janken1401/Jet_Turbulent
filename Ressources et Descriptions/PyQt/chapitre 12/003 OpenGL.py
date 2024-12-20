from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from PyQt5.QtOpenGL import *

import OpenGL.GL as gl
from OpenGL import GLU
from OpenGL.arrays import vbo

import sys
import numpy as np


class WidgetOpenGL(QOpenGLWidget):
    def __init__(self, parent=None):
        self.parent = parent
        QOpenGLWidget.__init__(self, parent)

    def initializeGL(self):
        print("initializeGL")

        gl.glEnable(gl.GL_DEPTH_TEST)

        self.initialisationGeometrieOpenGL()

        self.rotX = 0.0
        self.rotY = 0.0
        self.rotZ = 0.0

    def resizeGL(self, width, height):

        print("resizeGL")

        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        aspect = width / float(height)

        GLU.gluPerspective(45.0, aspect, 1.0, 100.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def paintGL(self):

        print("paintGL")

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        gl.glPushMatrix()

        gl.glTranslate(0.0, 0.0, -50.0) 
        gl.glScale(20.0, 20.0, 20.0) 
        gl.glRotate(self.rotX, 1.0, 0.0, 0.0)
        gl.glRotate(self.rotY, 0.0, 1.0, 0.0)
        gl.glRotate(self.rotZ, 0.0, 0.0, 1.0)
        gl.glTranslate(-0.5, -0.5, -0.5) 

        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)

        gl.glVertexPointer(3, gl.GL_FLOAT, 0, self.vertVBO)
        gl.glColorPointer(3, gl.GL_FLOAT, 0, self.colorVBO)

        gl.glDrawElements(gl.GL_QUADS, len(self.matriceCubique), gl.GL_UNSIGNED_INT, self.matriceCubique)

        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)

        gl.glPopMatrix()  

    def initialisationGeometrieOpenGL(self):

        print("initialisationGeometrieOpenGL")

        self.cubeVtxArray = np.array(
            [[0.0, 0.0, 0.0],
             [1.0, 0.0, 0.0],
             [1.0, 1.0, 0.0],
             [0.0, 1.0, 0.0],
             [0.0, 0.0, 1.0],
             [1.0, 0.0, 1.0],
             [1.0, 1.0, 1.0],
             [0.0, 1.0, 1.0]])
        self.vertVBO = vbo.VBO(np.reshape(self.cubeVtxArray,
                                          (1, -1)).astype(np.float32))
        self.vertVBO.bind()

        self.cubeClrArray = np.array(
            [[0.0, 0.0, 0.0],
             [1.0, 0.0, 0.0],
             [1.0, 1.0, 0.0],
             [0.0, 1.0, 0.0],
             [0.0, 0.0, 1.0],
             [1.0, 0.0, 1.0],
             [1.0, 1.0, 1.0],
             [0.0, 1.0, 1.0]])
        self.colorVBO = vbo.VBO(np.reshape(self.cubeClrArray,
                                           (1, -1)).astype(np.float32))
        self.colorVBO.bind()

        self.matriceCubique = np.array(
            [0, 1, 2, 3,
             3, 2, 6, 7,
             1, 0, 4, 5,
             2, 1, 5, 6,
             0, 3, 7, 4,
             7, 6, 5, 4])

    def faireRotationAxeX(self, valeur):
        self.rotX = np.pi * valeur

    def faireRotationAxeY(self, valeur):
        self.rotY = np.pi * valeur

    def faireRotationAxeZ(self, valeur):
        self.rotZ = np.pi * valeur


class Fenetre(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)  

        self.resize(350, 350)
        self.setWindowTitle('Chapitre 12 - OpenGL')

        self.widgetOpenGL = WidgetOpenGL(self)
        self.initialiserRendu()

        timer = QTimer(self)
        timer.setInterval(20)
        timer.timeout.connect(self.widgetOpenGL.update)
        timer.start()

    def initialiserRendu(self):
        widgetCentral = QWidget()
        widgetVertical = QVBoxLayout()
        widgetCentral.setLayout(widgetVertical)

        self.setCentralWidget(widgetCentral)

        widgetVertical.addWidget(self.widgetOpenGL)

        sliderX = QSlider(Qt.Horizontal)
        sliderX.valueChanged.connect(lambda val: self.widgetOpenGL.faireRotationAxeX(val))

        sliderY = QSlider(Qt.Horizontal)
        sliderY.valueChanged.connect(lambda val: self.widgetOpenGL.faireRotationAxeY(val))

        sliderZ = QSlider(Qt.Horizontal)
        sliderZ.valueChanged.connect(lambda val: self.widgetOpenGL.faireRotationAxeZ(val))

        widgetVertical.addWidget(sliderX)
        widgetVertical.addWidget(sliderY)
        widgetVertical.addWidget(sliderZ)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    fenetre = Fenetre()
    fenetre.show()

    sys.exit(app.exec_())

