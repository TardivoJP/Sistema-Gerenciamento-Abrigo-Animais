from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QMessageBox,
    QDateEdit, QPushButton
)
from PyQt6.QtCore import Qt, QDate
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from database import create_connection
from datetime import datetime
import matplotlib.dates as mdates

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
        self.analysis_combo.addItem("Novos Adotantes")
        self.analysis_combo.addItem("Novos Voluntários")
        self.analysis_combo.currentIndexChanged.connect(self.update_analysis)
        layout.addWidget(self.analysis_combo)

        # Filtros
        self.filter_layout = QVBoxLayout()

        # Widget para Filtros de Data
        self.date_filter_widget = QWidget()
        self.date_filter_layout = QHBoxLayout(self.date_filter_widget)

        self.date_filter_layout.addWidget(QLabel("Data Início:"))
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_filter_layout.addWidget(self.start_date_edit)

        self.date_filter_layout.addWidget(QLabel("Data Fim:"))
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_filter_layout.addWidget(self.end_date_edit)

        self.apply_date_filter_button = QPushButton("Aplicar Filtro")
        self.apply_date_filter_button.clicked.connect(self.refresh_current_analysis)
        self.date_filter_layout.addWidget(self.apply_date_filter_button)

        self.filter_layout.addWidget(self.date_filter_widget)
        self.date_filter_widget.setVisible(False)  # Inicialmente oculto

        # Widget para Filtros Extras (Tipo de Animal)
        self.extra_filter_widget = QWidget()
        self.extra_filter_layout = QHBoxLayout(self.extra_filter_widget)
        self.extra_filter_layout.addWidget(QLabel("Tipo de Animal:"))
        self.extra_filter_combo = QComboBox()
        self.extra_filter_combo.addItem("Todos")
        self.extra_filter_combo.addItem("Cachorro")
        self.extra_filter_combo.addItem("Gato")
        self.extra_filter_combo.currentIndexChanged.connect(self.refresh_current_analysis)
        self.extra_filter_layout.addWidget(self.extra_filter_combo)
        self.filter_layout.addWidget(self.extra_filter_widget)
        self.extra_filter_widget.setVisible(False)  # Inicialmente oculto

        # Widget para Filtros de Status (Adotado/Não Adotado)
        self.status_filter_widget = QWidget()
        self.status_filter_layout = QHBoxLayout(self.status_filter_widget)
        self.status_filter_layout.addWidget(QLabel("Status:"))
        self.status_filter_combo = QComboBox()
        self.status_filter_combo.addItem("Todos")
        self.status_filter_combo.addItem("Adotado")
        self.status_filter_combo.addItem("Não Adotado")
        self.status_filter_combo.currentIndexChanged.connect(self.refresh_current_analysis)
        self.status_filter_layout.addWidget(self.status_filter_combo)
        self.filter_layout.addWidget(self.status_filter_widget)
        self.status_filter_widget.setVisible(False)  # Inicialmente oculto

        layout.addLayout(self.filter_layout)

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

        # Resetar visibilidade dos filtros
        self.date_filter_widget.setVisible(False)
        self.extra_filter_widget.setVisible(False)
        self.status_filter_widget.setVisible(False)

        # Resetar seleção do filtro extra e status
        self.extra_filter_combo.setCurrentIndex(0)
        self.status_filter_combo.setCurrentIndex(0)

        if index == 1:
            # Adoções ao longo do tempo
            self.date_filter_widget.setVisible(True)
            self.setup_date_filters()
            self.refresh_current_analysis()
        elif index == 2:
            # Animais no Abrigo
            self.date_filter_widget.setVisible(True)
            self.extra_filter_widget.setVisible(True)
            self.status_filter_widget.setVisible(True)
            self.setup_date_filters()
            self.refresh_current_analysis()
        elif index == 3:
            # Doações ao longo do tempo
            self.date_filter_widget.setVisible(True)
            self.setup_date_filters()
            self.refresh_current_analysis()
        elif index == 4:
            # Novos Adotantes
            self.date_filter_widget.setVisible(True)
            self.setup_date_filters()
            self.refresh_current_analysis()
        elif index == 5:
            # Novos Voluntários
            self.date_filter_widget.setVisible(True)
            self.setup_date_filters()
            self.refresh_current_analysis()
        else:
            # Nada selecionado
            self.date_filter_widget.setVisible(False)
            self.extra_filter_widget.setVisible(False)
            self.status_filter_widget.setVisible(False)

    def setup_date_filters(self):
        # Definir datas padrão
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-6))
        self.end_date_edit.setDate(QDate.currentDate())
        # Exibir os campos de data
        self.date_filter_widget.setVisible(True)

    def get_date_range(self):
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd") if self.date_filter_widget.isVisible() else None
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd") if self.date_filter_widget.isVisible() else None
        return start_date, end_date

    def refresh_current_analysis(self):
        index = self.analysis_combo.currentIndex()
        if index == 1:
            self.show_adoptions_over_time()
        elif index == 2:
            self.show_animals_in_shelter()
        elif index == 3:
            self.show_donations_over_time()
        elif index == 4:
            self.show_new_adopters()
        elif index == 5:
            self.show_new_volunteers()
        else:
            self.figure.clear()
            self.canvas.draw()
            self.stats_label.setText("")

    def show_adoptions_over_time(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        start_date, end_date = self.get_date_range()

        conn = create_connection()
        cursor = conn.cursor()
        query = 'SELECT date FROM adoptions'
        params = []
        if start_date and end_date:
            query += ' WHERE date BETWEEN ? AND ?'
            params = [start_date, end_date]
        print(f"Executing Query for Adoptions: {query} with params {params}")  # Debug
        cursor.execute(query, params)
        dates = cursor.fetchall()
        conn.close()

        print(f"Number of Adoptions Fetched: {len(dates)}")  # Debug

        if not dates:
            ax.text(0.5, 0.5, "Nenhuma adoção encontrada no período selecionado", ha='center', va='center', fontsize=12)
            self.canvas.draw()
            self.stats_label.setText("Total de Adoções: 0")
            return

        date_counts = {}
        for date_tuple in dates:
            date_str = date_tuple[0]
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                # Tentar outro formato se necessário
                print(f"Invalid date format for Adoptions: {date_str}")  # Debug
                continue
            # Usar o primeiro dia do mês para representar o mês
            month_dt = datetime(date_obj.year, date_obj.month, 1)
            date_counts[month_dt] = date_counts.get(month_dt, 0) + 1

        months = sorted(date_counts.keys())
        counts = [date_counts[month] for month in months]

        # Converter datas para números para o matplotlib
        months_num = mdates.date2num(months)

        ax.bar(months_num, counts, width=20, color='skyblue')  # width=20 dias para cada barra
        ax.set_title("Adoções ao longo do tempo")
        ax.set_xlabel("Mês")
        ax.set_ylabel("Número de Adoções")
        ax.tick_params(axis='x', rotation=45)

        # Melhorar o formato do eixo X para datas
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))

        self.figure.tight_layout()
        self.canvas.draw()

        total_adoptions = sum(counts)
        self.stats_label.setText(f"Total de Adoções: {total_adoptions}")

    def show_animals_in_shelter(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        filter_type = self.extra_filter_combo.currentText() if self.extra_filter_widget.isVisible() else "Todos"
        status_filter = self.status_filter_combo.currentText() if self.status_filter_widget.isVisible() else "Não Adotado"
        start_date, end_date = self.get_date_range()

        conn = create_connection()
        cursor = conn.cursor()
        params = []
        query = '''
            SELECT type, COUNT(*) as c FROM animals
            WHERE 1=1
        '''

        # Aplicar filtro de status
        if status_filter != "Todos":
            query += ' AND status = ?'
            params.append(status_filter)
        else:
            # Se "Todos", incluir ambos adotados e não adotados
            pass  # Nenhum filtro aplicado

        # Aplicar filtro de tipo de animal
        if filter_type != "Todos":
            query += ' AND type = ?'
            params.append(filter_type)

        # Aplicar filtro de data usando DATE(created_at)
        if start_date and end_date:
            query += ' AND DATE(created_at) BETWEEN ? AND ?'
            params.extend([start_date, end_date])

        query += '''
            GROUP BY type
            ORDER BY c DESC
        '''
        print(f"Executing Query for Animals in Shelter: {query} with params {params}")  # Debug
        cursor.execute(query, params)
        data = cursor.fetchall()

        print(f"Number of Animals Fetched: {len(data)}")  # Debug

        if len(data) == 0:
            ax.text(0.5, 0.5, "Nenhum animal encontrado para esse filtro", ha='center', va='center', fontsize=12)
            counts = []
        else:
            types = [row[0] for row in data]
            counts = [row[1] for row in data]

            ax.bar(types, counts, color='orange')
            ax.set_title("Quantidade de Animais no Abrigo")
            ax.set_xlabel("Tipo de Animal")
            ax.set_ylabel("Quantidade")
            ax.tick_params(axis='x', rotation=45)

        self.figure.tight_layout()
        self.canvas.draw()

        # Total de animais com o filtro aplicado
        query_total = 'SELECT COUNT(*) FROM animals WHERE 1=1'
        params_total = []

        if status_filter != "Todos":
            query_total += ' AND status = ?'
            params_total.append(status_filter)

        if filter_type != "Todos":
            query_total += ' AND type = ?'
            params_total.append(filter_type)

        if start_date and end_date:
            query_total += ' AND DATE(created_at) BETWEEN ? AND ?'
            params_total.extend([start_date, end_date])

        print(f"Executing Query for Total Animals: {query_total} with params {params_total}")  # Debug
        cursor.execute(query_total, params_total)
        total_animals = cursor.fetchone()[0]
        conn.close()

        print(f"Total Animals in Shelter: {total_animals}")  # Debug

        self.stats_label.setText(f"Total de Animais no Abrigo ({status_filter}): {total_animals}")

    def show_donations_over_time(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        start_date, end_date = self.get_date_range()

        conn = create_connection()
        cursor = conn.cursor()
        query = 'SELECT date, amount FROM donations'
        params = []
        if start_date and end_date:
            query += ' WHERE DATE(date) BETWEEN ? AND ?'
            params = [start_date, end_date]
        print(f"Executing Query for Donations: {query} with params {params}")  # Debug
        cursor.execute(query, params)
        data = cursor.fetchall()
        conn.close()

        print(f"Number of Donations Fetched: {len(data)}")  # Debug

        if not data:
            ax.text(0.5, 0.5, "Nenhuma doação encontrada no período selecionado", ha='center', va='center', fontsize=12)
            self.canvas.draw()
            self.stats_label.setText("Total de Doações: R$ 0.00")
            return

        date_sums = {}
        for date_str, amount in data:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                # Tentar outro formato se necessário
                print(f"Invalid date format for Donations: {date_str}")  # Debug
                continue
            # Usar o primeiro dia do mês para representar o mês
            month_dt = datetime(date_obj.year, date_obj.month, 1)
            date_sums[month_dt] = date_sums.get(month_dt, 0) + amount

        months = sorted(date_sums.keys())
        sums = [date_sums[month] for month in months]

        # Converter datas para números para o matplotlib
        months_num = mdates.date2num(months)

        ax.plot(months_num, sums, marker='o', linestyle='-', color='green')
        ax.set_title("Doações ao longo do tempo")
        ax.set_xlabel("Mês")
        ax.set_ylabel("Valor das Doações (R$)")
        ax.tick_params(axis='x', rotation=45)

        # Melhorar o formato do eixo X para datas
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))

        self.figure.tight_layout()
        self.canvas.draw()

        total_donations = sum(sums)
        self.stats_label.setText(f"Total de Doações: R$ {total_donations:.2f}")

    def show_new_adopters(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        start_date, end_date = self.get_date_range()

        conn = create_connection()
        cursor = conn.cursor()
        
        # Query para novos adotantes usando a tabela 'adopters'
        query_adopters = '''
            SELECT created_at FROM adopters
        '''
        params_adopters = []
        if start_date and end_date:
            query_adopters += ' WHERE DATE(created_at) BETWEEN ? AND ?'
            params_adopters = [start_date, end_date]
        print(f"Executing Query for New Adopters: {query_adopters} with params {params_adopters}")  # Debug
        cursor.execute(query_adopters, params_adopters)
        adopters_dates = cursor.fetchall()
        conn.close()

        print(f"Number of New Adopters Fetched: {len(adopters_dates)}")  # Debug

        # Prepare data para plotagem
        date_counts_adopters = {}
        for date_tuple in adopters_dates:
            date_str = date_tuple[0]
            if not date_str:
                continue
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    print(f"Invalid date format for Adopters: {date_str}")  # Debug
                    continue  # Ignorar datas mal formatadas
            # Usar o primeiro dia do mês para representar o mês
            month_dt = datetime(date_obj.year, date_obj.month, 1)
            date_counts_adopters[month_dt] = date_counts_adopters.get(month_dt, 0) + 1

        months = sorted(date_counts_adopters.keys())
        adopters_counts = [date_counts_adopters[month] for month in months]

        print(f"Months with New Adopters: {months}")  # Debug
        print(f"Counts of New Adopters per Month: {adopters_counts}")  # Debug

        if not months:
            ax.text(0.5, 0.5, "Nenhum novo adotante encontrado no período selecionado", ha='center', va='center', fontsize=12)
            self.canvas.draw()
            self.stats_label.setText("Total de Novos Adotantes: 0")
            return

        # Converter datas para números para o matplotlib
        months_num = mdates.date2num(months)

        ax.bar(months_num, adopters_counts, width=20, color='blue')  # width=20 dias para cada barra
        ax.set_title("Novos Adotantes ao longo do tempo")
        ax.set_xlabel("Mês")
        ax.set_ylabel("Número de Adotantes")
        ax.tick_params(axis='x', rotation=45)

        # Melhorar o formato do eixo X para datas
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))

        self.figure.tight_layout()
        self.canvas.draw()

        total_adopters = sum(adopters_counts)
        self.stats_label.setText(f"Total de Novos Adotantes: {total_adopters}")

    def show_new_volunteers(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        start_date, end_date = self.get_date_range()

        conn = create_connection()
        cursor = conn.cursor()
        
        # Query para novos voluntários usando a tabela 'volunteers'
        query_volunteers = '''
            SELECT created_at FROM volunteers
        '''
        params_volunteers = []
        if start_date and end_date:
            query_volunteers += ' WHERE DATE(created_at) BETWEEN ? AND ?'
            params_volunteers = [start_date, end_date]
        print(f"Executing Query for New Volunteers: {query_volunteers} with params {params_volunteers}")  # Debug
        cursor.execute(query_volunteers, params_volunteers)
        volunteers_dates = cursor.fetchall()
        conn.close()

        print(f"Number of New Volunteers Fetched: {len(volunteers_dates)}")  # Debug

        # Prepare data para plotagem
        date_counts_volunteers = {}
        for date_tuple in volunteers_dates:
            date_str = date_tuple[0]
            if not date_str:
                continue
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    print(f"Invalid date format for Volunteers: {date_str}")  # Debug
                    continue  # Ignorar datas mal formatadas
            # Usar o primeiro dia do mês para representar o mês
            month_dt = datetime(date_obj.year, date_obj.month, 1)
            date_counts_volunteers[month_dt] = date_counts_volunteers.get(month_dt, 0) + 1

        months = sorted(date_counts_volunteers.keys())
        volunteers_counts = [date_counts_volunteers[month] for month in months]

        print(f"Months with New Volunteers: {months}")  # Debug
        print(f"Counts of New Volunteers per Month: {volunteers_counts}")  # Debug

        if not months:
            ax.text(0.5, 0.5, "Nenhum novo voluntário encontrado no período selecionado", ha='center', va='center', fontsize=12)
            self.canvas.draw()
            self.stats_label.setText("Total de Novos Voluntários: 0")
            return

        # Converter datas para números para o matplotlib
        months_num = mdates.date2num(months)

        ax.bar(months_num, volunteers_counts, width=20, color='green')  # width=20 dias para cada barra
        ax.set_title("Novos Voluntários ao longo do tempo")
        ax.set_xlabel("Mês")
        ax.set_ylabel("Número de Voluntários")
        ax.tick_params(axis='x', rotation=45)

        # Melhorar o formato do eixo X para datas
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))

        self.figure.tight_layout()
        self.canvas.draw()

        total_volunteers = sum(volunteers_counts)
        self.stats_label.setText(f"Total de Novos Voluntários: {total_volunteers}")
