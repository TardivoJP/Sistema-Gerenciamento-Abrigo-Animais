from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QLabel, QLineEdit, QComboBox, QMessageBox,
    QStackedLayout, QFormLayout, QDateEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from database import create_connection
from datetime import datetime

class AdopterListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_page = 0
        self.page_size = 25
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.stacked_layout = QStackedLayout()

        # Tela da tabela de adotantes
        self.table_widget = QWidget()
        self.initTableUI()
        self.stacked_layout.addWidget(self.table_widget)

        # Tela do formulário de novo adotante
        self.form_widget = QWidget()
        self.initFormUI()
        self.stacked_layout.addWidget(self.form_widget)

        # Tela do formulário de edição de adotante
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
        title = QLabel("Lista de Adotantes")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "Telefone", "CPF", "", ""])
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
        self.new_button = QPushButton("Novo Adotante")
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

        # Ocupação
        self.occupation_input = QLineEdit()
        form_layout.addRow("Ocupação:", self.occupation_input)

        # Renda
        self.income_input = QLineEdit()
        form_layout.addRow("Renda:", self.income_input)

        layout.addLayout(form_layout)

        # Botões de Ação
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.save_adopter)
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

        # Ocupação
        self.edit_occupation_input = QLineEdit()
        form_layout.addRow("Ocupação:", self.edit_occupation_input)

        # Renda
        self.edit_income_input = QLineEdit()
        form_layout.addRow("Renda:", self.edit_income_input)

        layout.addLayout(form_layout)

        # Botões de Ação
        button_layout = QHBoxLayout()
        self.update_button = QPushButton("Salvar Alterações")
        self.update_button.clicked.connect(self.update_adopter)
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
            SELECT id, name, phone, cpf FROM adopters
            LIMIT ? OFFSET ?
        ''', (self.page_size, offset))
        records = cursor.fetchall()
        self.table.setRowCount(len(records))

        for row_idx, row_data in enumerate(records):
            for col_idx, col_data in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

            adopter_id = row_data[0]

            # Botão de editar
            edit_button = QPushButton("Editar")
            edit_button.clicked.connect(lambda checked, aid=adopter_id: self.edit_adopter(aid))
            self.table.setCellWidget(row_idx, 4, edit_button)

            # Botão de deletar
            delete_button = QPushButton("Deletar")
            delete_button.clicked.connect(lambda checked, aid=adopter_id: self.delete_adopter(aid))
            self.table.setCellWidget(row_idx, 5, delete_button)

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
        self.occupation_input.clear()
        self.income_input.clear()
        # Alterar para a tela do formulário
        self.stacked_layout.setCurrentWidget(self.form_widget)

    def cancel_form(self):
        # Voltar para a tela da tabela
        self.stacked_layout.setCurrentWidget(self.table_widget)

    def save_adopter(self):
        name = self.name_input.text().strip()
        address = self.address_input.text().strip()
        phone = self.phone_input.text().strip()
        cpf = self.cpf_input.text().strip()
        birth_date = self.birth_date_input.date().toString("yyyy-MM-dd")
        occupation = self.occupation_input.text().strip()
        income = self.income_input.text().strip()

        # Validação dos dados
        if not name or not cpf:
            QMessageBox.warning(self, "Erro", "Por favor, preencha os campos obrigatórios: Nome e CPF.")
            return

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO adopters (name, address, phone, cpf, birth_date, occupation, income)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, address, phone, cpf, birth_date, occupation, income))
        conn.commit()
        conn.close()

        # Voltar para a tela da tabela e atualizar os dados
        self.stacked_layout.setCurrentWidget(self.table_widget)
        self.load_data()

    def edit_adopter(self, adopter_id):
        # Carregar dados do adotante
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM adopters WHERE id = ?', (adopter_id,))
        record = cursor.fetchone()
        conn.close()

        if record:
            self.edit_id = record[0]
            self.edit_name_input.setText(record[1])
            self.edit_address_input.setText(record[2])
            self.edit_phone_input.setText(record[3])
            self.edit_cpf_input.setText(record[4])
            self.edit_birth_date_input.setDate(datetime.strptime(record[5], "%Y-%m-%d"))
            self.edit_occupation_input.setText(record[6])
            self.edit_income_input.setText(str(record[7]) if record[7] else "")
            # Alterar para a tela do formulário de edição
            self.stacked_layout.setCurrentWidget(self.edit_form_widget)
        else:
            QMessageBox.warning(self, "Erro", "Adotante não encontrado.")

    def update_adopter(self):
        name = self.edit_name_input.text().strip()
        address = self.edit_address_input.text().strip()
        phone = self.edit_phone_input.text().strip()
        cpf = self.edit_cpf_input.text().strip()
        birth_date = self.edit_birth_date_input.date().toString("yyyy-MM-dd")
        occupation = self.edit_occupation_input.text().strip()
        income = self.edit_income_input.text().strip()

        # Validação dos dados
        if not name or not cpf:
            QMessageBox.warning(self, "Erro", "Por favor, preencha os campos obrigatórios: Nome e CPF.")
            return

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE adopters
            SET name = ?, address = ?, phone = ?, cpf = ?, birth_date = ?, occupation = ?, income = ?
            WHERE id = ?
        ''', (name, address, phone, cpf, birth_date, occupation, income, self.edit_id))
        conn.commit()
        conn.close()

        # Voltar para a tela da tabela e atualizar os dados
        self.stacked_layout.setCurrentWidget(self.table_widget)
        self.load_data()

    def delete_adopter(self, adopter_id):
        reply = QMessageBox.question(
            self, 'Confirmação', 'Tem certeza que deseja deletar este adotante?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            conn = create_connection()
            cursor = conn.cursor()

            # Verificar se o adotante tem adoções associadas
            cursor.execute('SELECT COUNT(*) FROM adoptions WHERE adopter_id = ?', (adopter_id,))
            count = cursor.fetchone()[0]
            if count > 0:
                QMessageBox.warning(self, "Erro", "Não é possível deletar um adotante com adoções associadas.")
                conn.close()
                return

            cursor.execute('DELETE FROM adopters WHERE id = ?', (adopter_id,))
            conn.commit()
            conn.close()
            self.load_data()
