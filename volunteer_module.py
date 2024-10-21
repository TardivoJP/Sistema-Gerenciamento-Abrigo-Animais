from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QLabel, QLineEdit, QTextEdit, QMessageBox,
    QStackedLayout, QFormLayout, QDateEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from database import create_connection
from datetime import datetime

class VolunteerListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_page = 0
        self.page_size = 25
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.stacked_layout = QStackedLayout()

        # Tela da tabela de voluntários
        self.table_widget = QWidget()
        self.initTableUI()
        self.stacked_layout.addWidget(self.table_widget)

        # Tela do formulário de novo voluntário
        self.form_widget = QWidget()
        self.initFormUI()
        self.stacked_layout.addWidget(self.form_widget)

        # Tela do formulário de edição de voluntário
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
        title = QLabel("Lista de Voluntários")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "Telefone", "", ""])
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

        # Botão Novo Cadastro
        self.new_button = QPushButton("Novo Voluntário")
        self.new_button.clicked.connect(self.show_form)
        layout.addWidget(self.new_button)

        self.table_widget.setLayout(layout)
        self.load_data()

    def initFormUI(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        # Nome
        self.name_input = QLineEdit()
        form_layout.addRow("Nome:", self.name_input)

        # Endereço
        self.address_input = QLineEdit()
        form_layout.addRow("Endereço:", self.address_input)

        # Telefone
        self.phone_input = QLineEdit()
        form_layout.addRow("Telefone:", self.phone_input)

        # CPF
        self.cpf_input = QLineEdit()
        form_layout.addRow("CPF:", self.cpf_input)

        # Data de Nascimento
        self.birth_date_input = QDateEdit()
        self.birth_date_input.setCalendarPopup(True)
        self.birth_date_input.setDate(datetime.now())
        form_layout.addRow("Data de Nascimento:", self.birth_date_input)

        # Disponibilidade
        self.availability_input = QTextEdit()
        form_layout.addRow("Disponibilidade:", self.availability_input)

        # Habilidades
        self.skills_input = QTextEdit()
        form_layout.addRow("Habilidades:", self.skills_input)

        # Experiência
        self.experience_input = QTextEdit()
        form_layout.addRow("Experiência:", self.experience_input)

        # Motivação
        self.motivation_input = QTextEdit()
        form_layout.addRow("Motivação:", self.motivation_input)

        layout.addLayout(form_layout)

        # Botões de Ação
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.save_volunteer)
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.cancel_form)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.form_widget.setLayout(layout)

    def initEditFormUI(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        # ID (oculto)
        self.edit_id = None

        # Nome
        self.edit_name_input = QLineEdit()
        form_layout.addRow("Nome:", self.edit_name_input)

        # Endereço
        self.edit_address_input = QLineEdit()
        form_layout.addRow("Endereço:", self.edit_address_input)

        # Telefone
        self.edit_phone_input = QLineEdit()
        form_layout.addRow("Telefone:", self.edit_phone_input)

        # CPF
        self.edit_cpf_input = QLineEdit()
        form_layout.addRow("CPF:", self.edit_cpf_input)

        # Data de Nascimento
        self.edit_birth_date_input = QDateEdit()
        self.edit_birth_date_input.setCalendarPopup(True)
        self.edit_birth_date_input.setDate(datetime.now())
        form_layout.addRow("Data de Nascimento:", self.edit_birth_date_input)

        # Disponibilidade
        self.edit_availability_input = QTextEdit()
        form_layout.addRow("Disponibilidade:", self.edit_availability_input)

        # Habilidades
        self.edit_skills_input = QTextEdit()
        form_layout.addRow("Habilidades:", self.edit_skills_input)

        # Experiência
        self.edit_experience_input = QTextEdit()
        form_layout.addRow("Experiência:", self.edit_experience_input)

        # Motivação
        self.edit_motivation_input = QTextEdit()
        form_layout.addRow("Motivação:", self.edit_motivation_input)

        layout.addLayout(form_layout)

        # Botões de Ação
        button_layout = QHBoxLayout()
        self.update_button = QPushButton("Salvar Alterações")
        self.update_button.clicked.connect(self.update_volunteer)
        self.cancel_edit_button = QPushButton("Cancelar")
        self.cancel_edit_button.clicked.connect(self.cancel_form)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.cancel_edit_button)

        layout.addLayout(button_layout)

        self.edit_form_widget.setLayout(layout)

    def load_data(self):
        conn = create_connection()
        cursor = conn.cursor()
        offset = self.current_page * self.page_size
        cursor.execute('''
            SELECT id, name, phone FROM volunteers
            LIMIT ? OFFSET ?
        ''', (self.page_size, offset))
        records = cursor.fetchall()
        self.table.setRowCount(len(records))

        for row_idx, row_data in enumerate(records):
            for col_idx, col_data in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

            volunteer_id = row_data[0]

            # Botão de editar
            edit_button = QPushButton("Editar")
            edit_button.clicked.connect(lambda checked, vid=volunteer_id: self.edit_volunteer(vid))
            self.table.setCellWidget(row_idx, 3, edit_button)

            # Botão de deletar
            delete_button = QPushButton("Deletar")
            delete_button.clicked.connect(lambda checked, vid=volunteer_id: self.delete_volunteer(vid))
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
        # Limpar os campos do formulário
        self.name_input.clear()
        self.address_input.clear()
        self.phone_input.clear()
        self.cpf_input.clear()
        self.birth_date_input.setDate(datetime.now())
        self.availability_input.clear()
        self.skills_input.clear()
        self.experience_input.clear()
        self.motivation_input.clear()
        # Alterar para a tela do formulário
        self.stacked_layout.setCurrentWidget(self.form_widget)

    def cancel_form(self):
        # Voltar para a tela da tabela
        self.stacked_layout.setCurrentWidget(self.table_widget)

    def save_volunteer(self):
        name = self.name_input.text().strip()
        address = self.address_input.text().strip()
        phone = self.phone_input.text().strip()
        cpf = self.cpf_input.text().strip()
        birth_date = self.birth_date_input.date().toString("yyyy-MM-dd")
        availability = self.availability_input.toPlainText().strip()
        skills = self.skills_input.toPlainText().strip()
        experience = self.experience_input.toPlainText().strip()
        motivation = self.motivation_input.toPlainText().strip()

        # Validação dos dados
        if not name or not cpf:
            QMessageBox.warning(self, "Erro", "Por favor, preencha os campos obrigatórios: Nome e CPF.")
            return

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO volunteers (name, address, phone, cpf, birth_date, availability, skills, experience, motivation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, address, phone, cpf, birth_date, availability, skills, experience, motivation))
        conn.commit()
        conn.close()

        # Voltar para a tela da tabela e atualizar os dados
        self.stacked_layout.setCurrentWidget(self.table_widget)
        self.load_data()

    def edit_volunteer(self, volunteer_id):
        # Carregar dados do voluntário
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM volunteers WHERE id = ?', (volunteer_id,))
        record = cursor.fetchone()
        conn.close()

        if record:
            self.edit_id = record[0]
            self.edit_name_input.setText(record[1])
            self.edit_address_input.setText(record[2])
            self.edit_phone_input.setText(record[3])
            self.edit_cpf_input.setText(record[4])
            self.edit_birth_date_input.setDate(datetime.strptime(record[5], "%Y-%m-%d"))
            self.edit_availability_input.setPlainText(record[6])
            self.edit_skills_input.setPlainText(record[7])
            self.edit_experience_input.setPlainText(record[8])
            self.edit_motivation_input.setPlainText(record[9])
            # Alterar para a tela do formulário de edição
            self.stacked_layout.setCurrentWidget(self.edit_form_widget)
        else:
            QMessageBox.warning(self, "Erro", "Voluntário não encontrado.")

    def update_volunteer(self):
        name = self.edit_name_input.text().strip()
        address = self.edit_address_input.text().strip()
        phone = self.edit_phone_input.text().strip()
        cpf = self.edit_cpf_input.text().strip()
        birth_date = self.edit_birth_date_input.date().toString("yyyy-MM-dd")
        availability = self.edit_availability_input.toPlainText().strip()
        skills = self.edit_skills_input.toPlainText().strip()
        experience = self.edit_experience_input.toPlainText().strip()
        motivation = self.edit_motivation_input.toPlainText().strip()

        # Validação dos dados
        if not name or not cpf:
            QMessageBox.warning(self, "Erro", "Por favor, preencha os campos obrigatórios: Nome e CPF.")
            return

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE volunteers
            SET name = ?, address = ?, phone = ?, cpf = ?, birth_date = ?, availability = ?, skills = ?, experience = ?, motivation = ?
            WHERE id = ?
        ''', (name, address, phone, cpf, birth_date, availability, skills, experience, motivation, self.edit_id))
        conn.commit()
        conn.close()

        # Voltar para a tela da tabela e atualizar os dados
        self.stacked_layout.setCurrentWidget(self.table_widget)
        self.load_data()

    def delete_volunteer(self, volunteer_id):
        reply = QMessageBox.question(
            self, 'Confirmação', 'Tem certeza que deseja deletar este voluntário?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            conn = create_connection()
            cursor = conn.cursor()

            # Verificar se o voluntário tem doações associadas
            cursor.execute('SELECT COUNT(*) FROM donations WHERE volunteer_id = ?', (volunteer_id,))
            count = cursor.fetchone()[0]
            if count > 0:
                QMessageBox.warning(self, "Erro", "Não é possível deletar um voluntário com doações associadas.")
                conn.close()
                return

            cursor.execute('DELETE FROM volunteers WHERE id = ?', (volunteer_id,))
            conn.commit()
            conn.close()
            self.load_data()
