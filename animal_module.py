from base_list_widget import BaseListWidget
from PyQt6.QtWidgets import QLineEdit, QCheckBox, QTextEdit, QComboBox, QPushButton, QMessageBox
from database import create_connection

class AnimalListWidget(BaseListWidget):
    def __init__(self):
        self.column_mapping_local = {
            0: "id",
            1: "name",
            2: "type",
            3: "breed",
            4: "vaccinated",
            5: "neutered",
            6: "status"
        }
        super().__init__()
        self.order_by_column = "id"  # Definido após super().__init__

    def get_title(self):
        return "Lista de Animais"

    def get_new_button_text(self):
        return "Novo Cadastro"

    def get_table_headers(self):
        return ["ID", "Nome", "Tipo", "Raça", "Vacinado", "Castrado", "Status", "", ""]

    def get_column_mapping(self):
        return self.column_mapping_local

    def init_search_fields(self):
        # Campos para filtrar: ID, Nome, Tipo, Raça, Status
        self.search_field_combo.addItem("ID", "id")
        self.search_field_combo.addItem("Nome", "name")
        self.search_field_combo.addItem("Tipo", "type")
        self.search_field_combo.addItem("Raça", "breed")
        self.search_field_combo.addItem("Status", "status")

    def build_record_query(self, count_only=False):
        base = "SELECT "
        if count_only:
            base += "COUNT(*)"
        else:
            base += "id, name, type, breed, vaccinated, neutered, status"
        base += " FROM animals"

        conditions = []
        if self.filter_field and self.filter_value:
            field = self.filter_field
            value = self.filter_value
            if field == "id":
                if value.isdigit():
                    conditions.append("id = {}".format(int(value)))
                else:
                    conditions.append("CAST(id AS TEXT) LIKE '%{}%'".format(value))
            else:
                conditions.append("{} LIKE '%{}%'".format(field, value))

        if conditions:
            base += " WHERE " + " AND ".join(conditions)

        if not count_only:
            if self.order_by_column is None:
                self.order_by_column = "id"
            base += f" ORDER BY {self.order_by_column} {self.order_direction}"
            base += f" LIMIT {self.page_size} OFFSET {self.current_page * self.page_size}"

        return base

    def add_actions_to_row(self, row_idx, row_data):
        animal_id = row_data[0]
        animal_status = row_data[6]

        edit_button = QPushButton("Editar")
        edit_button.clicked.connect(lambda checked, aid=animal_id: self.edit_record(aid))
        self.table.setCellWidget(row_idx, 7, edit_button)

        delete_button = QPushButton("Deletar")
        delete_button.clicked.connect(lambda checked, aid=animal_id: self.delete_action(aid))
        self.table.setCellWidget(row_idx, 8, delete_button)

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
        # Mesmos campos do formulário normal
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
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO animals (name, type, breed, vaccinated, neutered, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data["name"], data["type"], data["breed"], int(data["vaccinated"]), int(data["neutered"]), data["description"]))
        conn.commit()
        conn.close()

    def update_record(self, record_id, data):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE animals
            SET name = ?, type = ?, breed = ?, vaccinated = ?, neutered = ?, description = ?
            WHERE id = ?
        ''', (data["name"], data["type"], data["breed"], int(data["vaccinated"]), int(data["neutered"]), data["description"], record_id))
        conn.commit()
        conn.close()

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


