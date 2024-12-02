#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 20:58:45 2024

@author: ahmed
"""
import sys

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QComboBox, QLabel, QLineEdit, QMessageBox)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from src.Field.rans_field import RansField
from src.Field.perturbation_field import PerturbationField

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Analyse de Stabilité d'un Jet Turbulent")
        self.setGeometry(100, 100, 1200, 800)
        
        
        main_layout = QVBoxLayout()
        
        # Paramètres de Mach et Strouhal
        self.param_layout = self.create_param_layout()
        main_layout.addLayout(self.param_layout)
        
        
        self.setup_rans_section(main_layout)
        self.setup_pse_section(main_layout)
        self.setup_qtot_section(main_layout)

        # Widget central
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def create_param_layout(self):
        
        param_layout = QHBoxLayout()
        
        
        mach_label = QLabel("Nombre de cas Mach:")
        param_layout.addWidget(mach_label)

        self.mach_cases = {
            1: "0.97335", 2: "0.97479", 3: "0.98081", 4: "0.9835", 5: "0.98544", 
            6: "0.98691", 7: "0.98794", 8: "0.98856", 9: "0.98877", 10: "0.98554"
        }
        
        self.mach_box = QComboBox()
        self.mach_box.addItems([str(k) for k in self.mach_cases.keys()])
        param_layout.addWidget(self.mach_box)
        
       
        strouhal_label = QLabel("Strouhal:")
        param_layout.addWidget(strouhal_label)
        self.strouhal_box = QComboBox()
        self.strouhal_box.addItems(["0.4", "1.0"])
        param_layout.addWidget(self.strouhal_box)
        
        return param_layout

    def setup_rans_section(self, main_layout):
        
        rans_layout = QVBoxLayout()
        rans_label = QLabel("Options RANS:")
        rans_layout.addWidget(rans_label)
        
       
        component_label = QLabel("Composante:")
        self.rans_component_box = QComboBox()
        self.rans_component_box.addItems(["ux", "ur", "ut", "rho", "T", "p"])
        rans_layout.addWidget(component_label)
        rans_layout.addWidget(self.rans_component_box)
        
        
        xi_label = QLabel("Entrez la valeur de xi pour le profil :")
        self.rans_xi_input = QLineEdit()
        self.rans_xi_input.setPlaceholderText("Entrez un entier positif")
        rans_layout.addWidget(xi_label)
        rans_layout.addWidget(self.rans_xi_input)
        rans_layout.addWidget(xi_label)
        rans_layout.addWidget(self.rans_xi_input)
        
        
        self.rans_canvas = FigureCanvas(Figure(figsize=(5, 4)))
        rans_layout.addWidget(self.rans_canvas)
        
        # Bouton pour afficher les graphiques RANS
        self.rans_run_button = QPushButton("Afficher les résultats RANS")
        self.rans_run_button.clicked.connect(self.run_rans_analysis)
        rans_layout.addWidget(self.rans_run_button)
        
        main_layout.addLayout(rans_layout) 

    def setup_pse_section(self, main_layout):
        
        pse_layout = QVBoxLayout()
        pse_label = QLabel("Options PSE:")
        pse_layout.addWidget(pse_label)

        
        ref_label = QLabel("Valeurs de référence (indice k):")
        self.pse_ref_box = QComboBox()
        self.pse_ref_box.addItems(["1", "2", "3", "4", "5", "6", "7", "8", "9", 
                                   "10"])
        pse_layout.addWidget(ref_label)
        pse_layout.addWidget(self.pse_ref_box)
        
        component_label = QLabel("Composantes des perturbations (x - r):")
        self.pse_component_box = QComboBox()
        self.pse_component_box.addItems(["Re(ux)", "Im(ux)", "abs(ux)", 
                                         "Re(ur)", "Im(ur)", "abs(ur)", 
                                         "Re(rho)", "Im(rho)", "abs(rho)"])
        pse_layout.addWidget(component_label)
        pse_layout.addWidget(self.pse_component_box)
        
        
        xi_label = QLabel("Entrez la valeur de xi pour le profil :")
        self.pse_xi_input = QLineEdit()
        self.pse_xi_input.setPlaceholderText("Entrez un entier entre 0 et 200")
        pse_layout.addWidget(xi_label)
        pse_layout.addWidget(self.pse_xi_input)
  
       
        alpha_label = QLabel("Valeurs de α en fonction de x:")
        self.pse_alpha_box = QComboBox()
        self.pse_alpha_box.addItems(["Re(alpha)", "Im(alpha)", "abs(alpha)", 
                                "Re(int(alpha))", "Im(int(alpha))", "C<sub>ph</sub>", "sigma", "N"])
        pse_layout.addWidget(alpha_label)
        pse_layout.addWidget(self.pse_alpha_box)
        
    
        xmin_label = QLabel("Valeur de xmin:")
        self.xmin_input = QLineEdit()
        self.xmin_input.setPlaceholderText("Entrez une valeur pour xmin ")
        pse_layout.addWidget(xmin_label)
        pse_layout.addWidget(self.xmin_input)

        xmax_label = QLabel("Valeur de xmax :")
        self.xmax_input = QLineEdit()
        self.xmax_input.setPlaceholderText("Entrez une valeur pour xmax ")
        pse_layout.addWidget(xmax_label)
        pse_layout.addWidget(self.xmax_input)

        rmin_label = QLabel("Valeur de rmin:")
        self.rmin_input = QLineEdit()
        self.rmin_input.setPlaceholderText("Entrez une valeur pour rmin ")
        pse_layout.addWidget(rmin_label)
        pse_layout.addWidget(self.rmin_input)

        rmax_label = QLabel("Valeur de rmax :")
        self.rmax_input = QLineEdit()
        self.rmax_input.setPlaceholderText("Entrez une valeur pour rmax ")
        pse_layout.addWidget(rmax_label)
        pse_layout.addWidget(self.rmax_input)
      
        self.pse_run_button = QPushButton("Afficher les résultats PSE")
        self.pse_run_button.clicked.connect(self.run_pse_analysis)
        pse_layout.addWidget(self.pse_run_button)
        
        self.pse_canvas = FigureCanvas(Figure(figsize=(5, 4)))
        pse_layout.addWidget(self.pse_canvas)
     

        main_layout.addLayout(pse_layout)

    def setup_qtot_section(self, main_layout):
        
        qtot_layout = QVBoxLayout()
        qtot_label = QLabel("Options Champ Total (qtot):")
        qtot_layout.addWidget(qtot_label)
        
        
        epsilon_label = QLabel("Sélectionnez la valeur de εq:")
        self.epsilon_q_box = QComboBox()
        self.epsilon_q_box.addItems(["0.01", "0.1"])  # Options pour εq
        qtot_layout.addWidget(epsilon_label)
        qtot_layout.addWidget(self.epsilon_q_box)
        
       
        component_label = QLabel("Composante pour le champ total (qtot):")
        self.qtot_component_box = QComboBox()
        self.qtot_component_box.addItems(["ux", "ur", "ut", "rho", "T", "p"])
        qtot_layout.addWidget(component_label)
        qtot_layout.addWidget(self.qtot_component_box)

       
        xi_label = QLabel("Entrez la valeur de xi pour le profil :")
        self.qtot_xi_input = QLineEdit()
        self.qtot_xi_input.setPlaceholderText("Entrez un entier entre 0 et 200")
        qtot_layout.addWidget(xi_label)
        qtot_layout.addWidget(self.qtot_xi_input)
        
       
        self.qtot_canvas = FigureCanvas(Figure(figsize=(5, 4)))
        qtot_layout.addWidget(self.qtot_canvas)
        
        
        self.qtot_run_button = QPushButton("Afficher les résultats Champ Total (qtot)")
        self.qtot_run_button.clicked.connect(self.run_qtot_analysis)
        qtot_layout.addWidget(self.qtot_run_button)
        
        main_layout.addLayout(qtot_layout)


    def run_rans_analysis(self):
        print("Bouton cliqué - Début de run_rans_analysis")
      
        selected_case = int(self.mach_box.currentText())  
        mach_value = float(self.mach_cases[selected_case])  
        print(f"Cas sélectionné : {selected_case}, Mach : {mach_value}")
        
        component = self.rans_component_box.currentText() 
        try:
            xi_value = int(self.rans_xi_input.text())  
            print(f"Composante : {component}, xi : {xi_value}")
            if not (0 <= xi_value <= 535):  
                raise ValueError("La valeur de xi doit être entre 0 et 535.")
        except ValueError as e:
            QMessageBox.warning(self, "Erreur", str(e))
            return

        print("Chargement des données avec PerturbationField")
        pert_field = PerturbationField(St=0.4, ID_MACH=selected_case)  
        x_grid = pert_field.x_grid 
        rans_values = pert_field.rans_values.get(component)  
        
        if rans_values is None:
            QMessageBox.warning(self, "Erreur", f"La composante {component} n'est pas disponible dans les données RANS.")
            return
        
        rans_profile = rans_values.iloc[:, xi_value]  
 
        print("Aperçu des données de rans_profile:", rans_profile.head())
        
        print(f"Taille de x_grid : {len(x_grid)}, Taille de rans_profile : {len(rans_profile)}")
        if len(x_grid) != len(rans_profile):
            QMessageBox.warning(self, "Erreur", "Les tailles de x_grid et rans_profile ne correspondent pas.")
            return

        self.rans_canvas.figure.clf() 
        ax = self.rans_canvas.figure.add_subplot(111)
        
        ax.plot(x_grid, rans_profile, label=f"{component} pour xi={xi_value}")
        ax.set_xlabel("x")
        ax.set_ylabel(component)
        ax.legend()
        self.rans_canvas.draw_idle()
        self.rans_canvas.flush_events()
        print("Affichage terminé pour RANS.")
        
   
    def run_pse_analysis(self):
        pass


    def run_qtot_analysis(self):
        
        print("Bouton cliqué - Début de run_qtot_analysis")
       
        selected_case = int(self.mach_box.currentText())
        mach_value = float(self.mach_cases[selected_case])
        print(f"Cas sélectionné : {selected_case}, Mach : {mach_value}")
       
        epsilon_q = float(self.epsilon_q_box.currentText())
        component = self.qtot_component_box.currentText()
        print(f"Valeur de epsilon_q : {epsilon_q}, Composante : {component}")
                
        try:
            xi_value = int(self.qtot_xi_input.text())
            print(f"xi sélectionné pour qtot : {xi_value}")
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une valeur valide pour xi.")
            return
        
        rans_field = RansField(ID_MACH=selected_case)
        x_grid = np.linspace(0, 20, 536)
        rans_field.interpolate(x_grid)
        
        pert_field = PerturbationField(St=0.4, ID_MACH=selected_case)
        pert_values = pert_field.values.get(f"Re({component})", None)
        if pert_values is None:
            QMessageBox.warning(self, "Erreur", f"Composante de perturbation {component} non disponible.")
            return
               
        rans_values = rans_field.interpolated_values[component]
        qtot_values = rans_values + epsilon_q * pert_values
       
        max_xi = qtot_values.shape[1] - 1
        if xi_value > max_xi:
            QMessageBox.warning(self, "Erreur", f"L'indice xi={xi_value} dépasse la limite maximale ({max_xi}).")
            return
        
        qtot_profile = qtot_values.iloc[:, xi_value]
        
        print("Aperçu des données de qtot_profile:", qtot_profile.head())
       
        self.qtot_canvas.figure.clf()
        ax = self.qtot_canvas.figure.add_subplot(111)
        ax.plot(x_grid, qtot_profile, label=f"{component} pour xi={xi_value} et εq={epsilon_q}")
        ax.set_xlabel("x")
        ax.set_ylabel(component)
        ax.legend()
        ax.set_title(f"Champ Total qtot de {component} avec εq={epsilon_q}")
        self.qtot_canvas.draw_idle()
        self.qtot_canvas.flush_events()
        print("Affichage terminé pour Champ Total qtot.")

if __name__ == "__main__":

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
