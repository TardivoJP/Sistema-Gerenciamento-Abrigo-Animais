from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QComboBox
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from database import create_connection
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

class AnalyticsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        title = QLabel("Análise e Insights")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # ComboBox para o tipo de análise
        self.analysis_combo = QComboBox()
        self.analysis_combo.addItem("Selecione uma análise")
        self.analysis_combo.addItem("Adoções ao longo do tempo")
        self.analysis_combo.addItem("Animais no Abrigo")
        self.analysis_combo.addItem("Doações ao longo do tempo")
        self.analysis_combo.addItem("Participação de Voluntários")
        self.analysis_combo.currentIndexChanged.connect(self.update_analysis)
        layout.addWidget(self.analysis_combo)

        # Placeholder para o gráfico
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Labels para as estatísticas
        self.stats_label = QLabel("")
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.stats_label)

        self.setLayout(layout)

    def update_analysis(self, index):
        if index == 1:
            self.show_adoptions_over_time()
        elif index == 2:
            self.show_animals_in_shelter()
        elif index == 3:
            self.show_donations_over_time()
        elif index == 4:
            self.show_volunteer_participation()
        else:
            # Limpar a figura e os labels
            self.figure.clear()
            self.canvas.draw()
            self.stats_label.setText("")

    def show_adoptions_over_time(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT date FROM adoptions
        ''')
        dates = cursor.fetchall()
        conn.close()

        date_counts = {}
        for date_tuple in dates:
            date_str = date_tuple[0]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            month_str = date_obj.strftime("%Y-%m")
            date_counts[month_str] = date_counts.get(month_str, 0) + 1

        months = sorted(date_counts.keys())
        counts = [date_counts[month] for month in months]

        ax.bar(months, counts, color='skyblue')
        ax.set_title("Adoções ao longo do tempo")
        ax.set_xlabel("Mês")
        ax.set_ylabel("Número de Adoções")
        ax.tick_params(axis='x', rotation=45)

        self.figure.tight_layout()
        self.canvas.draw()

        total_adoptions = sum(counts)
        self.stats_label.setText(f"Total de Adoções: {total_adoptions}")

    def show_animals_in_shelter(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT type, COUNT(*) FROM animals WHERE status != 'Adotado' GROUP BY type
        ''')
        data = cursor.fetchall()
        conn.close()

        types = [row[0] for row in data]
        counts = [row[1] for row in data]

        ax.pie(counts, labels=types, autopct='%1.1f%%', startangle=90)
        ax.set_title("Animais Disponíveis no Abrigo")

        self.figure.tight_layout()
        self.canvas.draw()

        total_animals = sum(counts)
        self.stats_label.setText(f"Total de Animais no Abrigo: {total_animals}")

    def show_donations_over_time(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT date, amount FROM donations
        ''')
        data = cursor.fetchall()
        conn.close()

        date_sums = {}
        for date_str, amount in data:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            month_str = date_obj.strftime("%Y-%m")
            date_sums[month_str] = date_sums.get(month_str, 0) + amount

        months = sorted(date_sums.keys())
        sums = [date_sums[month] for month in months]

        ax.plot(months, sums, marker='o', linestyle='-', color='green')
        ax.set_title("Doações ao longo do tempo")
        ax.set_xlabel("Mês")
        ax.set_ylabel("Valor das Doações")
        ax.tick_params(axis='x', rotation=45)

        self.figure.tight_layout()
        self.canvas.draw()

        total_donations = sum(sums)
        self.stats_label.setText(f"Total de Doações: R$ {total_donations:.2f}")

    def show_volunteer_participation(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM volunteers
        ''')
        total_volunteers = cursor.fetchone()[0]

        cursor.execute('''
            SELECT volunteer_id, COUNT(*) FROM donations GROUP BY volunteer_id
        ''')
        data = cursor.fetchall()
        conn.close()

        participating_volunteers = len(data)
        non_participating = total_volunteers - participating_volunteers

        labels = ['Ativos', 'Inativos']
        sizes = [participating_volunteers, non_participating]

        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.set_title("Participação de Voluntários em Doações")

        self.figure.tight_layout()
        self.canvas.draw()

        self.stats_label.setText(f"Total de Voluntários: {total_volunteers}")

