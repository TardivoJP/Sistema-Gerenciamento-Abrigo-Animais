from base_list_widget import BaseListWidget
from PyQt6.QtWidgets import (
    QLineEdit, QPushButton, QDateEdit, QTextEdit, QMessageBox
)
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from datetime import datetime
from database import create_connection

class VolunteerListWidget(BaseListWidget):
    def __init__(self):
        super().__init__()
        self.order_by_column = "id"

    def get_title(self):
        return "Lista de Voluntários"

    def get_new_button_text(self):
        return "Novo Voluntário"

    def get_table_headers(self):
        # Agora temos CPF na tabela
        return ["ID", "Nome", "Telefone", "CPF", "", ""]

    def init_search_fields(self):
        self.search_field_combo.addItem("ID", "id")
        self.search_field_combo.addItem("Nome", "name")
        self.search_field_combo.addItem("Telefone", "phone")
        self.search_field_combo.addItem("CPF", "cpf")

    def get_column_mapping(self):
        # Mapeamento para permitir ordenação e filtragem
        return {
            0: "id",
            1: "name",
            2: "phone",
            3: "cpf"
        }

    def build_record_query(self, count_only=False):
        base = "SELECT "
        if count_only:
            base += "COUNT(*)"
        else:
            # Precisamos incluir o CPF também no SELECT
            base += "id, name, phone, cpf"
        base += " FROM volunteers"

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
        volunteer_id = row_data[0]

        edit_button = QPushButton("Editar")
        edit_button.clicked.connect(lambda checked, vid=volunteer_id: self.edit_record(vid))
        self.table.setCellWidget(row_idx, 4, edit_button)

        delete_button = QPushButton("Deletar")
        delete_button.clicked.connect(lambda checked, vid=volunteer_id: self.delete_action(vid))
        self.table.setCellWidget(row_idx, 5, delete_button)

    def initFormFields(self, form_layout):
        self.name_input = QLineEdit()
        form_layout.addRow("Nome:", self.name_input)

        self.address_input = QLineEdit()
        form_layout.addRow("Endereço:", self.address_input)

        self.phone_input = QLineEdit()
        self.setup_digit_only_validator(self.phone_input)
        self.phone_input.textChanged.connect(self.format_phone)
        form_layout.addRow("Telefone:", self.phone_input)

        self.cpf_input = QLineEdit()
        self.setup_digit_only_validator(self.cpf_input)
        self.cpf_input.textChanged.connect(self.format_cpf)
        form_layout.addRow("CPF:", self.cpf_input)

        self.birth_date_input = QDateEdit()
        self.birth_date_input.setCalendarPopup(True)
        self.birth_date_input.setDate(datetime.now())
        form_layout.addRow("Data de Nascimento:", self.birth_date_input)

        self.availability_input = QTextEdit()
        form_layout.addRow("Disponibilidade:", self.availability_input)

        self.skills_input = QTextEdit()
        form_layout.addRow("Habilidades:", self.skills_input)

        self.experience_input = QTextEdit()
        form_layout.addRow("Experiência:", self.experience_input)

        self.motivation_input = QTextEdit()
        form_layout.addRow("Motivação:", self.motivation_input)

    def initEditFormFields(self, form_layout):
        self.edit_id = None

        self.edit_name_input = QLineEdit()
        form_layout.addRow("Nome:", self.edit_name_input)

        self.edit_address_input = QLineEdit()
        form_layout.addRow("Endereço:", self.edit_address_input)

        self.edit_phone_input = QLineEdit()
        self.setup_digit_only_validator(self.edit_phone_input)
        self.edit_phone_input.textChanged.connect(self.format_phone_edit)
        form_layout.addRow("Telefone:", self.edit_phone_input)

        self.edit_cpf_input = QLineEdit()
        self.setup_digit_only_validator(self.edit_cpf_input)
        self.edit_cpf_input.textChanged.connect(self.format_cpf_edit)
        form_layout.addRow("CPF:", self.edit_cpf_input)

        self.edit_birth_date_input = QDateEdit()
        self.edit_birth_date_input.setCalendarPopup(True)
        self.edit_birth_date_input.setDate(datetime.now())
        form_layout.addRow("Data de Nascimento:", self.edit_birth_date_input)

        self.edit_availability_input = QTextEdit()
        form_layout.addRow("Disponibilidade:", self.edit_availability_input)

        self.edit_skills_input = QTextEdit()
        form_layout.addRow("Habilidades:", self.edit_skills_input)

        self.edit_experience_input = QTextEdit()
        form_layout.addRow("Experiência:", self.edit_experience_input)

        self.edit_motivation_input = QTextEdit()
        form_layout.addRow("Motivação:", self.edit_motivation_input)

    def setup_digit_only_validator(self, line_edit):
        regex = QRegularExpression("^[0-9]*$")
        validator = QRegularExpressionValidator(regex)
        line_edit.setValidator(validator)

    def strip_non_digits(self, s):
        return "".join([c for c in s if c.isdigit()])

    def format_phone(self):
        text = self.strip_non_digits(self.phone_input.text())
        if len(text) > 11:
            text = text[:11]
        formatted = self.format_phone_text(text)
        self.phone_input.blockSignals(True)
        self.phone_input.setText(formatted)
        self.phone_input.setCursorPosition(len(self.phone_input.text()))
        self.phone_input.blockSignals(False)

    def format_phone_edit(self):
        text = self.strip_non_digits(self.edit_phone_input.text())
        if len(text) > 11:
            text = text[:11]
        formatted = self.format_phone_text(text)
        self.edit_phone_input.blockSignals(True)
        self.edit_phone_input.setText(formatted)
        self.edit_phone_input.setCursorPosition(len(self.edit_phone_input.text()))
        self.edit_phone_input.blockSignals(False)

    def format_phone_text(self, digits):
        if len(digits) == 0:
            return ""
        if len(digits) == 10:
            return f"({digits[0:2]}) {digits[2:6]}-{digits[6:]}"
        elif len(digits) == 11:
            return f"({digits[0:2]}) {digits[2:7]}-{digits[7:]}"
        else:
            return digits

    def format_cpf(self):
        text = self.strip_non_digits(self.cpf_input.text())
        if len(text) > 11:
            text = text[:11]
        formatted = self.format_cpf_text(text)
        self.cpf_input.blockSignals(True)
        self.cpf_input.setText(formatted)
        self.cpf_input.setCursorPosition(len(self.cpf_input.text()))
        self.cpf_input.blockSignals(False)

    def format_cpf_edit(self):
        text = self.strip_non_digits(self.edit_cpf_input.text())
        if len(text) > 11:
            text = text[:11]
        formatted = self.format_cpf_text(text)
        self.edit_cpf_input.blockSignals(True)
        self.edit_cpf_input.setText(formatted)
        self.edit_cpf_input.setCursorPosition(len(self.edit_cpf_input.text()))
        self.edit_cpf_input.blockSignals(False)

    def format_cpf_text(self, digits):
        if len(digits) == 11:
            return f"{digits[0:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:11]}"
        else:
            return digits

    def clear_form(self):
        self.name_input.clear()
        self.address_input.clear()
        self.phone_input.clear()
        self.cpf_input.clear()
        self.birth_date_input.setDate(datetime.now())
        self.availability_input.clear()
        self.skills_input.clear()
        self.experience_input.clear()
        self.motivation_input.clear()

    def clear_edit_form(self):
        self.edit_name_input.clear()
        self.edit_address_input.clear()
        self.edit_phone_input.clear()
        self.edit_cpf_input.clear()
        self.edit_birth_date_input.setDate(datetime.now())
        self.edit_availability_input.clear()
        self.edit_skills_input.clear()
        self.edit_experience_input.clear()
        self.edit_motivation_input.clear()

    def collect_form_data(self):
        phone_digits = self.strip_non_digits(self.phone_input.text())
        cpf_digits = self.strip_non_digits(self.cpf_input.text())

        data = {
            "name": self.name_input.text().strip(),
            "address": self.address_input.text().strip(),
            "phone": phone_digits,
            "cpf": cpf_digits,
            "birth_date": self.birth_date_input.date().toString("yyyy-MM-dd"),
            "availability": self.availability_input.toPlainText().strip(),
            "skills": self.skills_input.toPlainText().strip(),
            "experience": self.experience_input.toPlainText().strip(),
            "motivation": self.motivation_input.toPlainText().strip()
        }
        return data

    def collect_edit_form_data(self):
        phone_digits = self.strip_non_digits(self.edit_phone_input.text())
        cpf_digits = self.strip_non_digits(self.edit_cpf_input.text())

        data = {
            "name": self.edit_name_input.text().strip(),
            "address": self.edit_address_input.text().strip(),
            "phone": phone_digits,
            "cpf": cpf_digits,
            "birth_date": self.edit_birth_date_input.date().toString("yyyy-MM-dd"),
            "availability": self.edit_availability_input.toPlainText().strip(),
            "skills": self.edit_skills_input.toPlainText().strip(),
            "experience": self.edit_experience_input.toPlainText().strip(),
            "motivation": self.edit_motivation_input.toPlainText().strip()
        }
        return data

    def validate_data(self, data):
        # Campos obrigatórios: Nome, Endereço, CPF
        if not data["name"] or not data["cpf"] or not data["address"]:
            return False, "Por favor, preencha os campos obrigatórios: Nome, Endereço e CPF."

        # CPF deve ter 11 dígitos
        if len(data["cpf"]) != 11:
            return False, "CPF deve ter 11 dígitos."

        # Telefone: se não vazio, deve ter 10 ou 11 dígitos
        if data["phone"]:
            if len(data["phone"]) not in (10, 11):
                return False, "Telefone inválido. Deve conter 10 ou 11 dígitos."

        return True, ""

    def save_record(self, data):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO volunteers (name, address, phone, cpf, birth_date, availability, skills, experience, motivation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data["name"], data["address"], data["phone"], data["cpf"], data["birth_date"], data["availability"], data["skills"], data["experience"], data["motivation"]))
        conn.commit()
        conn.close()

    def update_record(self, record_id, data):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE volunteers
            SET name = ?, address = ?, phone = ?, cpf = ?, birth_date = ?, availability = ?, skills = ?, experience = ?, motivation = ?
            WHERE id = ?
        ''', (data["name"], data["address"], data["phone"], data["cpf"], data["birth_date"], data["availability"], data["skills"], data["experience"], data["motivation"], record_id))
        conn.commit()
        conn.close()

    def delete_record(self, record_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM volunteers WHERE id = ?', (record_id,))
        conn.commit()
        conn.close()

    def load_record(self, record_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM volunteers WHERE id = ?', (record_id,))
        record = cursor.fetchone()
        conn.close()
        return record

    def fill_edit_form(self, record):
        self.edit_id = record[0]
        self.edit_name_input.setText(record[1])
        self.edit_address_input.setText(record[2])

        phone_digits = record[3] if record[3] else ""
        self.edit_phone_input.setText(phone_digits)

        cpf_digits = record[4] if record[4] else ""
        self.edit_cpf_input.setText(cpf_digits)

        self.edit_birth_date_input.setDate(datetime.strptime(record[5], "%Y-%m-%d"))
        self.edit_availability_input.setPlainText(record[6] if record[6] else "")
        self.edit_skills_input.setPlainText(record[7] if record[7] else "")
        self.edit_experience_input.setPlainText(record[8] if record[8] else "")
        self.edit_motivation_input.setPlainText(record[9] if record[9] else "")

    def edit_record(self, record_id):
        record = self.load_record(record_id)
        if record:
            self.fill_edit_form(record)
            self.stacked_layout.setCurrentWidget(self.edit_form_widget)
        else:
            QMessageBox.warning(self, "Erro", "Voluntário não encontrado.")

    def delete_action(self, record_id):
        reply = QMessageBox.question(
            self, 'Confirmação', 'Tem certeza que deseja deletar este voluntário?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM donations WHERE volunteer_id = ?', (record_id,))
            count = cursor.fetchone()[0]
            if count > 0:
                QMessageBox.warning(self, "Erro", "Não é possível deletar um voluntário com doações associadas.")
                conn.close()
                return
            self.delete_record(record_id)
            self.load_data()
