from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QLabel, QLineEdit, QTextEdit, QCheckBox, QMessageBox,
    QStackedLayout, QFormLayout, QToolButton, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from database import create_connection

class AnimalListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_page = 0
        self.page_size = 25
        self.initUI()

    def initUI(self):
        # Layout principal com pilha para alternar entre tabela e formulário
        self.layout = QVBoxLayout()
        self.stacked_layout = QStackedLayout()

        # Tela da tabela de animais
        self.table_widget = QWidget()
        self.initTableUI()
        self.stacked_layout.addWidget(self.table_widget)

        # Tela do formulário de novo animal
        self.form_widget = QWidget()
        self.initFormUI()
        self.stacked_layout.addWidget(self.form_widget)

        # Tela do formulário de edição de animal
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
        title = QLabel("Lista de Animais")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "Tipo", "Raça", "Vacinado", "Castrado", "Status", "", ""])
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
        self.new_button = QPushButton("Novo Cadastro")
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

        # Tipo (ComboBox)
        self.type_input = QComboBox()
        self.type_input.addItem("")
        self.type_input.addItem("Cachorro")
        self.type_input.addItem("Gato")
        form_layout.addRow("Tipo:", self.type_input)

        # Raça
        self.breed_input = QLineEdit()
        form_layout.addRow("Raça:", self.breed_input)

        # Vacinado
        self.vaccinated_input = QCheckBox("Vacinado")
        form_layout.addRow(self.vaccinated_input)

        # Castrado
        self.neutered_input = QCheckBox("Castrado")
        form_layout.addRow(self.neutered_input)

        # Descrição
        self.description_input = QTextEdit()
        form_layout.addRow("Descrição:", self.description_input)

        layout.addLayout(form_layout)

        # Botões de Ação
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.save_animal)
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

        # Tipo (ComboBox)
        self.edit_type_input = QComboBox()
        self.edit_type_input.addItem("")
        self.edit_type_input.addItem("Cachorro")
        self.edit_type_input.addItem("Gato")
        form_layout.addRow("Tipo:", self.edit_type_input)

        # Raça
        self.edit_breed_input = QLineEdit()
        form_layout.addRow("Raça:", self.edit_breed_input)

        # Vacinado
        self.edit_vaccinated_input = QCheckBox("Vacinado")
        form_layout.addRow(self.edit_vaccinated_input)

        # Castrado
        self.edit_neutered_input = QCheckBox("Castrado")
        form_layout.addRow(self.edit_neutered_input)

        # Descrição
        self.edit_description_input = QTextEdit()
        form_layout.addRow("Descrição:", self.edit_description_input)

        layout.addLayout(form_layout)

        # Botões de Ação
        button_layout = QHBoxLayout()
        self.update_button = QPushButton("Confirmar Edição")
        self.update_button.clicked.connect(self.update_animal)
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
            SELECT id, name, type, breed, vaccinated, neutered, status FROM animals
            LIMIT ? OFFSET ?
        ''', (self.page_size, offset))
        records = cursor.fetchall()
        self.table.setRowCount(len(records))

        for row_idx, row_data in enumerate(records):
            for col_idx, col_data in enumerate(row_data):
                if col_idx in (4, 5):  # Colunas 'vacinado' e 'castrado'
                    col_data = "Sim" if col_data else "Não"
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

            animal_status = row_data[6]  # Status do animal

            # Botão de editar
            edit_button = QPushButton("Editar")
            edit_button.clicked.connect(lambda checked, row=row_data[0]: self.edit_animal(row))
            self.table.setCellWidget(row_idx, 7, edit_button)

            # Botão de deletar
            delete_button = QPushButton("Deletar")
            delete_button.clicked.connect(lambda checked, row=row_data[0]: self.delete_animal(row))
            self.table.setCellWidget(row_idx, 8, delete_button)

            # Desabilitar botões se o animal já foi adotado
            if animal_status == 'Adotado':
                edit_button.setEnabled(False)
                delete_button.setEnabled(False)

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
        self.type_input.setCurrentIndex(0)
        self.breed_input.clear()
        self.vaccinated_input.setChecked(False)
        self.neutered_input.setChecked(False)
        self.description_input.clear()
        # Alterar para a tela do formulário
        self.stacked_layout.setCurrentWidget(self.form_widget)

    def cancel_form(self):
        # Voltar para a tela da tabela
        self.stacked_layout.setCurrentWidget(self.table_widget)

    def save_animal(self):
        name = self.name_input.text().strip()
        type_ = self.type_input.currentText().strip()
        breed = self.breed_input.text().strip()
        vaccinated = self.vaccinated_input.isChecked()
        neutered = self.neutered_input.isChecked()
        description = self.description_input.toPlainText().strip()

        # Validação dos dados
        if not name or not type_:
            QMessageBox.warning(self, "Erro", "Por favor, preencha os campos obrigatórios: Nome e Tipo.")
            return
        if not breed:
            QMessageBox.warning(self, "Erro", "Por favor, preencha o campo: Raça.")
            return

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO animals (name, type, breed, vaccinated, neutered, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, type_, breed, int(vaccinated), int(neutered), description))
        conn.commit()
        conn.close()

        # Voltar para a tela da tabela e atualizar os dados
        self.stacked_layout.setCurrentWidget(self.table_widget)
        self.load_data()

    def edit_animal(self, animal_id):
        # Carregar dados do animal
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM animals WHERE id = ?', (animal_id,))
        record = cursor.fetchone()
        conn.close()

        if record:
            self.edit_id = record[0]
            self.edit_name_input.setText(record[1])
            index = self.edit_type_input.findText(record[2])
            self.edit_type_input.setCurrentIndex(index)
            self.edit_breed_input.setText(record[3])
            self.edit_vaccinated_input.setChecked(bool(record[4]))
            self.edit_neutered_input.setChecked(bool(record[5]))
            self.edit_description_input.setPlainText(record[6])

            # Alterar para a tela do formulário de edição
            self.stacked_layout.setCurrentWidget(self.edit_form_widget)
        else:
            QMessageBox.warning(self, "Erro", "Animal não encontrado.")

    def update_animal(self):
        name = self.edit_name_input.text().strip()
        type_ = self.edit_type_input.currentText().strip()
        breed = self.edit_breed_input.text().strip()
        vaccinated = self.edit_vaccinated_input.isChecked()
        neutered = self.edit_neutered_input.isChecked()
        description = self.edit_description_input.toPlainText().strip()

        # Validação dos dados
        if not name or not type_:
            QMessageBox.warning(self, "Erro", "Por favor, preencha os campos obrigatórios: Nome e Tipo.")
            return
        if not breed:
            QMessageBox.warning(self, "Erro", "Por favor, preencha o campo: Raça.")
            return

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE animals
            SET name = ?, type = ?, breed = ?, vaccinated = ?, neutered = ?, description = ?
            WHERE id = ?
        ''', (name, type_, breed, int(vaccinated), int(neutered), description, self.edit_id))
        conn.commit()
        conn.close()

        # Voltar para a tela da tabela e atualizar os dados
        self.stacked_layout.setCurrentWidget(self.table_widget)
        self.load_data()

    def delete_animal(self, animal_id):
        reply = QMessageBox.question(
            self, 'Confirmação', 'Tem certeza que deseja deletar este animal?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM animals WHERE id = ?', (animal_id,))
            conn.commit()
            conn.close()
            self.load_data()
