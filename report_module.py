from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QDateEdit, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QDate
from database import create_connection
from datetime import datetime, timedelta
import os

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

class ReportWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.set_styles()

    def set_styles(self):
        style = (
            "QWidget {"
            "    background-color: #f4f6fb;"
            "}"
            "QPushButton {"
            "    border: 1px solid #f4f6fb;"
            "    border-radius: 15px;"
            "    background-color: #fffefe;"
            "    color: black;"
            "    padding: 5px 10px;"
            "    font-size: 14px;"
            "}"
            "QPushButton:hover {"
            "    background-color: #eaeaea;"
            "}"
            "QPushButton:disabled {"
            "    background-color: #d3d3d3;"
            "    color: #a9a9a9;"
            "}"
            "QTableWidget {"
            "    gridline-color: transparent;"
            "    background-color: #fffefe;"  # Cor de fundo da tabela
            "    border: 2px solid #eef1f6;"
            "    border-bottom-left-radius: 10px;"  # Arredondando a borda inferior esquerda
            "    border-bottom-right-radius: 10px;"  # Arredondando a borda inferior direita
            "    border-top-left-radius: 10px;"  # Sem arredondamento no topo esquerdo
            "    border-top-right-radius: 10px;"  # Sem arredondamento no topo direito
            "}"
            "QHeaderView::section {"
            "    background-color: #f4f6fb;"  # Cor de fundo
            "    color: #9ba3b2;"  # Cor do texto
            "    border: none;"
            "    padding: 8px;"  # Espaçamento interno para evitar cortes
            "    text-align: left;"
            "}"
            "QHeaderView::up-arrow, QHeaderView::down-arrow {"
            "    width: 12px;"  # Largura do ícone
            "    height: 12px;"  # Altura do ícone
            "    margin-left: 5px;"  # Espaçamento entre texto e ícone
            "    padding: 2px;"  # Evita cortes
            "}"
            "QComboBox, QLineEdit {"
            "    background-color: #fffefe;"  # Cor de fundo dos campos de pesquisa
            "    border: 1px solid #eef1f6;"  # Borda para os campos
            "    border-radius: 5px;"  # Bordas arredondadas
            "    padding: 5px;"  # Espaçamento interno
            "    font-size: 14px;"  # Tamanho da fonte
            "}"
            "QComboBox:hover, QLineEdit:hover {"
            "    background-color: #d3d3d3;"  # Cor de fundo ao passar o mouse
            "}"
                    # Customizando a barra de rolagem
        "QScrollBar:horizontal {"
        "    border: none;"  # Remove a borda
        "    background: #f0f0f0;"  # Cor de fundo da barra horizontal
        "    height: 8px;"  # Altura da barra de rolagem horizontal
        "    margin: 0px 21px 0 21px;"  # Distância do conteúdo
        "}"
        "QScrollBar:vertical {"
        "    border: none;"  # Remove a borda
        "    background: #f0f0f0;"  # Cor de fundo da barra vertical
        "    width: 8px;"  # Largura da barra de rolagem vertical
        "    margin: 21px 0 21px 0;"  # Distância do conteúdo
        "}"
        "QScrollBar::handle:horizontal, QScrollBar::handle:vertical {"
        "    background: #c0c0c0;"  # Cor do 'thumb' (parte que se arrasta)
        "    border-radius: 4px;"  # Bordas arredondadas
        "}"
        "QScrollBar::handle:horizontal:hover, QScrollBar::handle:vertical:hover {"
        "    background: #a0a0a0;"  # Cor do 'thumb' ao passar o mouse
        "}"
        "QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal, "
        "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {"
        "    background: none;"  # Remove os botões de seta da barra de rolagem
        "}"
        "QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical, "
        "QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {"
        "    background: none;"  # Remove os botões de seta
        "}"
        )



        self.setStyleSheet(style)
    def initUI(self):
        layout = QVBoxLayout()

        # Título
        title = QLabel("Relatório")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # Barra de Botões Rápidos para Relatórios Temporais
        quick_report_layout = QHBoxLayout()
        self.weekly_button = QPushButton("Semanal")
        self.weekly_button.clicked.connect(lambda: self.set_date_range('weekly'))
        quick_report_layout.addWidget(self.weekly_button)

        self.biweekly_button = QPushButton("Quinzenal")
        self.biweekly_button.clicked.connect(lambda: self.set_date_range('biweekly'))
        quick_report_layout.addWidget(self.biweekly_button)

        self.monthly_button = QPushButton("Mensal")
        self.monthly_button.clicked.connect(lambda: self.set_date_range('monthly'))
        quick_report_layout.addWidget(self.monthly_button)

        self.bimonthly_button = QPushButton("Bimestral")
        self.bimonthly_button.clicked.connect(lambda: self.set_date_range('bimonthly'))
        quick_report_layout.addWidget(self.bimonthly_button)

        self.semiannual_button = QPushButton("Semestral")
        self.semiannual_button.clicked.connect(lambda: self.set_date_range('semiannual'))
        quick_report_layout.addWidget(self.semiannual_button)

        self.annual_button = QPushButton("Anual")
        self.annual_button.clicked.connect(lambda: self.set_date_range('annual'))
        quick_report_layout.addWidget(self.annual_button)

        layout.addLayout(quick_report_layout)

        # Seleção de Data Inicial e Data Final
        date_layout = QHBoxLayout()
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        date_layout.addWidget(QLabel("Data Inicial:"))
        date_layout.addWidget(self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        date_layout.addWidget(QLabel("Data Final:"))
        date_layout.addWidget(self.end_date)

        layout.addLayout(date_layout)

        # Botão para gerar relatório
        self.generate_button = QPushButton("Gerar Relatório")
        self.generate_button.clicked.connect(self.generate_report)
        layout.addWidget(self.generate_button)

        # Área de texto para exibir o sumário
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        layout.addWidget(self.report_text)

        # Botão para exportar PDF
        self.export_button = QPushButton("Exportar PDF")
        self.export_button.clicked.connect(self.export_pdf)
        self.export_button.setEnabled(False)  # Só habilitar após gerar o relatório
        layout.addWidget(self.export_button)

        self.setLayout(layout)

    def set_date_range(self, period):
        end_date = QDate.currentDate()
        if period == 'weekly':
            start_date = end_date.addDays(-7)
        elif period == 'biweekly':
            start_date = end_date.addDays(-14)
        elif period == 'monthly':
            start_date = end_date.addMonths(-1)
        elif period == 'bimonthly':
            start_date = end_date.addMonths(-2)
        elif period == 'semiannual':
            start_date = end_date.addMonths(-6)
        elif period == 'annual':
            start_date = end_date.addYears(-1)
        else:
            start_date = end_date

        self.start_date.setDate(start_date)
        self.end_date.setDate(end_date)
        self.generate_report()

    def generate_report(self):
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")

        # Converter para datetime de fato, se necessário
        start_dt = datetime.strptime(start, "%Y-%m-%d")
        end_dt = datetime.strptime(end, "%Y-%m-%d")

        if end_dt < start_dt:
            QMessageBox.warning(self, "Erro", "A data final deve ser maior ou igual à data inicial.")
            return

        # Consultas ao banco
        conn = create_connection()
        cursor = conn.cursor()

        # 1. Total de Animais Disponíveis no Final do Período
        cursor.execute('''
            SELECT COUNT(*) FROM animals
            WHERE DATE(created_at) <= DATE(?)
              AND status != 'Adotado'
        ''', (end,))
        total_animais_disponiveis = cursor.fetchone()[0]

        # 2. Total de Animais Adicionados no Período
        cursor.execute('''
            SELECT COUNT(*) FROM animals
            WHERE DATE(created_at) BETWEEN DATE(?) AND DATE(?)
        ''', (start, end))
        total_animais_adicionados = cursor.fetchone()[0]

        # 3. Adoções Realizadas no Período
        cursor.execute('''
            SELECT COUNT(*) FROM adoptions
            WHERE DATE(date) BETWEEN DATE(?) AND DATE(?)
        ''', (start, end))
        total_adocoes = cursor.fetchone()[0]

        # 4. Doações Recebidas no Período
        cursor.execute('''
            SELECT SUM(amount) FROM donations
            WHERE DATE(date) BETWEEN DATE(?) AND DATE(?)
        ''', (start, end))
        doacoes_sum = cursor.fetchone()[0]
        if doacoes_sum is None:
            doacoes_sum = 0.0

        # 5. Total de Novos Adotantes no Período
        cursor.execute('''
            SELECT COUNT(*) FROM adopters
            WHERE DATE(created_at) BETWEEN DATE(?) AND DATE(?)
        ''', (start, end))
        novos_adotantes = cursor.fetchone()[0]

        # 6. Total de Novos Voluntários no Período
        cursor.execute('''
            SELECT COUNT(*) FROM volunteers
            WHERE DATE(created_at) BETWEEN DATE(?) AND DATE(?)
        ''', (start, end))
        novos_voluntarios = cursor.fetchone()[0]

        # 7. Total de Doações Médias por Dia no Período
        dias = (end_dt - start_dt).days + 1
        doacoes_media_diaria = doacoes_sum / dias if dias > 0 else 0.0

        conn.close()

        # Montar o texto do relatório
        report_str = f"Relatório de {start} a {end}\n\n"
        report_str += f"1. Total de Animais Disponíveis: {total_animais_disponiveis}\n"
        report_str += f"2. Total de Animais Adicionados no Período: {total_animais_adicionados}\n"
        report_str += f"3. Total de Adoções Realizadas: {total_adocoes}\n"
        report_str += f"4. Total de Doações Recebidas: R$ {doacoes_sum:.2f}\n"
        report_str += f"5. Total de Novos Adotantes: {novos_adotantes}\n"
        report_str += f"6. Total de Novos Voluntários: {novos_voluntarios}\n"
        report_str += f"7. Doações Médias por Dia: R$ {doacoes_media_diaria:.2f}\n"

        # Exibir o relatório na interface
        self.report_text.setText(report_str)
        self.export_button.setEnabled(True)

    def export_pdf(self):
        if not PDF_AVAILABLE:
            QMessageBox.warning(self, "Erro", "Biblioteca 'reportlab' não está instalada. Instale-a usando 'pip install reportlab'.")
            return

        report_content = self.report_text.toPlainText()
        if not report_content.strip():
            QMessageBox.warning(self, "Erro", "Gere o relatório primeiro antes de exportar.")
            return

        # Caminho do arquivo PDF
        filename = "relatorio.pdf"

        try:
            c = canvas.Canvas(filename, pagesize=A4)
            c.setFont("Helvetica", 12)

            text_object = c.beginText(2*cm, 27*cm)
            for line in report_content.split("\n"):
                text_object.textLine(line)
            c.drawText(text_object)
            c.showPage()
            c.save()

            QMessageBox.information(self, "Sucesso", f"Relatório exportado para {os.path.abspath(filename)}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao exportar o PDF: {str(e)}")
