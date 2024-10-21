import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QHBoxLayout, QListWidget, QStackedWidget
)
from PyQt6.QtCore import Qt
from database import create_tables

from animal_module import AnimalListWidget
from adoption_module import AdoptionListWidget
from adopter_module import AdopterListWidget
from volunteer_module import VolunteerListWidget
from donation_module import DonationsListWidget
from analytics_module import AnalyticsWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Gestão da ONG de Abrigo de Animais")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()

    def initUI(self):
        # Layout principal
        main_layout = QHBoxLayout()

        # Barra lateral
        self.sidebar = QListWidget()
        self.sidebar.addItem("Home")
        self.sidebar.addItem("Cadastros")
        self.sidebar.addItem("  - Animais")
        self.sidebar.addItem("  - Adotantes")
        self.sidebar.addItem("  - Voluntários")
        self.sidebar.addItem("Processos")
        self.sidebar.addItem("  - Adoções")
        self.sidebar.addItem("  - Doações")
        self.sidebar.currentRowChanged.connect(self.display)
        self.sidebar.addItem("Análise e Insights")

        # Area principal de conteudo
        self.stack = QStackedWidget()
        self.home_widget = QLabel("Bem-vindo ao Sistema de Gestão da ONG de Abrigo de Animais.")
        self.home_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Widgets dos modulos
        self.animals_widget = AnimalListWidget()
        self.adoptions_widget = AdoptionListWidget()
        self.adopters_widget = AdopterListWidget()
        self.volunteers_widget = VolunteerListWidget()
        self.donations_widget = DonationsListWidget()
        self.analytics_widget = AnalyticsWidget()

        # Widgets em pilha
        self.stack.addWidget(self.home_widget)         # Index 0
        self.stack.addWidget(self.animals_widget)      # Index 1
        self.stack.addWidget(self.adopters_widget)     # Index 2
        self.stack.addWidget(self.volunteers_widget)   # Index 3
        self.stack.addWidget(self.adoptions_widget)    # Index 4
        self.stack.addWidget(self.donations_widget)    # Index 5
        self.stack.addWidget(self.analytics_widget)    # Index 6

        # Ajustando tamanho dos elementos
        main_layout.addWidget(self.sidebar, 1)  # Barra lateral =  1 unidade de espaco
        main_layout.addWidget(self.stack, 4)    # Area principal =  4 unidades de espaco

        # Set the main layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def display(self, index):
        if index == 0:
            self.stack.setCurrentWidget(self.home_widget)
        elif index == 2:
            self.stack.setCurrentWidget(self.animals_widget)
            self.animals_widget.load_data()
        elif index == 3:
            self.stack.setCurrentWidget(self.adopters_widget)
            self.adopters_widget.load_data()
        elif index == 4:
            self.stack.setCurrentWidget(self.volunteers_widget)
            self.volunteers_widget.load_data()
        elif index == 6:
            self.stack.setCurrentWidget(self.adoptions_widget)
            self.adoptions_widget.load_data()
        elif index == 7:
            self.stack.setCurrentWidget(self.donations_widget)
            self.donations_widget.load_data()
        elif index == 8:
            self.stack.setCurrentWidget(self.analytics_widget)
        else:
            pass

if __name__ == '__main__':
    create_tables()  # Garante que o banco de dados esteja configurado
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
