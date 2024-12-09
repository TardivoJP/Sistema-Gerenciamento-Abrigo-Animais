from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from database import create_connection
import matplotlib.pyplot as plt
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

        # ComboBox principal de análise
        self.analysis_combo = QComboBox()
        self.analysis_combo.addItem("Selecione uma análise")
        self.analysis_combo.addItem("Adoções ao longo do tempo")
        self.analysis_combo.addItem("Animais no Abrigo")
        self.analysis_combo.addItem("Doações ao longo do tempo")
        self.analysis_combo.addItem("Participação de Voluntários")
        self.analysis_combo.currentIndexChanged.connect(self.update_analysis)
        layout.addWidget(self.analysis_combo)

        # Linha de filtros adicionais
        filter_layout = QHBoxLayout()
        self.year_combo = QComboBox()
        self.year_combo.addItem("Todos os anos")
        self.year_combo.setVisible(False)
        self.year_combo.currentIndexChanged.connect(self.refresh_current_analysis)
        filter_layout.addWidget(self.year_combo)

        self.extra_filter_combo = QComboBox()
        self.extra_filter_combo.setVisible(False)
        self.extra_filter_combo.currentIndexChanged.connect(self.refresh_current_analysis)
        filter_layout.addWidget(self.extra_filter_combo)

        layout.addLayout(filter_layout)

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
        self.figure.clear()
        self.canvas.draw()
        self.stats_label.setText("")

        self.year_combo.setVisible(False)
        self.extra_filter_combo.setVisible(False)
        self.year_combo.clear()
        self.year_combo.addItem("Todos os anos")

        self.extra_filter_combo.clear()

        if index == 1:
            # Adoções ao longo do tempo
            self.setup_years_for_adoptions()
            self.year_combo.setVisible(True)
            self.refresh_current_analysis()
        elif index == 2:
            # Animais no Abrigo
            # Filtro por tipo: Todos, Cachorro, Gato
            self.extra_filter_combo.addItem("Todos")
            self.extra_filter_combo.addItem("Cachorro")
            self.extra_filter_combo.addItem("Gato")
            self.extra_filter_combo.setVisible(True)
            self.refresh_current_analysis()
        elif index == 3:
            # Doações ao longo do tempo
            self.setup_years_for_donations()
            self.year_combo.setVisible(True)
            self.refresh_current_analysis()
        elif index == 4:
            # Participação de Voluntários
            self.extra_filter_combo.addItem("Participação em Doações")
            self.extra_filter_combo.addItem("Média de Doações por Voluntário")
            self.extra_filter_combo.setVisible(True)
            self.refresh_current_analysis()
        else:
            # Nada selecionado
            pass

    def refresh_current_analysis(self):
        index = self.analysis_combo.currentIndex()
        if index == 1:
            self.show_adoptions_over_time()
        elif index == 2:
            self.show_animals_in_shelter()
        elif index == 3:
            self.show_donations_over_time()
        elif index == 4:
            self.show_volunteer_participation()
        else:
            self.figure.clear()
            self.canvas.draw()
            self.stats_label.setText("")

    def setup_years_for_adoptions(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT strftime('%Y', date) FROM adoptions ORDER BY 1")
        years = cursor.fetchall()
        conn.close()
        for y in years:
            if y[0] is not None:
                self.year_combo.addItem(y[0])

    def setup_years_for_donations(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT strftime('%Y', date) FROM donations ORDER BY 1")
        years = cursor.fetchall()
        conn.close()
        for y in years:
            if y[0] is not None:
                self.year_combo.addItem(y[0])

    def get_selected_year(self):
        if self.year_combo.isVisible():
            year_text = self.year_combo.currentText()
            if year_text != "Todos os anos":
                return year_text
        return None

    def show_adoptions_over_time(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        year = self.get_selected_year()

        conn = create_connection()
        cursor = conn.cursor()
        if year is None:
            cursor.execute('SELECT date FROM adoptions')
        else:
            cursor.execute("SELECT date FROM adoptions WHERE strftime('%Y', date) = ?", (year,))
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

        filter_type = self.extra_filter_combo.currentText() if self.extra_filter_combo.isVisible() else "Todos"

        conn = create_connection()
        cursor = conn.cursor()
        if filter_type == "Todos":
            cursor.execute('''
                SELECT breed, COUNT(*) as c FROM animals
                WHERE status != 'Adotado'
                GROUP BY breed
                ORDER BY c DESC
                LIMIT 5
            ''')
        else:
            cursor.execute('''
                SELECT breed, COUNT(*) as c FROM animals
                WHERE status != 'Adotado' AND type = ?
                GROUP BY breed
                ORDER BY c DESC
                LIMIT 5
            ''', (filter_type,))

        data = cursor.fetchall()
        conn.close()

        if len(data) == 0:
            # Nenhum animal não adotado encontrado de acordo com o filtro
            ax.text(0.5, 0.5, "Nenhuma raça encontrada para esse filtro", ha='center', va='center', fontsize=12)
            counts = []
        else:
            breeds = [row[0] for row in data]
            counts = [row[1] for row in data]

            ax.bar(breeds, counts, color='orange')
            ax.set_title("Top 5 Raças de Animais Não Adotados")
            ax.set_xlabel("Raça")
            ax.set_ylabel("Quantidade")
            ax.tick_params(axis='x', rotation=45)

        self.figure.tight_layout()
        self.canvas.draw()

        total_animals = 0
        # Se quisermos mostrar total de todos animais não adotados com o filtro
        conn = create_connection()
        cursor = conn.cursor()
        if filter_type == "Todos":
            cursor.execute('SELECT COUNT(*) FROM animals WHERE status != "Adotado"')
        else:
            cursor.execute('SELECT COUNT(*) FROM animals WHERE status != "Adotado" AND type = ?', (filter_type,))
        total_animals = cursor.fetchone()[0]
        conn.close()

        self.stats_label.setText(f"Total de Animais no Abrigo (filtro={filter_type}): {total_animals}")

    def show_donations_over_time(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        year = self.get_selected_year()

        conn = create_connection()
        cursor = conn.cursor()
        if year is None:
            cursor.execute('SELECT date, amount FROM donations')
        else:
            cursor.execute('SELECT date, amount FROM donations WHERE strftime("%Y", date) = ?', (year,))
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

        analysis_type = self.extra_filter_combo.currentText() if self.extra_filter_combo.isVisible() else "Participação em Doações"

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM volunteers')
        total_volunteers = cursor.fetchone()[0]

        cursor.execute('SELECT volunteer_id, COUNT(*) FROM donations GROUP BY volunteer_id')
        data = cursor.fetchall()
        conn.close()

        if analysis_type == "Participação em Doações":
            participating_volunteers = len(data)
            non_participating = total_volunteers - participating_volunteers

            labels = ['Ativos', 'Inativos']
            sizes = [participating_volunteers, non_participating]

            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.set_title("Participação de Voluntários em Doações")

            self.stats_label.setText(f"Total de Voluntários: {total_volunteers}")

        else:
            # "Média de Doações por Voluntário"
            if len(data) > 0:
                total_donations = sum([x[1] for x in data])
                avg = total_donations / len(data)
            else:
                avg = 0.0

            ax.bar(["Média/Voluntário"], [avg], color='purple')
            ax.set_title("Média de Doações por Voluntário Ativo")

            self.stats_label.setText(f"Média de Doações por Voluntário Ativo: {avg:.2f}")

        self.figure.tight_layout()
        self.canvas.draw()
