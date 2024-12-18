from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QDateEdit, QTextEdit, QMessageBox,
    QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, QDate
from database import create_connection
from datetime import datetime
import os
import sys

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    
def resource_path(relative_path):
    """Retorna o caminho absoluto para recursos, mesmo no executável."""
    if hasattr(sys, '_MEIPASS'):  # Atributo adicionado pelo PyInstaller
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class ReportWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.set_styles()

    def set_styles(self):
        style = (
            "QWidget {"
            "    background-color: #f4f6fb;"
            "    font-family: Arial, sans-serif;"
            "}"
            "QPushButton {"
            "    border: 1px solid #eef1f6;"
            "    border-radius: 15px;"
            "    background-color: #ffffff;"
            "    color: black;"
            "    padding: 8px 15px;"
            "    font-size: 14px;"
            "    margin: 2px;"
            "}"
            "QPushButton:hover {"
            "    background-color: #eaeaea;"
            "}"
            "QPushButton:disabled {"
            "    background-color: #d3d3d3;"
            "    color: #a9a9a9;"
            "}"
            "QDateEdit, QTextEdit {"
            "    background-color: #fff;"
            "    border: 1px solid #eef1f6;"
            "    border-radius: 5px;"
            "    padding: 5px;"
            "    font-size: 14px;"
            "}"
            "QLabel {"
            "    font-size: 14px;"
            "    color: #333333;"
            "}"
        )
        self.setStyleSheet(style)

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Title
        title = QLabel("Relatório")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title)

        # Quick report buttons in a group box
        quick_group = QGroupBox("Períodos Rápidos")
        quick_layout = QHBoxLayout()
        quick_group.setLayout(quick_layout)

        self.weekly_button = QPushButton("Semanal")
        self.weekly_button.clicked.connect(lambda: self.set_date_range('weekly'))
        quick_layout.addWidget(self.weekly_button)

        self.biweekly_button = QPushButton("Quinzenal")
        self.biweekly_button.clicked.connect(lambda: self.set_date_range('biweekly'))
        quick_layout.addWidget(self.biweekly_button)

        self.monthly_button = QPushButton("Mensal")
        self.monthly_button.clicked.connect(lambda: self.set_date_range('monthly'))
        quick_layout.addWidget(self.monthly_button)

        self.bimonthly_button = QPushButton("Bimestral")
        self.bimonthly_button.clicked.connect(lambda: self.set_date_range('bimonthly'))
        quick_layout.addWidget(self.bimonthly_button)

        self.semiannual_button = QPushButton("Semestral")
        self.semiannual_button.clicked.connect(lambda: self.set_date_range('semiannual'))
        quick_layout.addWidget(self.semiannual_button)

        self.annual_button = QPushButton("Anual")
        self.annual_button.clicked.connect(lambda: self.set_date_range('annual'))
        quick_layout.addWidget(self.annual_button)

        main_layout.addWidget(quick_group)

        # Date range selection in a group box
        date_group = QGroupBox("Selecionar Intervalo")
        date_form = QFormLayout()

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        date_form.addRow("Data Inicial:", self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        date_form.addRow("Data Final:", self.end_date)

        date_group.setLayout(date_form)
        main_layout.addWidget(date_group)

        # Generate and export buttons
        buttons_layout = QHBoxLayout()
        self.generate_button = QPushButton("Gerar Relatório")
        self.generate_button.clicked.connect(self.generate_report)
        buttons_layout.addWidget(self.generate_button)

        self.export_button = QPushButton("Exportar PDF")
        self.export_button.clicked.connect(self.export_pdf)
        self.export_button.setEnabled(False)
        buttons_layout.addWidget(self.export_button)

        main_layout.addLayout(buttons_layout)

        # Report text display
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        main_layout.addWidget(self.report_text)

        self.setLayout(main_layout)

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
        start_dt = datetime.strptime(start, "%Y-%m-%d")
        end_dt = datetime.strptime(end, "%Y-%m-%d")

        if end_dt < start_dt:
            QMessageBox.warning(self, "Erro", "A data final deve ser maior ou igual à data inicial.")
            return

        conn = create_connection()
        cursor = conn.cursor()

        # Total animais disponíveis no final do período
        cursor.execute('''
            SELECT COUNT(*) FROM animals
            WHERE DATE(created_at) <= DATE(?) AND status != 'Adotado'
        ''', (end,))
        total_animais_disponiveis = cursor.fetchone()[0]

        # Total animais adicionados
        cursor.execute('''
            SELECT COUNT(*) FROM animals
            WHERE DATE(created_at) BETWEEN DATE(?) AND DATE(?)
        ''', (start, end))
        total_animais_adicionados = cursor.fetchone()[0]

        # Adoções realizadas
        cursor.execute('''
            SELECT COUNT(*) FROM adoptions
            WHERE DATE(date) BETWEEN DATE(?) AND DATE(?)
        ''', (start, end))
        total_adocoes = cursor.fetchone()[0]

        # Doações recebidas
        cursor.execute('''
            SELECT SUM(amount) FROM donations
            WHERE DATE(date) BETWEEN DATE(?) AND DATE(?)
        ''', (start, end))
        doacoes_sum = cursor.fetchone()[0]
        if doacoes_sum is None:
            doacoes_sum = 0.0

        # Novos adotantes
        cursor.execute('''
            SELECT COUNT(*) FROM adopters
            WHERE DATE(created_at) BETWEEN DATE(?) AND DATE(?)
        ''', (start, end))
        novos_adotantes = cursor.fetchone()[0]

        # Novos voluntários
        cursor.execute('''
            SELECT COUNT(*) FROM volunteers
            WHERE DATE(created_at) BETWEEN DATE(?) AND DATE(?)
        ''', (start, end))
        novos_voluntarios = cursor.fetchone()[0]

        # Média diária de doações
        dias = (end_dt - start_dt).days + 1
        doacoes_media_diaria = doacoes_sum / dias if dias > 0 else 0.0

        conn.close()

        report_str = f"Período: {start} a {end}\n\n"
        report_str += f"1. Total de Animais Disponíveis: {total_animais_disponiveis}\n"
        report_str += f"2. Total de Animais Adicionados: {total_animais_adicionados}\n"
        report_str += f"3. Total de Adoções Realizadas: {total_adocoes}\n"
        report_str += f"4. Doações Recebidas: R$ {doacoes_sum:.2f}\n"
        report_str += f"5. Novos Adotantes: {novos_adotantes}\n"
        report_str += f"6. Novos Voluntários: {novos_voluntarios}\n"
        report_str += f"7. Doações Médias/Dia: R$ {doacoes_media_diaria:.2f}\n"

        self.report_text.setText(report_str)
        self.export_button.setEnabled(True)

    def export_pdf(self):
        if not PDF_AVAILABLE:
            QMessageBox.warning(self, "Erro", "Biblioteca 'reportlab' não está instalada.")
            return

        report_content = self.report_text.toPlainText().strip()
        if not report_content:
            QMessageBox.warning(self, "Erro", "Gere o relatório primeiro.")
            return

        filename = "relatorio.pdf"

        try:
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.lib import colors

            # Parse the generated report text.
            # The text format was something like:
            # Período: yyyy-mm-dd a yyyy-mm-dd
            # (line by line data)
            lines = report_content.split("\n")
            # First line: Period info
            period_line = lines[0] if lines else "Período Desconhecido"
            data_lines = lines[2:]  # Skip the blank line and the period line

            # Extracting data in a structured manner:
            # Expected lines like: "1. Total de Animais Disponíveis: X"
            # We'll create a table with two columns: Description and Value
            table_data = []
            for dl in data_lines:
                # Each line: "N. <description>: <value>"
                parts = dl.split(":")
                if len(parts) == 2:
                    desc = parts[0].strip()
                    val = parts[1].strip()
                    table_data.append([desc, val])

            # Setup document
            doc = SimpleDocTemplate(
                filename,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )

            # Styles
            styles = getSampleStyleSheet()
            # Modify some default styles or add new ones
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Title'],
                fontName='Helvetica-Bold',
                fontSize=20,
                leading=24,
                alignment=1,  # center
                textColor=colors.black
            )

            subtitle_style = ParagraphStyle(
                'SubtitleStyle',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=12,
                textColor=colors.grey,
                alignment=1
            )

            section_header_style = ParagraphStyle(
                'SectionHeader',
                parent=styles['Heading2'],
                fontName='Helvetica-Bold',
                fontSize=14,
                textColor=colors.black,
                spaceAfter=10
            )

            normal_style = styles['Normal']

            # Build story
            story = []

            # Logo and title (side by side)
            logo_path = resource_path("icons/logo_amar.png")  # Ensure this exists
            if os.path.exists(logo_path):
                # Adjust width/height to taste
                logo = Image(logo_path, width=3*cm, height=3*cm)
            else:
                logo = Paragraph("<b>[LOGO]</b>", normal_style)

            # We'll place the logo and the title side by side using a table:
            header_data = [
                [logo, Paragraph("Relatório de Atividades", title_style)]
            ]
            header_table = Table(header_data, colWidths=[4*cm, None])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertically center
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black)
            ]))
            story.append(header_table)
            story.append(Spacer(1, 0.5*cm))

            # Subtitle (Period)
            story.append(Paragraph(period_line, subtitle_style))
            story.append(Spacer(1, 0.5*cm))

            # Section header
            # story.append(Paragraph("Resumo", section_header_style))
            # story.append(Spacer(1, 0.2*cm))

            # Create table with data
            # Add a header row
            table_header = [['Descrição', 'Valor']]
            final_table_data = table_header + table_data

            report_table = Table(final_table_data, colWidths=[10*cm, None])
            report_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dfe6f0')),  # Header background
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('GRID', (0,0), (-1, -1), 0.5, colors.grey),
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),  # Align values to right
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            story.append(report_table)
            story.append(Spacer(1, 1*cm))

            # A concluding paragraph or footer can be added if desired.
            # For example, we can add a subtle note at the bottom:
            story.append(Paragraph("Este relatório foi gerado automaticamente pelo sistema.", normal_style))

            # Build the PDF
            doc.build(story)

            QMessageBox.information(self, "Sucesso", f"Relatório exportado para {os.path.abspath(filename)}")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao exportar o PDF: {str(e)}")

