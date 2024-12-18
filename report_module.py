from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QDateEdit, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QDate
from database import create_connection
from datetime import datetime
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
        )
        self.setStyleSheet(style)

    def initUI(self):
        layout = QVBoxLayout()

        # Título
        title = QLabel("Relatório")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # Botões de períodos rápidos
        quick_report_layout = QHBoxLayout()
        self.weekly_button = QPushButton("Semanal")
        self.weekly_button.clicked.connect(lambda: self.set_date_range('weekly'))
        quick_report_layout.addWidget(self.weekly_button)

        self.monthly_button = QPushButton("Mensal")
        self.monthly_button.clicked.connect(lambda: self.set_date_range('monthly'))
        quick_report_layout.addWidget(self.monthly_button)

        self.annual_button = QPushButton("Anual")
        self.annual_button.clicked.connect(lambda: self.set_date_range('annual'))
        quick_report_layout.addWidget(self.annual_button)

        layout.addLayout(quick_report_layout)

        # Seleção de Data
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

        # Botão de gerar relatório
        self.generate_button = QPushButton("Gerar Relatório")
        self.generate_button.clicked.connect(self.generate_report)
        layout.addWidget(self.generate_button)

        # Área de texto para exibir o sumário
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        layout.addWidget(self.report_text)

        # Botão de exportar PDF
        self.export_button = QPushButton("Exportar PDF")
        self.export_button.clicked.connect(self.export_pdf)
        self.export_button.setEnabled(False)
        layout.addWidget(self.export_button)

        self.setLayout(layout)

    def set_date_range(self, period):
        end_date = QDate.currentDate()
        if period == 'weekly':
            start_date = end_date.addDays(-7)
        elif period == 'monthly':
            start_date = end_date.addMonths(-1)
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

        start_dt = datetime.strptime(start, "%Y-%m-%d")
        end_dt = datetime.strptime(end, "%Y-%m-%d")

        if end_dt < start_dt:
            QMessageBox.warning(self, "Erro", "A data final deve ser maior ou igual à data inicial.")
            return

        conn = create_connection()
        cursor = conn.cursor()

        # Dados do banco
        cursor.execute('''
            SELECT COUNT(*) FROM animals WHERE DATE(created_at) <= DATE(?) AND status != 'Adotado'
        ''', (end,))
        total_animais_disponiveis = cursor.fetchone()[0]

        cursor.execute('''
            SELECT COUNT(*) FROM animals WHERE DATE(created_at) BETWEEN DATE(?) AND DATE(?)
        ''', (start, end))
        total_animais_adicionados = cursor.fetchone()[0]

        cursor.execute('''
            SELECT COUNT(*) FROM adoptions WHERE DATE(date) BETWEEN DATE(?) AND DATE(?)
        ''', (start, end))
        total_adocoes = cursor.fetchone()[0]

        cursor.execute('''
            SELECT SUM(amount) FROM donations WHERE DATE(date) BETWEEN DATE(?) AND DATE(?)
        ''', (start, end))
        doacoes_sum = cursor.fetchone()[0] or 0.0

        cursor.execute('''
            SELECT COUNT(*) FROM adopters WHERE DATE(created_at) BETWEEN DATE(?) AND DATE(?)
        ''', (start, end))
        novos_adotantes = cursor.fetchone()[0]

        conn.close()

        report_str = f"Relatório de {start} a {end}\n\n"
        report_str += f"1. Animais Disponíveis: {total_animais_disponiveis}\n"
        report_str += f"2. Animais Adicionados: {total_animais_adicionados}\n"
        report_str += f"3. Adoções Realizadas: {total_adocoes}\n"
        report_str += f"4. Doações Recebidas: R$ {doacoes_sum:.2f}\n"
        report_str += f"5. Novos Adotantes: {novos_adotantes}\n"

        self.report_text.setText(report_str)
        self.export_button.setEnabled(True)

    def export_pdf(self):
        if not PDF_AVAILABLE:
            QMessageBox.warning(self, "Erro", "Instale a biblioteca 'reportlab'.")
            return

        report_content = self.report_text.toPlainText()
        if not report_content.strip():
            QMessageBox.warning(self, "Erro", "Gere o relatório antes de exportar.")
            return

        filename = "relatorio.pdf"

        try:
            c = canvas.Canvas(filename, pagesize=A4)
            width, height = A4
            margin = 2 * cm
            y_position = height - margin

            # Capa
            c.setFont("Helvetica-Bold", 20)
            c.drawCentredString(width / 2, y_position, "Relatório de Animais")
            y_position -= 2 * cm
            c.setFont("Helvetica", 12)
            c.drawCentredString(width / 2, y_position, f"Período: {self.start_date.date().toString('dd/MM/yyyy')} a {self.end_date.date().toString('dd/MM/yyyy')}")
            y_position -= 1 * cm
            c.drawCentredString(width / 2, y_position, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            c.showPage()

            # Conteúdo
            c.setFont("Helvetica", 12)
            y_position = height - margin

            for line in report_content.split("\n"):
                if y_position < margin:
                    c.showPage()
                    y_position = height - margin
                c.drawString(margin, y_position, line)
                y_position -= 0.7 * cm

            c.save()

            QMessageBox.information(self, "Sucesso", f"Relatório exportado para {os.path.abspath(filename)}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar o PDF: {str(e)}")
