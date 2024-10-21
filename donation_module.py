from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QLabel, QComboBox, QMessageBox,
    QStackedLayout, QFormLayout, QDateEdit, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from database import create_connection
from datetime import datetime

class DonationsListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_page = 0
        self.page_size = 25
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.stacked_layout = QStackedLayout()

        # Tela da tabela de doações
        self.table_widget = QWidget()
        self.initTableUI()
        self.stacked_layout.addWidget(self.table_widget)

        # Tela do formulário de nova doação
        self.form_widget = QWidget()
        self.initFormUI()
        self.stacked_layout.addWidget(self.form_widget)

        # Tela do formulário de edição de doação
        self.edit_form_widget = QWidget()
        self.initEditFormUI()
        self.stacked_layout.addWidget(self.edit_form_widget)

        self.layout.addLayout(self.stacked_layout)
        self.setLayout(self.layout)

        # Exibir a tabela inicialmente
        self.stacked_layout.setCurrentWidget(self.table_widget)

    def initTableUI(self):
        layout = QVBoxLayout()

        # Título
        title = QLabel("Lista de Doações")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Voluntário", "Data", "Valor", ""])
        layout.addWidget(self.table)

        # Controles de Paginação
        pagination_layout = QHBoxLayout()
        self.prev_button = QPushButton("Anterior")
        self.next_button = QPushButton("Próximo")
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.next_button)
        layout.addLayout(pagination_layout)

        # Botão Nova Doação
        self.new_button = QPushButton("Nova Doação")
        self.new_button.clicked.connect(self.show_form)
        layout.addWidget(self.new_button)

        self.table_widget.setLayout(layout)
        self.load_data()

    def initFormUI(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        # Seleção do Voluntário
        self.volunteer_combo = QComboBox()
        self.load_volunteers()
        form_layout.addRow("Voluntário:", self.volunteer_combo)

        # Data da Doação
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(datetime.now())
        form_layout.addRow("Data da Doação:", self.date_input)

        # Valor
        self.amount_input = QLineEdit()
        form_layout.addRow("Valor:", self.amount_input)

        layout.addLayout(form_layout)

        # Botões de Ação
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.save_donation)
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.cancel_form)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.form_widget.setLayout(layout)

    def initEditFormUI(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        # ID da doação
        self.edit_donation_id = None

        # Seleção do Voluntário
        self.edit_volunteer_combo = QComboBox()
        self.load_volunteers(edit=True)
        form_layout.addRow("Voluntário:", self.edit_volunteer_combo)

        # Data da Doação
        self.edit_date_input = QDateEdit()
        self.edit_date_input.setCalendarPopup(True)
        self.edit_date_input.setDate(datetime.now())
        form_layout.addRow("Data da Doação:", self.edit_date_input)

        # Valor
        self.edit_amount_input = QLineEdit()
        form_layout.addRow("Valor:", self.edit_amount_input)

        layout.addLayout(form_layout)

        # Botões de Ação
        button_layout = QHBoxLayout()
        self.update_button = QPushButton("Salvar Alterações")
        self.update_button.clicked.connect(self.update_donation)
        self.cancel_edit_button = QPushButton("Cancelar")
        self.cancel_edit_button.clicked.connect(self.cancel_form)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.cancel_edit_button)

        layout.addLayout(button_layout)

        self.edit_form_widget.setLayout(layout)

    def load_volunteers(self, edit=False):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM volunteers')
        volunteers = cursor.fetchall()
        if edit:
            combo = self.edit_volunteer_combo
        else:
            combo = self.volunteer_combo
        combo.clear()
        combo.insertItem(0, "", None)
        for volunteer in volunteers:
            combo.addItem(f"{volunteer[1]} (ID: {volunteer[0]})", volunteer[0])
        conn.close()

    def load_data(self):
        conn = create_connection()
        cursor = conn.cursor()
        offset = self.current_page * self.page_size
        cursor.execute('''
            SELECT donations.id, volunteers.name, donations.date, donations.amount, volunteers.id
            FROM donations
            JOIN volunteers ON donations.volunteer_id = volunteers.id
            LIMIT ? OFFSET ?
        ''', (self.page_size, offset))
        records = cursor.fetchall()
        self.table.setRowCount(len(records))

        for row_idx, row_data in enumerate(records):
            for col_idx, col_data in enumerate(row_data[:-1]):  # Exclui o último campo (volunteer_id)
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

            donation_id = row_data[0]

            # Botão de deletar
            delete_button = QPushButton("Deletar")
            delete_button.clicked.connect(lambda checked, did=donation_id: self.delete_donation(did))
            self.table.setCellWidget(row_idx, 4, delete_button)

        conn.close()

    def next_page(self):
        self.current_page += 1
        self.load_data()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_data()

    def show_form(self):
        self.load_volunteers()
        self.volunteer_combo.setCurrentIndex(0)

        self.date_input.setDate(datetime.now())
        self.amount_input.clear()

        self.stacked_layout.setCurrentWidget(self.form_widget)

    def cancel_form(self):
        # Voltar para a tela da tabela
        self.stacked_layout.setCurrentWidget(self.table_widget)

    def save_donation(self):
        volunteer_id = self.volunteer_combo.currentData()
        date = self.date_input.date().toString("yyyy-MM-dd")
        amount = self.amount_input.text().strip()

        # Validação dos dados
        if volunteer_id is None:
            QMessageBox.warning(self, "Erro", "Por favor, selecione um voluntário.")
            return
        if not amount:
            QMessageBox.warning(self, "Erro", "Por favor, informe o valor da doação.")
            return

        try:
            amount = float(amount)
        except ValueError:
            QMessageBox.warning(self, "Erro", "Valor inválido.")
            return

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO donations (volunteer_id, date, amount)
            VALUES (?, ?, ?)
        ''', (volunteer_id, date, amount))
        conn.commit()
        conn.close()

        # Voltar para a tela da tabela e atualizar os dados
        self.stacked_layout.setCurrentWidget(self.table_widget)
        self.load_data()

    def edit_donation(self, donation_id):
        # Carregar dados da doação
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, volunteer_id, date, amount FROM donations WHERE id = ?
        ''', (donation_id,))
        record = cursor.fetchone()
        conn.close()

        if record:
            self.edit_donation_id = record[0]
            volunteer_id = record[1]
            date = record[2]
            amount = record[3]

            self.load_volunteers(edit=True)

            index = self.edit_volunteer_combo.findData(volunteer_id)
            if index != -1:
                self.edit_volunteer_combo.setCurrentIndex(index)
            else:
                self.edit_volunteer_combo.setCurrentIndex(0)

            self.edit_date_input.setDate(datetime.strptime(date, "%Y-%m-%d"))
            self.edit_amount_input.setText(str(amount))

            self.stacked_layout.setCurrentWidget(self.edit_form_widget)
        else:
            QMessageBox.warning(self, "Erro", "Doação não encontrada.")

    def update_donation(self):
        volunteer_id = self.edit_volunteer_combo.currentData()
        date = self.edit_date_input.date().toString("yyyy-MM-dd")
        amount = self.edit_amount_input.text().strip()

        # Validação dos dados
        if volunteer_id is None:
            QMessageBox.warning(self, "Erro", "Por favor, selecione um voluntário.")
            return
        if not amount:
            QMessageBox.warning(self, "Erro", "Por favor, informe o valor da doação.")
            return

        try:
            amount = float(amount)
        except ValueError:
            QMessageBox.warning(self, "Erro", "Valor inválido.")
            return

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE donations
            SET volunteer_id = ?, date = ?, amount = ?
            WHERE id = ?
        ''', (volunteer_id, date, amount, self.edit_donation_id))
        conn.commit()
        conn.close()

        # Voltar para a tela da tabela e atualizar os dados
        self.stacked_layout.setCurrentWidget(self.table_widget)
        self.load_data()

    def delete_donation(self, donation_id):
        reply = QMessageBox.question(
            self, 'Confirmação', 'Tem certeza que deseja deletar esta doação?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM donations WHERE id = ?', (donation_id,))
            conn.commit()
            conn.close()
            self.load_data()
