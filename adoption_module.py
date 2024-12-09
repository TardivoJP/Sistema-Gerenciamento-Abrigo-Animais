from base_list_widget import BaseListWidget
from PyQt6.QtWidgets import QLineEdit, QDateEdit, QComboBox, QMessageBox, QPushButton, QCompleter
from PyQt6.QtCore import Qt
from datetime import datetime
from database import create_connection

class AdoptionListWidget(BaseListWidget):
    def __init__(self):
        self.column_mapping_local = {
            0: "adoptions.id"
        }
        super().__init__()
        self.order_by_column = "adoptions.id"  

        self.adopter_dict = {}
        self.animal_dict = {}

    def get_title(self):
        return "Lista de Adoções"

    def get_new_button_text(self):
        return "Nova Adoção"

    def get_table_headers(self):
        return ["ID", "Adotante", "Animal", "Data", "Status", "", ""]

    def init_search_fields(self):
        self.search_field_combo.addItem("ID", "adoptions.id")
        self.search_field_combo.addItem("Adotante", "adopters.name")
        self.search_field_combo.addItem("Animal", "animals.name")
        self.search_field_combo.addItem("Status", "adoptions.status")
        self.search_field_combo.addItem("Data", "adoptions.date")

    def get_column_mapping(self):
        return {
            0: "adoptions.id",
            1: "adopters.name",
            2: "animals.name",
            3: "adoptions.date",
            4: "adoptions.status"
        }

    def build_record_query(self, count_only=False):
        base = "SELECT "
        if count_only:
            base += "COUNT(*)"
        else:
            base += "adoptions.id, adopters.name, animals.name, adoptions.date, adoptions.status, animals.id"
        base += " FROM adoptions"
        base += " JOIN adopters ON adoptions.adopter_id = adopters.id"
        base += " JOIN animals ON adoptions.animal_id = animals.id"

        conditions = []
        if self.filter_field and self.filter_value:
            field = self.filter_field
            value = self.filter_value
            if field == "adoptions.id":
                if value.isdigit():
                    conditions.append("adoptions.id = {}".format(int(value)))
                else:
                    conditions.append("CAST(adoptions.id AS TEXT) LIKE '%{}%'".format(value))
            elif field == "adoptions.status":
                conditions.append("adoptions.status LIKE '%{}%'".format(value))
            elif field == "adoptions.date":
                conditions.append("adoptions.date LIKE '%{}%'".format(value))
            elif field == "adopters.name":
                conditions.append("adopters.name LIKE '%{}%'".format(value))
            elif field == "animals.name":
                conditions.append("animals.name LIKE '%{}%'".format(value))

        if conditions:
            base += " WHERE " + " AND ".join(conditions)

        if not count_only:
            if self.order_by_column is None:
                self.order_by_column = "adoptions.id"
            base += f" ORDER BY {self.order_by_column} {self.order_direction}"
            base += f" LIMIT {self.page_size} OFFSET {self.current_page * self.page_size}"

        return base

    def add_actions_to_row(self, row_idx, row_data):
        adoption_id = row_data[0]
        animal_id = row_data[5]

        edit_button = QPushButton("Editar")
        edit_button.clicked.connect(lambda checked, aid=adoption_id: self.edit_record(aid))
        self.table.setCellWidget(row_idx, 5, edit_button)

        delete_button = QPushButton("Deletar")
        delete_button.clicked.connect(lambda checked, aid=adoption_id, anid=animal_id: self.delete_action(aid, anid))
        self.table.setCellWidget(row_idx, 6, delete_button)

    def delete_action(self, adoption_id, animal_id):
        reply = QMessageBox.question(
            self, 'Confirmação', 'Tem certeza que deseja deletar esta adoção?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.delete_record((adoption_id, animal_id))
            self.load_data()

    def initFormFields(self, form_layout):
        self.adopter_input = QLineEdit()
        self.animal_input = QLineEdit()

        # Campos adicionais de info
        self.adopter_info = QLineEdit()
        self.adopter_info.setReadOnly(True)
        self.adopter_info.setStyleSheet("color: grey;")

        self.animal_info = QLineEdit()
        self.animal_info.setReadOnly(True)
        self.animal_info.setStyleSheet("color: grey;")

        form_layout.addRow("Selecionar Adotante:", self.adopter_input)
        form_layout.addRow("Info Adotante:", self.adopter_info)
        form_layout.addRow("Selecionar Animal:", self.animal_input)
        form_layout.addRow("Info Animal:", self.animal_info)

        self.date_input = QDateEdit()
        self.date_input.setDate(datetime.now())
        form_layout.addRow("Data da Adoção:", self.date_input)

        self.status_input = QComboBox()
        self.status_input.addItems(["Pendente", "Concluída", "Cancelada"])
        form_layout.addRow("Status:", self.status_input)

        # Sinais para atualizar infos ao terminar de editar
        self.adopter_input.editingFinished.connect(self.update_adopter_info)
        self.animal_input.editingFinished.connect(self.update_animal_info)

    def initEditFormFields(self, form_layout):
        self.edit_adopter_input = QLineEdit()
        self.edit_animal_input = QLineEdit()

        self.edit_adopter_info = QLineEdit()
        self.edit_adopter_info.setReadOnly(True)
        self.edit_adopter_info.setStyleSheet("color: grey;")

        self.edit_animal_info = QLineEdit()
        self.edit_animal_info.setReadOnly(True)
        self.edit_animal_info.setStyleSheet("color: grey;")

        form_layout.addRow("Selecionar Adotante:", self.edit_adopter_input)
        form_layout.addRow("Info Adotante:", self.edit_adopter_info)
        form_layout.addRow("Selecionar Animal:", self.edit_animal_input)
        form_layout.addRow("Info Animal:", self.edit_animal_info)

        self.edit_date_input = QDateEdit()
        self.edit_date_input.setDate(datetime.now())
        form_layout.addRow("Data da Adoção:", self.edit_date_input)

        self.edit_status_input = QComboBox()
        self.edit_status_input.addItems(["Pendente", "Concluída", "Cancelada"])
        form_layout.addRow("Status:", self.edit_status_input)

        self.edit_adopter_input.editingFinished.connect(self.update_adopter_info_edit)
        self.edit_animal_input.editingFinished.connect(self.update_animal_info_edit)

    def load_adopters_list(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, address, phone FROM adopters')
        adopters = cursor.fetchall()
        conn.close()
        self.adopter_dict.clear()
        items = []
        # Agora armazenamos não só o ID, mas também infos extras
        # { "Pedro (ID:10)": (10, "Endereço...", "Telefone...") }
        self.adopter_full_info = {}
        for (aid, name, address, phone) in adopters:
            key = f"{name} (ID:{aid})"
            self.adopter_dict[key] = aid
            self.adopter_full_info[key] = (aid, address, phone)
            items.append(key)
        return items

    def load_animals_list(self):
        conn = create_connection()
        cursor = conn.cursor()
        # Excluir animais adotados
        cursor.execute('SELECT id, name, type, breed, status FROM animals WHERE status != "Adotado"')
        animals = cursor.fetchall()
        conn.close()
        self.animal_dict.clear()
        self.animal_full_info = {}
        items = []
        for (anid, name, atype, breed, status) in animals:
            key = f"{name} (ID:{anid})"
            self.animal_dict[key] = anid
            # Guardar tipo e raça
            self.animal_full_info[key] = (anid, atype, breed, status)
            items.append(key)
        return items

    def setup_completer(self, line_edit, items):
        completer = QCompleter(items, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        line_edit.setCompleter(completer)

    def clear_form(self):
        adopters_list = self.load_adopters_list()
        animals_list = self.load_animals_list()

        self.adopter_input.clear()
        self.animal_input.clear()
        self.adopter_info.clear()
        self.animal_info.clear()

        self.setup_completer(self.adopter_input, adopters_list)
        self.setup_completer(self.animal_input, animals_list)

        self.date_input.setDate(datetime.now())
        self.status_input.setCurrentIndex(0)

    def clear_edit_form(self):
        adopters_list = self.load_adopters_list()
        animals_list = self.load_animals_list()

        self.edit_adopter_input.clear()
        self.edit_animal_input.clear()
        self.edit_adopter_info.clear()
        self.edit_animal_info.clear()

        self.setup_completer(self.edit_adopter_input, adopters_list)
        self.setup_completer(self.edit_animal_input, animals_list)

        self.edit_date_input.setDate(datetime.now())
        self.edit_status_input.setCurrentIndex(0)

    def collect_form_data(self):
        data = {
            "adopter_key": self.adopter_input.text().strip(),
            "animal_key": self.animal_input.text().strip(),
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "status": self.status_input.currentText()
        }
        return data

    def collect_edit_form_data(self):
        data = {
            "adopter_key": self.edit_adopter_input.text().strip(),
            "animal_key": self.edit_animal_input.text().strip(),
            "date": self.edit_date_input.date().toString("yyyy-MM-dd"),
            "status": self.edit_status_input.currentText()
        }
        return data

    def validate_data(self, data):
        if data["adopter_key"] not in self.adopter_dict:
            return False, "Por favor, selecione um adotante válido (use a busca para selecionar)."
        if data["animal_key"] not in self.animal_dict:
            return False, "Por favor, selecione um animal válido (use a busca para selecionar)."
        return True, ""

    def save_record(self, data):
        adopter_id = self.adopter_dict[data["adopter_key"]]
        animal_id = self.animal_dict[data["animal_key"]]
        date = data["date"]
        status = data["status"]

        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT status FROM animals WHERE id = ?', (animal_id,))
        animal_status = cursor.fetchone()[0]
        if animal_status == 'Adotado':
            conn.close()
            raise ValueError("Este animal já foi adotado.")

        cursor.execute('''
            INSERT INTO adoptions (adopter_id, animal_id, date, status)
            VALUES (?, ?, ?, ?)
        ''', (adopter_id, animal_id, date, status))

        cursor.execute("UPDATE animals SET status = 'Adotado' WHERE id = ?", (animal_id,))

        conn.commit()
        conn.close()

    def update_record(self, record_id, data):
        adopter_id = self.adopter_dict[data["adopter_key"]]
        animal_id = self.animal_dict[data["animal_key"]]
        date = data["date"]
        status = data["status"]

        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT animal_id FROM adoptions WHERE id = ?', (record_id,))
        old_animal_id = cursor.fetchone()[0]

        if animal_id != old_animal_id:
            cursor.execute('SELECT status FROM animals WHERE id = ?', (animal_id,))
            animal_status = cursor.fetchone()[0]
            if animal_status == 'Adotado':
                conn.close()
                raise ValueError("O novo animal selecionado já foi adotado.")

            cursor.execute("UPDATE animals SET status = 'Disponível' WHERE id = ?", (old_animal_id,))
            cursor.execute("UPDATE animals SET status = 'Adotado' WHERE id = ?", (animal_id,))

        cursor.execute('''
            UPDATE adoptions
            SET adopter_id = ?, animal_id = ?, date = ?, status = ?
            WHERE id = ?
        ''', (adopter_id, animal_id, date, status, record_id))

        conn.commit()
        conn.close()

    def delete_record(self, record_id):
        adoption_id, animal_id = record_id
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM adoptions WHERE id = ?', (adoption_id,))
        cursor.execute("UPDATE animals SET status = 'Disponível' WHERE id = ?", (animal_id,))
        conn.commit()
        conn.close()

    def load_record(self, record_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT adoptions.id, adoptions.adopter_id, adoptions.animal_id, adoptions.date, adoptions.status
            FROM adoptions
            WHERE adoptions.id = ?
        ''', (record_id,))
        record = cursor.fetchone()
        conn.close()
        return record

    def fill_edit_form(self, record):
        self.edit_id = record[0]
        adopter_id = record[1]
        animal_id = record[2]
        date = record[3]
        status = record[4]

        adopters_list = self.load_adopters_list()
        animals_list = self.load_animals_list()
        self.setup_completer(self.edit_adopter_input, adopters_list)
        self.setup_completer(self.edit_animal_input, animals_list)

        adopter_key = None
        for k, v in self.adopter_dict.items():
            if v == adopter_id:
                adopter_key = k
                break

        animal_key = None
        for k, v in self.animal_dict.items():
            if v == animal_id:
                animal_key = k
                break

        if adopter_key is not None:
            self.edit_adopter_input.setText(adopter_key)
        else:
            self.edit_adopter_input.clear()

        if animal_key is not None:
            self.edit_animal_input.setText(animal_key)
        else:
            self.edit_animal_input.clear()

        self.edit_date_input.setDate(datetime.strptime(date, "%Y-%m-%d"))

        index = self.edit_status_input.findText(status)
        if index != -1:
            self.edit_status_input.setCurrentIndex(index)
        else:
            self.edit_status_input.setCurrentIndex(0)

        # Atualizar infos extras após preencher o form
        self.update_adopter_info_edit()
        self.update_animal_info_edit()

    def update_adopter_info(self):
        key = self.adopter_input.text().strip()
        if key in self.adopter_full_info:
            aid, address, phone = self.adopter_full_info[key]
            self.adopter_info.setText(f"Endereço: {address}, Telefone: {phone}")
        else:
            self.adopter_info.clear()

    def update_animal_info(self):
        key = self.animal_input.text().strip()
        if key in self.animal_full_info:
            anid, atype, breed, status = self.animal_full_info[key]
            self.animal_info.setText(f"Tipo: {atype}, Raça: {breed}, Status: {status}")
        else:
            self.animal_info.clear()

    def update_adopter_info_edit(self):
        key = self.edit_adopter_input.text().strip()
        if key in self.adopter_full_info:
            aid, address, phone = self.adopter_full_info[key]
            self.edit_adopter_info.setText(f"Endereço: {address}, Telefone: {phone}")
        else:
            self.edit_adopter_info.clear()

    def update_animal_info_edit(self):
        key = self.edit_animal_input.text().strip()
        if key in self.animal_full_info:
            anid, atype, breed, status = self.animal_full_info[key]
            self.edit_animal_info.setText(f"Tipo: {atype}, Raça: {breed}, Status: {status}")
        else:
            self.edit_animal_info.clear()
