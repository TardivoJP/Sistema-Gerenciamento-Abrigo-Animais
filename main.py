import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel,
    QHBoxLayout, QVBoxLayout, QListWidget, QStackedWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
from database import create_tables

from animal_module import AnimalListWidget
from adoption_module import AdoptionListWidget
from adopter_module import AdopterListWidget
from volunteer_module import VolunteerListWidget
from donation_module import DonationsListWidget
from analytics_module import AnalyticsWidget
from report_module import ReportWidget



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Gestão da ONG de Abrigo de Animais")
        self.setGeometry(100, 100, 900, 600)
        self.initUI()

    def initUI(self):
        # Layout principal
        main_layout = QHBoxLayout()

        # Barra lateral
        self.sidebar = QListWidget()
        self.sidebar.addItem(QListWidgetItem(QIcon("icons/home_icon.png"), "Home"))
        self.sidebar.addItem(QListWidgetItem(QIcon("icons/animal_icon.png"), "Cadastros"))
        self.sidebar.addItem("  - Animais")
        self.sidebar.addItem("  - Adotantes")
        self.sidebar.addItem("  - Voluntários")
        self.sidebar.addItem(QListWidgetItem(QIcon("icons/adoption_icon.png"), "Processos"))
        self.sidebar.addItem("  - Adoções")
        self.sidebar.addItem("  - Doações")
        self.sidebar.addItem(QListWidgetItem(QIcon("icons/analytics_icon.png"), "Análise e Insights"))
        self.sidebar.addItem(QListWidgetItem(QIcon("icons/report_icon.png"), "Relatório"))
        self.sidebar.currentRowChanged.connect(self.display)
        
        # Ajustando tamanho fixo para a barra lateral
        self.sidebar.setMaximumWidth(250)  # Define a largura máxima (250 pixels)
        self.sidebar.setMinimumWidth(200)  # Define a largura mínima (200 pixels)


        # Aplicando estilo com CSS
        self.sidebar.setStyleSheet(
            """
            QListWidget {
                background: #fefffe;
                border: 1px solid #dfe4eb;
                border-radius: 8px;
            }
            QListWidget::item {
                background: #fefffe;
                border: 1px solid #fefffe;
                padding: 10px;
                color: #000000;
            }
            QListWidget::item:selected {
                background: #eff5fe;
                border: 1px solid #dfe4eb;
                border-radius: 8px;
                color: #000000;
            }
            """
        )

        # Area principal de conteudo
        self.stack = QStackedWidget()
        self.setup_home_widget()

        # Widgets dos modulos
        self.animals_widget = AnimalListWidget()
        self.adoptions_widget = AdoptionListWidget()
        self.adopters_widget = AdopterListWidget()
        self.volunteers_widget = VolunteerListWidget()
        self.donations_widget = DonationsListWidget()
        self.analytics_widget = AnalyticsWidget()
        self.reports_widget = ReportWidget()

        # Widgets em pilha
        self.stack.addWidget(self.home_container)      # Index 0
        self.stack.addWidget(self.animals_widget)      # Index 1
        self.stack.addWidget(self.adopters_widget)     # Index 2
        self.stack.addWidget(self.volunteers_widget)   # Index 3
        self.stack.addWidget(self.adoptions_widget)    # Index 4
        self.stack.addWidget(self.donations_widget)    # Index 5
        self.stack.addWidget(self.analytics_widget)    # Index 6
        self.stack.addWidget(self.reports_widget)      # Index 7

        # Ajustando tamanho dos elementos
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack)

        # Set the main layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def setup_home_widget(self):
        # Texto de boas-vindas
        self.home_widget = QLabel()
        self.home_widget.setText("""
            <h1 style="color: #2b7a78; text-align: center;">Bem-vindo ao Sistema de Gestão da ONG de Abrigo de Animais</h1>
            <p style="font-size: 16px; text-align: center; color: #555555;">
                Utilize o menu lateral para navegar entre as funcionalidades do sistema.
            </p>
        """)
        self.home_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Logotipo
        logo_label = QLabel()
        logo_pixmap = QPixmap("icons/logo amar.png")  # Substitua pelo caminho do arquivo de imagem
        logo_pixmap = logo_pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Informações rápidas
        #info_layout = QVBoxLayout()
        #info_label = QLabel("<b>Total de Adoções Realizadas:</b> ")
        #info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #info_layout.addWidget(info_label)

        # Layout principal da home
        home_layout = QVBoxLayout()
        home_layout.addWidget(logo_label)
        home_layout.addWidget(self.home_widget)
        #home_layout.addLayout(info_layout)

        self.home_container = QWidget()
        self.home_container.setLayout(home_layout)

    def display(self, index):
        if index == 0:
            self.stack.setCurrentWidget(self.home_container)
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
        elif index == 9:
            self.stack.setCurrentWidget(self.reports_widget)
        else:
            pass


if __name__ == '__main__':
    create_tables()  # Garante que o banco de dados esteja configurado
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
