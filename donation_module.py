from base_list_widget import BaseListWidget
from PyQt6.QtWidgets import (
    QLineEdit, QPushButton, QDateEdit, QCompleter, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator
from datetime import datetime
from database import create_connection

class DonationsListWidget(BaseListWidget):
    def __init__(self):
        super().__init__()
        self.order_by_column = "donations.id"
        self.volunteer_dict = {}
        self.volunteer_full_info = {}

    def get_title(self):
        return "Lista de Doações"

    def get_new_button_text(self):
        return "Nova Doação"

    def get_table_headers(self):
        return ["ID", "Voluntário", "Data", "Valor", ""]

    def init_search_fields(self):
        self.search_field_combo.addItem("ID", "donations.id")
        self.search_field_combo.addItem("Voluntário", "volunteers.name")
        self.search_field_combo.addItem("Data", "donations.date")
        self.search_field_combo.addItem("Valor", "donations.amount")

    def get_column_mapping(self):
        return {
            0: "donations.id",
            1: "volunteers.name",
            2: "donations.date",
            3: "donations.amount"
        }

    def build_record_query(self, count_only=False):
        base = "SELECT "
        if count_only:
            base += "COUNT(*)"
        else:
            base += "donations.id, volunteers.name, donations.date, donations.amount, volunteers.id"
        base += " FROM donations JOIN volunteers ON donations.volunteer_id = volunteers.id"

        conditions = []
        if self.filter_field and self.filter_value:
            field = self.filter_field
            value = self.filter_value
            if field == "donations.id":
                if value.isdigit():
                    conditions.append("donations.id = {}".format(int(value)))
                else:
                    conditions.append("CAST(donations.id AS TEXT) LIKE '%{}%'".format(value))
            elif field == "volunteers.name":
                conditions.append("volunteers.name LIKE '%{}%'".format(value))
            elif field == "donations.date":
                conditions.append("donations.date LIKE '%{}%'".format(value))
            elif field == "donations.amount":
                # Filtrar por valor, se for um número exato ou range, aqui apenas LIKE
                # Se quisermos filtrar número exato, podemos tentar converter
                # Simplesmente usar LIKE por enquanto:
                conditions.append("CAST(donations.amount AS TEXT) LIKE '%{}%'".format(value))

        if conditions:
            base += " WHERE " + " AND ".join(conditions)

        if not count_only:
            if self.order_by_column is None:
                self.order_by_column = "donations.id"
            base += f" ORDER BY {self.order_by_column} {self.order_direction}"
            base += f" LIMIT {self.page_size} OFFSET {self.current_page * self.page_size}"

        return base

    def add_actions_to_row(self, row_idx, row_data):
        donation_id = row_data[0]

        # Botão de deletar
        delete_button = QPushButton("Deletar")
        delete_button.clicked.connect(lambda checked, did=donation_id: self.delete_action(did))
        self.table.setCellWidget(row_idx, 4, delete_button)

    def initFormFields(self, form_layout):
        # Campo do voluntário
        self.volunteer_input = QLineEdit()
        self.volunteer_info = QLineEdit()
        self.volunteer_info.setReadOnly(True)
        self.volunteer_info.setStyleSheet("color: grey;")

        form_layout.addRow("Selecionar Voluntário:", self.volunteer_input)
        form_layout.addRow("Info Voluntário:", self.volunteer_info)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(datetime.now())
        form_layout.addRow("Data da Doação:", self.date_input)

        self.amount_input = QLineEdit()
        # Validador para valor
        income_validator = QDoubleValidator(0.0, 9999999999.99, 2)
        income_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.amount_input.setValidator(income_validator)
        form_layout.addRow("Valor:", self.amount_input)

        self.volunteer_input.editingFinished.connect(self.update_volunteer_info)

    def initEditFormFields(self, form_layout):
        self.edit_donation_id = None

        self.edit_volunteer_input = QLineEdit()
        self.edit_volunteer_info = QLineEdit()
        self.edit_volunteer_info.setReadOnly(True)
        self.edit_volunteer_info.setStyleSheet("color: grey;")

        form_layout.addRow("Selecionar Voluntário:", self.edit_volunteer_input)
        form_layout.addRow("Info Voluntário:", self.edit_volunteer_info)

        self.edit_date_input = QDateEdit()
        self.edit_date_input.setCalendarPopup(True)
        self.edit_date_input.setDate(datetime.now())
        form_layout.addRow("Data da Doação:", self.edit_date_input)

        self.edit_amount_input = QLineEdit()
        income_validator = QDoubleValidator(0.0, 9999999999.99, 2)
        income_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.edit_amount_input.setValidator(income_validator)
        form_layout.addRow("Valor:", self.edit_amount_input)

        self.edit_volunteer_input.editingFinished.connect(self.update_volunteer_info_edit)

    def load_volunteers_list(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, address, phone, cpf, birth_date FROM volunteers')
        volunteers = cursor.fetchall()
        conn.close()
        self.volunteer_dict.clear()
        self.volunteer_full_info.clear()
        items = []
        for (vid, name, address, phone, cpf, birth_date) in volunteers:
            key = f"{name} (ID:{vid})"
            self.volunteer_dict[key] = vid
            # Guardar infos do voluntário
            # Mostrar endereço, telefone no info
            self.volunteer_full_info[key] = (vid, address, phone)
            items.append(key)
        return items

    def setup_completer(self, line_edit, items):
        completer = QCompleter(items, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        line_edit.setCompleter(completer)

    def clear_form(self):
        volunteers_list = self.load_volunteers_list()

        self.volunteer_input.clear()
        self.volunteer_info.clear()
        self.setup_completer(self.volunteer_input, volunteers_list)

        self.date_input.setDate(datetime.now())
        self.amount_input.clear()

    def clear_edit_form(self):
        volunteers_list = self.load_volunteers_list()

        self.edit_volunteer_input.clear()
        self.edit_volunteer_info.clear()
        self.setup_completer(self.edit_volunteer_input, volunteers_list)

        self.edit_date_input.setDate(datetime.now())
        self.edit_amount_input.clear()

    def collect_form_data(self):
        data = {
            "volunteer_key": self.volunteer_input.text().strip(),
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "amount": self.amount_input.text().strip()
        }
        return data

    def collect_edit_form_data(self):
        data = {
            "volunteer_key": self.edit_volunteer_input.text().strip(),
            "date": self.edit_date_input.date().toString("yyyy-MM-dd"),
            "amount": self.edit_amount_input.text().strip()
        }
        return data

    def validate_data(self, data):
        # Voluntário obrigatório
        if data["volunteer_key"] not in self.volunteer_dict:
            return False, "Por favor, selecione um voluntário válido (use a busca para selecionar)."

        # Valor obrigatório e numérico
        if not data["amount"]:
            return False, "Por favor, informe o valor da doação."
        try:
            float(data["amount"].replace(",", "."))
        except ValueError:
            return False, "Valor inválido."

        # Data obrigatória - já garantida pelo QDateEdit, mas caso queira verificar:
        # Aqui se o QDateEdit não permitir data vazia, tudo bem.
        # Se quiser, pode checar se a data é válida, mas QDateEdit garante isso.

        return True, ""

    def save_record(self, data):
        volunteer_id = self.volunteer_dict[data["volunteer_key"]]
        date = data["date"]
        amount = float(data["amount"].replace(",", "."))

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO donations (volunteer_id, date, amount)
            VALUES (?, ?, ?)
        ''', (volunteer_id, date, amount))
        conn.commit()
        conn.close()

    def update_record(self, record_id, data):
        volunteer_id = self.volunteer_dict[data["volunteer_key"]]
        date = data["date"]
        amount = float(data["amount"].replace(",", "."))

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE donations
            SET volunteer_id = ?, date = ?, amount = ?
            WHERE id = ?
        ''', (volunteer_id, date, amount, record_id))
        conn.commit()
        conn.close()

    def delete_record(self, record_id):
        # Aqui record_id é apenas doação_id
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM donations WHERE id = ?', (record_id,))
        conn.commit()
        conn.close()

    def load_record(self, record_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, volunteer_id, date, amount FROM donations WHERE id = ?
        ''', (record_id,))
        record = cursor.fetchone()
        conn.close()
        return record

    def fill_edit_form(self, record):
        self.edit_id = record[0]
        volunteer_id = record[1]
        date = record[2]
        amount = record[3]

        volunteers_list = self.load_volunteers_list()
        self.setup_completer(self.edit_volunteer_input, volunteers_list)

        volunteer_key = None
        for k, v in self.volunteer_dict.items():
            if v == volunteer_id:
                volunteer_key = k
                break

        if volunteer_key is not None:
            self.edit_volunteer_input.setText(volunteer_key)
        else:
            self.edit_volunteer_input.clear()

        self.edit_date_input.setDate(datetime.strptime(date, "%Y-%m-%d"))
        self.edit_amount_input.setText(str(amount))

        self.update_volunteer_info_edit()

    def edit_record(self, record_id):
        record = self.load_record(record_id)
        if record:
            self.fill_edit_form(record)
            self.stacked_layout.setCurrentWidget(self.edit_form_widget)
        else:
            QMessageBox.warning(self, "Erro", "Doação não encontrada.")

    def delete_action(self, record_id):
        reply = QMessageBox.question(
            self, 'Confirmação', 'Tem certeza que deseja deletar esta doação?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.delete_record(record_id)
            self.load_data()

    def update_volunteer_info(self):
        key = self.volunteer_input.text().strip()
        if key in self.volunteer_full_info:
            vid, address, phone = self.volunteer_full_info[key]
            self.volunteer_info.setText(f"Endereço: {address}, Telefone: {phone}")
        else:
            self.volunteer_info.clear()

    def update_volunteer_info_edit(self):
        key = self.edit_volunteer_input.text().strip()
        if key in self.volunteer_full_info:
            vid, address, phone = self.volunteer_full_info[key]
            self.edit_volunteer_info.setText(f"Endereço: {address}, Telefone: {phone}")
        else:
            self.edit_volunteer_info.clear()
