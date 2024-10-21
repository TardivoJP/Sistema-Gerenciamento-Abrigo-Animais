from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QLabel, QComboBox, QDateEdit, QMessageBox, QStackedLayout, QFormLayout, QToolButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from database import create_connection
from datetime import datetime

class AdoptionListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_page = 0
        self.page_size = 25
        self.initUI()

    def initUI(self):
        # Layout principal com pilha para alternar entre tabela e formulário
        self.layout = QVBoxLayout()
        self.stacked_layout = QStackedLayout()

        # Tela da tabela de adoções
        self.table_widget = QWidget()
        self.initTableUI()
        self.stacked_layout.addWidget(self.table_widget)

        # Tela do formulário de nova adoção
        self.form_widget = QWidget()
        self.initFormUI()
        self.stacked_layout.addWidget(self.form_widget)

        self.layout.addLayout(self.stacked_layout)
        self.setLayout(self.layout)

        # Exibir a tabela inicialmente
        self.stacked_layout.setCurrentWidget(self.table_widget)

    def initTableUI(self):
        layout = QVBoxLayout()

        # Título
        title = QLabel("Lista de Adoções")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Adotante", "Animal", "Data", "Status", "", ""])
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

        # Botão Nova Adoção
        self.new_button = QPushButton("Nova Adoção")
        self.new_button.clicked.connect(self.show_form)
        layout.addWidget(self.new_button)

        self.table_widget.setLayout(layout)
        self.load_data()

    def initFormUI(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        # Seleção do Adotante
        self.adopter_combo = QComboBox()
        self.load_adopters()
        form_layout.addRow("Selecionar Adotante:", self.adopter_combo)

        # Seleção do Animal
        self.animal_combo = QComboBox()
        self.load_animals()
        form_layout.addRow("Selecionar Animal:", self.animal_combo)

        # Data da Adoção
        self.date_input = QDateEdit()
        self.date_input.setDate(datetime.now())
        form_layout.addRow("Data da Adoção:", self.date_input)

        # Status
        self.status_input = QComboBox()
        self.status_input.addItems(["Pendente", "Concluída", "Cancelada"])
        form_layout.addRow("Status:", self.status_input)

        layout.addLayout(form_layout)

        # Botões de Ação
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.register_adoption)
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.cancel_form)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.form_widget.setLayout(layout)

    def load_data(self):
        conn = create_connection()
        cursor = conn.cursor()
        offset = self.current_page * self.page_size
        cursor.execute('''
            SELECT adoptions.id, adopters.name, animals.name, adoptions.date, adoptions.status, animals.id
            FROM adoptions
            JOIN adopters ON adoptions.adopter_id = adopters.id
            JOIN animals ON adoptions.animal_id = animals.id
            LIMIT ? OFFSET ?
        ''', (self.page_size, offset))
        records = cursor.fetchall()
        self.table.setRowCount(len(records))

        for row_idx, row_data in enumerate(records):
            for col_idx, col_data in enumerate(row_data[:-1]):  # Exclui o último campo (animal_id)
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

            adoption_id = row_data[0]
            animal_id = row_data[5]

            # Botão de editar
            edit_button = QPushButton("Editar")
            edit_button.clicked.connect(lambda checked, aid=adoption_id: self.edit_adoption(aid))
            self.table.setCellWidget(row_idx, 5, edit_button)

            # Botão de deletar
            delete_button = QPushButton("Deletar")
            delete_button.clicked.connect(lambda checked, aid=adoption_id, anid=animal_id: self.delete_adoption(aid, anid))
            self.table.setCellWidget(row_idx, 6, delete_button)

        conn.close()

    def next_page(self):
        self.current_page += 1
        self.load_data()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_data()

    def show_form(self):
        self.adopter_combo.clear()
        self.animal_combo.clear()
        self.load_adopters()
        self.load_animals()

        self.adopter_combo.insertItem(0, "", None)
        self.animal_combo.insertItem(0, "", None)
        self.adopter_combo.setCurrentIndex(0)
        self.animal_combo.setCurrentIndex(0)

        self.date_input.setDate(datetime.now())
        self.status_input.setCurrentIndex(0)

        self.stacked_layout.setCurrentWidget(self.form_widget)


    def cancel_form(self):
        # Voltar para a tela da tabela
        self.stacked_layout.setCurrentWidget(self.table_widget)

    def load_adopters(self):
        self.adopter_combo.clear()
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM adopters')
        adopters = cursor.fetchall()
        for adopter in adopters:
            self.adopter_combo.addItem(f"{adopter[1]} (ID: {adopter[0]})", adopter[0])
        conn.close()

    def load_animals(self):
        self.animal_combo.clear()
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM animals')
        animals = cursor.fetchall()
        for animal in animals:
            self.animal_combo.addItem(f"{animal[1]} (ID: {animal[0]})", animal[0])
        conn.close()

    def register_adoption(self):
        adopter_id = self.adopter_combo.currentData()
        animal_id = self.animal_combo.currentData()
        date = self.date_input.date().toString("yyyy-MM-dd")
        status = self.status_input.currentText()

        # Validação dos dados
        if adopter_id is None:
            QMessageBox.warning(self, "Erro", "Por favor, selecione um adotante.")
            return
        if animal_id is None:
            QMessageBox.warning(self, "Erro", "Por favor, selecione um animal.")
            return

        conn = create_connection()
        cursor = conn.cursor()

        # Verificar se o animal já está adotado
        cursor.execute('SELECT status FROM animals WHERE id = ?', (animal_id,))
        animal_status = cursor.fetchone()[0]
        if animal_status == 'Adotado':
            QMessageBox.warning(self, "Erro", "Este animal já foi adotado.")
            conn.close()
            return

        # Inserir a adoção
        cursor.execute('''
            INSERT INTO adoptions (adopter_id, animal_id, date, status)
            VALUES (?, ?, ?, ?)
        ''', (adopter_id, animal_id, date, status))

        # Atualizar o status do animal para 'Adotado'
        cursor.execute('''
            UPDATE animals SET status = 'Adotado' WHERE id = ?
        ''', (animal_id,))

        conn.commit()
        conn.close()

        # Voltar para a tela da tabela e atualizar os dados
        self.stacked_layout.setCurrentWidget(self.table_widget)
        self.load_data()
     
    def delete_adoption(self, adoption_id, animal_id):
        reply = QMessageBox.question(
            self, 'Confirmação', 'Tem certeza que deseja deletar esta adoção?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            conn = create_connection()
            cursor = conn.cursor()

            # Deletar a adoção
            cursor.execute('DELETE FROM adoptions WHERE id = ?', (adoption_id,))

            # Atualizar o status do animal para 'Disponível'
            cursor.execute("UPDATE animals SET status = 'Disponível' WHERE id = ?", (animal_id,))

            conn.commit()
            conn.close()
            self.load_data()


    def edit_adoption(self, adoption_id):
        # Carregar dados da adoção
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT adoptions.id, adoptions.adopter_id, adoptions.animal_id, adoptions.date, adoptions.status
            FROM adoptions
            WHERE adoptions.id = ?
        ''', (adoption_id,))
        record = cursor.fetchone()
        conn.close()

        if record:
            self.edit_adoption_id = record[0]
            adopter_id = record[1]
            animal_id = record[2]
            date = record[3]
            status = record[4]

            # Limpar e recarregar os combos
            self.edit_adopter_combo.clear()
            self.edit_animal_combo.clear()
            self.load_edit_adopters()
            self.load_edit_animals()

            # Inserir opção vazia no início
            self.edit_adopter_combo.insertItem(0, "", None)
            self.edit_animal_combo.insertItem(0, "", None)

            # Selecionar o adotante atual
            index = self.edit_adopter_combo.findData(adopter_id)
            if index != -1:
                self.edit_adopter_combo.setCurrentIndex(index)
            else:
                self.edit_adopter_combo.setCurrentIndex(0)

            # Selecionar o animal atual
            index = self.edit_animal_combo.findData(animal_id)
            if index != -1:
                self.edit_animal_combo.setCurrentIndex(index)
            else:
                self.edit_animal_combo.setCurrentIndex(0)

            # Data
            self.edit_date_input.setDate(datetime.strptime(date, "%Y-%m-%d"))

            # Status
            index = self.edit_status_input.findText(status)
            if index != -1:
                self.edit_status_input.setCurrentIndex(index)
            else:
                self.edit_status_input.setCurrentIndex(0)

            # Alterar para a tela do formulário de edição
            self.stacked_layout.setCurrentWidget(self.edit_form_widget)
        else:
            QMessageBox.warning(self, "Erro", "Adoção não encontrada.")

    def load_edit_adopters(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM adopters')
        adopters = cursor.fetchall()
        for adopter in adopters:
            self.edit_adopter_combo.addItem(f"{adopter[1]} (ID: {adopter[0]})", adopter[0])
        conn.close()

    def load_edit_animals(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM animals')
        animals = cursor.fetchall()
        for animal in animals:
            self.edit_animal_combo.addItem(f"{animal[1]} (ID: {animal[0]})", animal[0])
        conn.close()

    def initEditFormUI(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        # ID da adoção
        self.edit_adoption_id = None

        # Seleção do Adotante
        self.edit_adopter_combo = QComboBox()
        form_layout.addRow("Selecionar Adotante:", self.edit_adopter_combo)

        # Seleção do Animal
        self.edit_animal_combo = QComboBox()
        form_layout.addRow("Selecionar Animal:", self.edit_animal_combo)

        # Data da Adoção
        self.edit_date_input = QDateEdit()
        self.edit_date_input.setDate(datetime.now())
        form_layout.addRow("Data da Adoção:", self.edit_date_input)

        # Status
        self.edit_status_input = QComboBox()
        self.edit_status_input.addItems(["Pendente", "Concluída", "Cancelada"])
        form_layout.addRow("Status:", self.edit_status_input)

        layout.addLayout(form_layout)

        # Botões de Ação
        button_layout = QHBoxLayout()
        self.update_button = QPushButton("Salvar Alterações")
        self.update_button.clicked.connect(self.update_adoption)
        self.cancel_edit_button = QPushButton("Cancelar")
        self.cancel_edit_button.clicked.connect(self.cancel_form)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.cancel_edit_button)

        layout.addLayout(button_layout)

        self.edit_form_widget.setLayout(layout)

    def update_adoption(self):
        adopter_id = self.edit_adopter_combo.currentData()
        animal_id = self.edit_animal_combo.currentData()
        date = self.edit_date_input.date().toString("yyyy-MM-dd")
        status = self.edit_status_input.currentText()

        # Validação dos dados
        if adopter_id is None:
            QMessageBox.warning(self, "Erro", "Por favor, selecione um adotante.")
            return
        if animal_id is None:
            QMessageBox.warning(self, "Erro", "Por favor, selecione um animal.")
            return

        conn = create_connection()
        cursor = conn.cursor()

        # Obter o animal_id atual da adoção
        cursor.execute('SELECT animal_id FROM adoptions WHERE id = ?', (self.edit_adoption_id,))
        old_animal_id = cursor.fetchone()[0]

        # Se o animal foi alterado, precisamos atualizar o status dos animais
        if animal_id != old_animal_id:
            # Verificar se o novo animal já está adotado
            cursor.execute('SELECT status FROM animals WHERE id = ?', (animal_id,))
            animal_status = cursor.fetchone()[0]
            if animal_status == 'Adotado':
                QMessageBox.warning(self, "Erro", "O novo animal selecionado já foi adotado.")
                conn.close()
                return

            # Atualizar status do antigo animal para 'Disponível'
            cursor.execute("UPDATE animals SET status = 'Disponível' WHERE id = ?", (old_animal_id,))

            # Atualizar status do novo animal para 'Adotado'
            cursor.execute("UPDATE animals SET status = 'Adotado' WHERE id = ?", (animal_id,))

        # Atualizar a adoção
        cursor.execute('''
            UPDATE adoptions
            SET adopter_id = ?, animal_id = ?, date = ?, status = ?
            WHERE id = ?
        ''', (adopter_id, animal_id, date, status, self.edit_adoption_id))

        conn.commit()
        conn.close()

        # Voltar para a tela da tabela e atualizar os dados
        self.stacked_layout.setCurrentWidget(self.table_widget)
        self.load_data()
