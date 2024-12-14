from math import ceil
from base_list_widget import BaseListWidget
from PyQt6.QtWidgets import QLineEdit, QCheckBox, QTextEdit, QComboBox, QPushButton, QMessageBox, QWidget, QVBoxLayout, QFormLayout, QTableWidgetItem
from PyQt6.QtCore import Qt
from datetime import datetime
from database import create_connection

class AnimalListWidget(BaseListWidget):
    def __init__(self):
        self.column_mapping_local = {
            0: "animals.id",
            1: "animals.name",
            2: "animals.type",
            3: "animals.breed",
            4: "animals.vaccinated",
            5: "animals.neutered",
            6: "animals.status",
            7: "animals.created_at"
        }
        super().__init__()
        self.order_by_column = "animals.id"
        self.initDetailsUI()

    def get_title(self):
        return "Lista de Animais"

    def get_new_button_text(self):
        return "Novo Cadastro"

    def get_table_headers(self):
        # Agora temos "Criado em" e 3 colunas de ação: Detalhes, Editar, Deletar
        return ["ID", "Nome", "Tipo", "Raça", "Vacinado", "Castrado", "Status", "Criado em", "Detalhes", "Editar", "Deletar"]

    def get_column_mapping(self):
        return self.column_mapping_local

    def init_search_fields(self):
        self.search_field_combo.addItem("ID", "animals.id")
        self.search_field_combo.addItem("Nome", "animals.name")
        self.search_field_combo.addItem("Tipo", "animals.type")
        self.search_field_combo.addItem("Raça", "animals.breed")
        self.search_field_combo.addItem("Status", "animals.status")

    def build_record_query(self, count_only=False):
        base = "SELECT "
        if count_only:
            base += "COUNT(*)"
        else:
            base += "animals.id, animals.name, animals.type, animals.breed, animals.vaccinated, animals.neutered, animals.status, animals.created_at"
        base += " FROM animals"

        conditions = []
        if self.filter_field and self.filter_value:
            field = self.filter_field
            value = self.filter_value
            if field == "animals.id":
                if value.isdigit():
                    conditions.append("animals.id = {}".format(int(value)))
                else:
                    conditions.append("CAST(animals.id AS TEXT) LIKE '%{}%'".format(value))
            else:
                conditions.append(f"{field} LIKE '%{value}%'")

        if conditions:
            base += " WHERE " + " AND ".join(conditions)

        if not count_only:
            if self.order_by_column is None:
                self.order_by_column = "animals.id"
            base += f" ORDER BY {self.order_by_column} {self.order_direction}"
            base += f" LIMIT {self.page_size} OFFSET {self.current_page * self.page_size}"

        return base

    def load_data(self):
        conn = create_connection()
        cursor = conn.cursor()

        # Consulta para contar o total de registros
        count_query = self.build_record_query(count_only=True)
        cursor.execute(count_query)
        total_records = cursor.fetchone()[0]

        if total_records == 0:
            self.total_pages = 0
        else:
            self.total_pages = ceil(total_records / self.page_size)

        if self.total_pages == 0:
            # Sem registros
            self.table.setRowCount(0)
            self.update_pagination_bar()
            self.update_current_page_label()
            conn.close()
            return

        if self.current_page >= self.total_pages:
            self.current_page = self.total_pages - 1

        # Consulta para obter os registros da página atual
        query = self.build_record_query(count_only=False)
        cursor.execute(query)
        records = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(records))
        for row_idx, row_data in enumerate(records):
            # Convertendo vacinado/castrado para "Sim/Não"
            row_list = list(row_data)
            row_list[4] = "Sim" if row_data[4] else "Não"
            row_list[5] = "Sim" if row_data[5] else "Não"

            for col_idx, value in enumerate(row_list):
                if col_idx < 8:  # Apenas as colunas de dados, antes dos botões
                    item = QTableWidgetItem(str(value))
                    if col_idx == 0:
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row_idx, col_idx, item)

            # Adiciona os botões de ação
            self.add_actions_to_row(row_idx, row_list)

        self.update_pagination_bar()
        self.update_current_page_label()

    def add_actions_to_row(self, row_idx, row_data):
        # row_data agora já é transformado, com row_data[0] = id do animal
        animal_id = row_data[0]
        animal_status = row_data[6]  # status está no index 6

        details_button = QPushButton("Detalhes")
        details_button.clicked.connect(lambda checked, aid=animal_id: self.show_details(aid))
        self.table.setCellWidget(row_idx, 8, details_button)

        edit_button = QPushButton("Editar")
        edit_button.clicked.connect(lambda checked, aid=animal_id: self.edit_record(aid))
        self.table.setCellWidget(row_idx, 9, edit_button)

        delete_button = QPushButton("Deletar")
        delete_button.clicked.connect(lambda checked, aid=animal_id: self.delete_action(aid))
        self.table.setCellWidget(row_idx, 10, delete_button)

        if animal_status == 'Adotado':
            edit_button.setEnabled(False)
            delete_button.setEnabled(False)

    def delete_action(self, record_id):
        reply = QMessageBox.question(
            self, 'Confirmação', 'Tem certeza que deseja deletar este animal?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.delete_record(record_id)
            self.load_data()

    def initFormFields(self, form_layout):
        self.name_input = QLineEdit()
        form_layout.addRow("Nome:", self.name_input)

        self.type_input = QComboBox()
        self.type_input.addItem("")
        self.type_input.addItem("Cachorro")
        self.type_input.addItem("Gato")
        form_layout.addRow("Tipo:", self.type_input)

        self.breed_input = QLineEdit()
        form_layout.addRow("Raça:", self.breed_input)

        self.vaccinated_input = QCheckBox("Vacinado")
        form_layout.addRow(self.vaccinated_input)

        self.neutered_input = QCheckBox("Castrado")
        form_layout.addRow(self.neutered_input)

        self.description_input = QTextEdit()
        form_layout.addRow("Descrição:", self.description_input)

    def initEditFormFields(self, form_layout):
        self.edit_name_input = QLineEdit()
        form_layout.addRow("Nome:", self.edit_name_input)

        self.edit_type_input = QComboBox()
        self.edit_type_input.addItem("")
        self.edit_type_input.addItem("Cachorro")
        self.edit_type_input.addItem("Gato")
        form_layout.addRow("Tipo:", self.edit_type_input)

        self.edit_breed_input = QLineEdit()
        form_layout.addRow("Raça:", self.edit_breed_input)

        self.edit_vaccinated_input = QCheckBox("Vacinado")
        form_layout.addRow(self.edit_vaccinated_input)

        self.edit_neutered_input = QCheckBox("Castrado")
        form_layout.addRow(self.edit_neutered_input)

        self.edit_description_input = QTextEdit()
        form_layout.addRow("Descrição:", self.edit_description_input)

    def clear_form(self):
        self.name_input.clear()
        self.type_input.setCurrentIndex(0)
        self.breed_input.clear()
        self.vaccinated_input.setChecked(False)
        self.neutered_input.setChecked(False)
        self.description_input.clear()

    def clear_edit_form(self):
        self.edit_name_input.clear()
        self.edit_type_input.setCurrentIndex(0)
        self.edit_breed_input.clear()
        self.edit_vaccinated_input.setChecked(False)
        self.edit_neutered_input.setChecked(False)
        self.edit_description_input.clear()

    def collect_form_data(self):
        data = {
            "name": self.name_input.text().strip(),
            "type": self.type_input.currentText().strip(),
            "breed": self.breed_input.text().strip(),
            "vaccinated": self.vaccinated_input.isChecked(),
            "neutered": self.neutered_input.isChecked(),
            "description": self.description_input.toPlainText().strip()
        }
        return data

    def collect_edit_form_data(self):
        data = {
            "name": self.edit_name_input.text().strip(),
            "type": self.edit_type_input.currentText().strip(),
            "breed": self.edit_breed_input.text().strip(),
            "vaccinated": self.edit_vaccinated_input.isChecked(),
            "neutered": self.edit_neutered_input.isChecked(),
            "description": self.edit_description_input.toPlainText().strip()
        }
        return data

    def validate_data(self, data):
        if not data["name"] or not data["type"]:
            return False, "Por favor, preencha os campos obrigatórios: Nome e Tipo."
        if not data["breed"]:
            return False, "Por favor, preencha o campo: Raça."
        return True, ""

    def save_record(self, data):
        valid, msg = self.validate_data(data)
        if not valid:
            QMessageBox.warning(self, "Erro", msg)
            return

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO animals (name, type, breed, vaccinated, neutered, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (data["name"], data["type"], data["breed"], int(data["vaccinated"]), int(data["neutered"]), data["description"], created_at))
        conn.commit()
        conn.close()

        self.load_data()
        self.stacked_layout.setCurrentWidget(self.table_widget)

    def update_record(self, record_id, data):
        valid, msg = self.validate_data(data)
        if not valid:
            QMessageBox.warning(self, "Erro", msg)
            return

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE animals
            SET name = ?, type = ?, breed = ?, vaccinated = ?, neutered = ?, description = ?
            WHERE id = ?
        ''', (data["name"], data["type"], data["breed"], int(data["vaccinated"]), int(data["neutered"]), data["description"], record_id))
        conn.commit()
        conn.close()

        self.load_data()
        self.stacked_layout.setCurrentWidget(self.table_widget)

    def delete_record(self, record_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM animals WHERE id = ?', (record_id,))
        conn.commit()
        conn.close()

    def load_record(self, record_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM animals WHERE id = ?', (record_id,))
        record = cursor.fetchone()
        conn.close()
        return record

    def fill_edit_form(self, record):
        # record: [id, name, type, breed, vaccinated, neutered, description, status, created_at]
        self.edit_id = record[0]
        self.edit_name_input.setText(record[1])
        index = self.edit_type_input.findText(record[2])
        if index < 0:
            index = 0
        self.edit_type_input.setCurrentIndex(index)
        self.edit_breed_input.setText(record[3])
        self.edit_vaccinated_input.setChecked(bool(record[4]))
        self.edit_neutered_input.setChecked(bool(record[5]))
        self.edit_description_input.setPlainText(record[6])

        self.stacked_layout.setCurrentWidget(self.edit_form_widget)

    def initDetailsUI(self):
        self.details_widget = QWidget()
        details_layout = QVBoxLayout()
        self.details_form = QFormLayout()

        self.details_name = QLineEdit(); self.details_name.setReadOnly(True)
        self.details_form.addRow("Nome:", self.details_name)

        self.details_type = QLineEdit(); self.details_type.setReadOnly(True)
        self.details_form.addRow("Tipo:", self.details_type)

        self.details_breed = QLineEdit(); self.details_breed.setReadOnly(True)
        self.details_form.addRow("Raça:", self.details_breed)

        self.details_vaccinated = QLineEdit(); self.details_vaccinated.setReadOnly(True)
        self.details_form.addRow("Vacinado:", self.details_vaccinated)

        self.details_neutered = QLineEdit(); self.details_neutered.setReadOnly(True)
        self.details_form.addRow("Castrado:", self.details_neutered)

        self.details_status = QLineEdit(); self.details_status.setReadOnly(True)
        self.details_form.addRow("Status:", self.details_status)

        self.details_created_at = QLineEdit(); self.details_created_at.setReadOnly(True)
        self.details_form.addRow("Criado em:", self.details_created_at)

        self.details_description = QTextEdit(); self.details_description.setReadOnly(True)
        self.details_form.addRow("Descrição:", self.details_description)

        details_layout.addLayout(self.details_form)

        close_button = QPushButton("Fechar")
        close_button.clicked.connect(lambda: self.stacked_layout.setCurrentWidget(self.table_widget))
        details_layout.addWidget(close_button)

        self.details_widget.setLayout(details_layout)
        self.stacked_layout.addWidget(self.details_widget)

    def show_details(self, record_id):
        record = self.load_record(record_id)
        if not record:
            QMessageBox.warning(self, "Erro", "Animal não encontrado.")
            return

        # record: id, name, type, breed, vaccinated, neutered, description, status, created_at
        self.details_name.setText(record[1] if record[1] else "")
        self.details_type.setText(record[2] if record[2] else "")
        self.details_breed.setText(record[3] if record[3] else "")
        self.details_vaccinated.setText("Sim" if record[4] else "Não")
        self.details_neutered.setText("Sim" if record[5] else "Não")
        self.details_status.setText(record[7] if record[7] else "")
        self.details_created_at.setText(record[8] if record[8] else "")
        self.details_description.setPlainText(record[6] if record[6] else "")

        self.stacked_layout.setCurrentWidget(self.details_widget)