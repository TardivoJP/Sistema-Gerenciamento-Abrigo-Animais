from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QDateEdit, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt
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

    def initUI(self):
        layout = QVBoxLayout()

        title = QLabel("Relatório")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # Seleção de Data Inicial e Data Final
        date_layout = QHBoxLayout()
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(datetime.now())
        date_layout.addWidget(QLabel("Data Inicial:"))
        date_layout.addWidget(self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(datetime.now())
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

        # Animais disponíveis no final do período:
        # status != 'Adotado'
        # Isso é no final do período, assumiremos estado atual (não temos histórico).
        # Se quisermos considerar apenas os animais adicionados até end_dt,
        # precisamos de um campo data_criacao em animals (não existe).
        # Por enquanto, consideramos estado atual.
        cursor.execute('SELECT COUNT(*) FROM animals WHERE status != "Adotado"')
        total_animals_available = cursor.fetchone()[0]

        # Adoções realizadas no período
        cursor.execute('''
            SELECT COUNT(*) FROM adoptions
            WHERE date BETWEEN ? AND ?
        ''', (start, end))
        adoptions_count = cursor.fetchone()[0]

        # Doações no período (soma)
        cursor.execute('''
            SELECT SUM(amount) FROM donations
            WHERE date BETWEEN ? AND ?
        ''', (start, end))
        donations_sum = cursor.fetchone()[0]
        if donations_sum is None:
            donations_sum = 0.0

        # Novos voluntários no período
        # Precisamos de um campo data_criacao em volunteers para isso. Não temos no schema atual.
        # Supondo que iremos adicionar campo 'created_at' em volunteers (YYYY-MM-DD)
        # Caso não haja, apenas não mostra essa estatística ou assume que não temos histórico.
        # Aqui demonstraremos com a suposição que existe um campo created_at:
        # Se não existe, vamos pular essa estatística ou mostrar não disponível.
        try:
            cursor.execute('SELECT COUNT(*) FROM volunteers WHERE birth_date BETWEEN ? AND ?', (start, end))
            # Usando birth_date como um proxy, NÃO É O IDEAL, pois não temos data de criação no schema.
            # Em um cenário real, precisaríamos de um campo data_criacao em volunteers.
            new_volunteers = cursor.fetchone()[0]
        except:
            new_volunteers = "N/D"

        # Animais adicionados no período
        # Mesmo problema que voluntários. Não existe campo de data_criacao em animals.
        # Vamos pular ou mostrar não disponível.
        # Precisaríamos de uma coluna 'added_date' em animals.
        # Suponhamos que iremos pular esta estatística se não temos data.
        new_animals = "N/D"

        conn.close()

        # Montar o texto do relatório
        report_str = f"Relatório de {start} a {end}\n\n"
        report_str += f"Animais disponíveis atualmente: {total_animals_available}\n"
        report_str += f"Adoções realizadas no período: {adoptions_count}\n"
        report_str += f"Total de Doações no período: R$ {donations_sum:.2f}\n"
        report_str += f"Novos voluntários (baseado em birth_date): {new_volunteers}\n"
        report_str += f"Novos animais adicionados no período: {new_animals}\n"

        self.report_text.setText(report_str)
        self.export_button.setEnabled(True)

    def export_pdf(self):
        if not PDF_AVAILABLE:
            QMessageBox.warning(self, "Erro", "Biblioteca 'reportlab' não disponível. Não é possível exportar PDF.")
            return

        report_content = self.report_text.toPlainText()
        if not report_content.strip():
            QMessageBox.warning(self, "Erro", "Gere o relatório primeiro antes de exportar.")
            return

        # Caminho do arquivo PDF
        filename = "relatorio.pdf"

        c = canvas.Canvas(filename, pagesize=A4)
        c.setFont("Helvetica", 12)

        text_object = c.beginText(2*cm, 27*cm)
        for line in report_content.split("\n"):
            text_object.textLine(line)
        c.drawText(text_object)
        c.showPage()
        c.save()

        QMessageBox.information(self, "Sucesso", f"Relatório exportado para {os.path.abspath(filename)}")
