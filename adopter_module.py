from base_list_widget import BaseListWidget
from PyQt6.QtWidgets import QLineEdit, QPushButton, QDateEdit, QMessageBox, QWidget, QVBoxLayout, QFormLayout
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator, QDoubleValidator
from datetime import datetime
from database import create_connection

class AdopterListWidget(BaseListWidget):
    def __init__(self):
        self.column_mapping_local = {
            0: "adopters.id",
            1: "persons.name",
            2: "persons.phone",
            3: "persons.cpf",
            4: "adopters.created_at"
        }
        super().__init__()
        self.order_by_column = "adopters.id"
        self.initDetailsUI()
        self.set_styles()

    def set_styles(self):
        style = (
            "QWidget {"
            "    background-color: #f4f6fb;"
            "}"
            "QPushButton {"
            "    border: 1px solid #f4f6fb;"
            "    border-radius: 15px;"
            "    background-color: #fffefe;"
            "    color: black;"
            "    padding: 5px 10px;"
            "    font-size: 14px;"
            "}"
            "QPushButton:hover {"
            "    background-color: #eaeaea;"
            "}"
            "QPushButton:disabled {"
            "    background-color: #d3d3d3;"
            "    color: #a9a9a9;"
            "}"
            "QTableWidget {"
            "    gridline-color: transparent;"
            "    background-color: #fffefe;"  # Cor de fundo da tabela
            "    border: 2px solid #eef1f6;"
            "    border-bottom-left-radius: 10px;"  # Arredondando a borda inferior esquerda
            "    border-bottom-right-radius: 10px;"  # Arredondando a borda inferior direita
            "    border-top-left-radius: 10px;"  # Sem arredondamento no topo esquerdo
            "    border-top-right-radius: 10px;"  # Sem arredondamento no topo direito
            "}"
            "QHeaderView::section {"
            "    background-color: #f4f6fb;"  # Cor de fundo
            "    color: #9ba3b2;"  # Cor do texto
            "    border: none;"
            "    padding: 8px;"  # Espaçamento interno para evitar cortes
            "    text-align: left;"
            "}"
            "QHeaderView::up-arrow, QHeaderView::down-arrow {"
            "    width: 12px;"  # Largura do ícone
            "    height: 12px;"  # Altura do ícone
            "    margin-left: 5px;"  # Espaçamento entre texto e ícone
            "    padding: 2px;"  # Evita cortes
            "}"
            "QComboBox, QLineEdit {"
            "    background-color: #fffefe;"  # Cor de fundo dos campos de pesquisa
            "    border: 1px solid #eef1f6;"  # Borda para os campos
            "    border-radius: 5px;"  # Bordas arredondadas
            "    padding: 5px;"  # Espaçamento interno
            "    font-size: 14px;"  # Tamanho da fonte
            "}"
            "QComboBox:hover, QLineEdit:hover {"
            "    background-color: #d3d3d3;"  # Cor de fundo ao passar o mouse
            "}"
                    # Customizando a barra de rolagem
        "QScrollBar:horizontal {"
        "    border: none;"  # Remove a borda
        "    background: #f0f0f0;"  # Cor de fundo da barra horizontal
        "    height: 8px;"  # Altura da barra de rolagem horizontal
        "    margin: 0px 21px 0 21px;"  # Distância do conteúdo
        "}"
        "QScrollBar:vertical {"
        "    border: none;"  # Remove a borda
        "    background: #f0f0f0;"  # Cor de fundo da barra vertical
        "    width: 8px;"  # Largura da barra de rolagem vertical
        "    margin: 21px 0 21px 0;"  # Distância do conteúdo
        "}"
        "QScrollBar::handle:horizontal, QScrollBar::handle:vertical {"
        "    background: #c0c0c0;"  # Cor do 'thumb' (parte que se arrasta)
        "    border-radius: 4px;"  # Bordas arredondadas
        "}"
        "QScrollBar::handle:horizontal:hover, QScrollBar::handle:vertical:hover {"
        "    background: #a0a0a0;"  # Cor do 'thumb' ao passar o mouse
        "}"
        "QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal, "
        "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {"
        "    background: none;"  # Remove os botões de seta da barra de rolagem
        "}"
        "QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical, "
        "QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {"
        "    background: none;"  # Remove os botões de seta
        "}"
        )



        self.setStyleSheet(style)
    def get_title(self):
        return "Lista de Adotantes"

    def get_new_button_text(self):
        return "Novo Adotante"

    def get_table_headers(self):
        return ["ID", "Nome", "Telefone", "CPF", "Criado em", "", "", ""]

    def init_search_fields(self):
        self.search_field_combo.addItem("ID", "adopters.id")
        self.search_field_combo.addItem("Nome", "persons.name")
        self.search_field_combo.addItem("Telefone", "persons.phone")
        self.search_field_combo.addItem("CPF", "persons.cpf")

    def get_column_mapping(self):
        return self.column_mapping_local

    def build_record_query(self, count_only=False):
        base = "SELECT "
        if count_only:
            base += "COUNT(*)"
        else:
            base += "adopters.id, persons.name, persons.phone, persons.cpf, adopters.created_at"
        base += " FROM adopters JOIN persons ON adopters.person_id = persons.id"

        conditions = []
        if self.filter_field and self.filter_value:
            field = self.filter_field
            value = self.filter_value
            if field == "adopters.id":
                if value.isdigit():
                    conditions.append("adopters.id = {}".format(int(value)))
                else:
                    conditions.append("CAST(adopters.id AS TEXT) LIKE '%{}%'".format(value))
            else:
                conditions.append(f"{field} LIKE '%{value}%'")

        if conditions:
            base += " WHERE " + " AND ".join(conditions)

        if not count_only:
            if self.order_by_column is None:
                self.order_by_column = "adopters.id"
            base += f" ORDER BY {self.order_by_column} {self.order_direction}"
            base += f" LIMIT {self.page_size} OFFSET {self.current_page * self.page_size}"

        return base

    def add_actions_to_row(self, row_idx, row_data):
        adopter_id = row_data[0]

        details_button = QPushButton("Detalhes")
        details_button.clicked.connect(lambda checked, aid=adopter_id: self.show_details(aid))
        self.table.setCellWidget(row_idx, 5, details_button)

        edit_button = QPushButton("Editar")
        edit_button.clicked.connect(lambda checked, aid=adopter_id: self.edit_record(aid))
        self.table.setCellWidget(row_idx, 6, edit_button)

        delete_button = QPushButton("Deletar")
        delete_button.clicked.connect(lambda checked, aid=adopter_id: self.delete_action(aid))
        self.table.setCellWidget(row_idx, 7, delete_button)

        # Verificar se o adotante possui adoções associadas
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM adoptions WHERE adopter_id = ?', (adopter_id,))
        count = cursor.fetchone()[0]
        conn.close()

        # Se houver adoções associadas, desabilita o botão Deletar
        if count > 0:
            delete_button.setEnabled(False)


    def delete_action(self, record_id):
        reply = QMessageBox.question(
            self, 'Confirmação', 'Tem certeza que deseja deletar este adotante?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            conn = create_connection()
            cursor = conn.cursor()
            # Verificar adoções
            cursor.execute('SELECT COUNT(*) FROM adoptions WHERE adopter_id = ?', (record_id,))
            count = cursor.fetchone()[0]
            if count > 0:
                conn.close()
                QMessageBox.warning(self, "Erro", "Não é possível deletar este adotante pois ele possui adoções associadas.\n"
                                                  "Delete primeiro as adoções associadas.")
                return

            cursor.execute('SELECT person_id FROM adopters WHERE id = ?', (record_id,))
            pid = cursor.fetchone()
            if pid:
                person_id = pid[0]
                cursor.execute('DELETE FROM adopters WHERE id = ?', (record_id,))
                # Atualizar persons.isAdopter se não houver mais adotantes
                cursor.execute('SELECT COUNT(*) FROM adopters WHERE person_id = ?', (person_id,))
                c = cursor.fetchone()[0]
                if c == 0:
                    cursor.execute('UPDATE persons SET isAdopter = 0 WHERE id = ?', (person_id,))

            conn.commit()
            conn.close()
            self.load_data()
        
    def initFormFields(self, form_layout):
        self.person_locked = False
        self.cpf_input = QLineEdit()
        self.setup_digit_only_validator(self.cpf_input)
        self.cpf_input.setMaxLength(14)  # Permite 11 dígitos + formatação. Ajuste se necessário.
        self.cpf_input.textChanged.connect(self.on_cpf_changed)
        form_layout.addRow("CPF:", self.cpf_input)

        self.name_input = QLineEdit()
        form_layout.addRow("Nome:", self.name_input)

        self.address_input = QLineEdit()
        form_layout.addRow("Endereço:", self.address_input)

        self.phone_input = QLineEdit()
        self.setup_digit_only_validator(self.phone_input)
        self.phone_input.textChanged.connect(self.format_phone)
        form_layout.addRow("Telefone:", self.phone_input)

        self.birth_date_input = QDateEdit()
        self.birth_date_input.setCalendarPopup(True)
        self.birth_date_input.setDate(datetime.now())
        form_layout.addRow("Data de Nascimento:", self.birth_date_input)

        self.occupation_input = QLineEdit()
        form_layout.addRow("Ocupação:", self.occupation_input)

        self.income_input = QLineEdit()
        income_validator = QDoubleValidator(0.0, 9999999999.99, 2)
        income_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.income_input.setValidator(income_validator)
        form_layout.addRow("Renda:", self.income_input)
        
    def on_cpf_changed(self):
        cpf_digits = self.strip_non_digits(self.cpf_input.text())

        # Se length > 11, truncar
        if len(cpf_digits) > 11:
            cpf_digits = cpf_digits[:11]
            # Repor texto formatado
            self.cpf_input.blockSignals(True)
            self.cpf_input.setText(self.format_cpf_text(cpf_digits))
            self.cpf_input.setCursorPosition(len(self.cpf_input.text()))
            self.cpf_input.blockSignals(False)

        if len(cpf_digits) == 11:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, address, phone, cpf, birth_date, isAdopter, isVolunteer FROM persons WHERE cpf = ?", (cpf_digits,))
            person = cursor.fetchone()
            conn.close()

            if person:
                _, pname, paddress, pphone, pcpf, pbirth, isAdopter, isVolunteer = person
                self.name_input.setText(pname if pname else "")
                self.address_input.setText(paddress if paddress else "")
                self.phone_input.setText(pphone if pphone else "")
                if pbirth:
                    self.birth_date_input.setDate(datetime.strptime(pbirth, "%Y-%m-%d"))
                else:
                    self.birth_date_input.setDate(datetime.now())

                self.lock_common_fields(True)
                self.person_locked = True
            else:
                if self.person_locked:
                    self.clear_common_fields()
                    self.lock_common_fields(False)
                    self.person_locked = False
        else:
            # Menos de 11 dígitos
            if self.person_locked:
                self.clear_common_fields()
                self.lock_common_fields(False)
                self.person_locked = False

    def lock_common_fields(self, lock: bool):
        self.name_input.setReadOnly(lock)
        self.address_input.setReadOnly(lock)
        self.phone_input.setReadOnly(lock)
        self.birth_date_input.setEnabled(not lock)

    def clear_common_fields(self):
        self.name_input.clear()
        self.address_input.clear()
        self.phone_input.clear()
        self.birth_date_input.setDate(datetime.now())

    def initEditFormFields(self, form_layout):
        self.edit_cpf_input = QLineEdit()
        self.setup_digit_only_validator(self.edit_cpf_input)
        self.edit_cpf_input.textChanged.connect(self.format_cpf_edit)
        self.edit_cpf_input.setReadOnly(True)
        form_layout.addRow("CPF:", self.edit_cpf_input)

        self.edit_name_input = QLineEdit()
        form_layout.addRow("Nome:", self.edit_name_input)

        self.edit_address_input = QLineEdit()
        form_layout.addRow("Endereço:", self.edit_address_input)

        self.edit_phone_input = QLineEdit()
        self.setup_digit_only_validator(self.edit_phone_input)
        self.edit_phone_input.textChanged.connect(self.format_phone_edit)
        form_layout.addRow("Telefone:", self.edit_phone_input)

        self.edit_birth_date_input = QDateEdit()
        self.edit_birth_date_input.setCalendarPopup(True)
        self.edit_birth_date_input.setDate(datetime.now())
        form_layout.addRow("Data de Nascimento:", self.edit_birth_date_input)

        self.edit_occupation_input = QLineEdit()
        form_layout.addRow("Ocupação:", self.edit_occupation_input)

        self.edit_income_input = QLineEdit()
        income_validator = QDoubleValidator(0.0, 9999999999.99, 2)
        income_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.edit_income_input.setValidator(income_validator)
        form_layout.addRow("Renda:", self.edit_income_input)

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
        self.cpf_input.clear()
        self.name_input.clear()
        self.address_input.clear()
        self.phone_input.clear()
        self.birth_date_input.setDate(datetime.now())
        self.occupation_input.clear()
        self.income_input.clear()

    def clear_edit_form(self):
        self.edit_cpf_input.clear()
        self.edit_name_input.clear()
        self.edit_address_input.clear()
        self.edit_phone_input.clear()
        self.edit_birth_date_input.setDate(datetime.now())
        self.edit_occupation_input.clear()
        self.edit_income_input.clear()

    def collect_form_data(self):
        phone_digits = self.strip_non_digits(self.phone_input.text())
        cpf_digits = self.strip_non_digits(self.cpf_input.text())

        data = {
            "cpf": cpf_digits,
            "name": self.name_input.text().strip(),
            "address": self.address_input.text().strip(),
            "phone": phone_digits,
            "birth_date": self.birth_date_input.date().toString("yyyy-MM-dd"),
            "occupation": self.occupation_input.text().strip(),
            "income": self.income_input.text().strip()
        }
        return data

    def collect_edit_form_data(self):
        phone_digits = self.strip_non_digits(self.edit_phone_input.text())
        cpf_digits = self.strip_non_digits(self.edit_cpf_input.text())

        data = {
            "cpf": cpf_digits,  # CPF teoricamente não muda
            "name": self.edit_name_input.text().strip(),
            "address": self.edit_address_input.text().strip(),
            "phone": phone_digits,
            "birth_date": self.edit_birth_date_input.date().toString("yyyy-MM-dd"),
            "occupation": self.edit_occupation_input.text().strip(),
            "income": self.edit_income_input.text().strip()
        }
        return data

    def validate_data(self, data):
        # Todos obrigatórios: Nome, Endereço, CPF, Telefone, birth_date, occupation, income
        if not data["cpf"]:
            return False, "Por favor, preencha o campo CPF."
        if len(data["cpf"]) != 11:
            return False, "CPF deve ter 11 dígitos."
        if not data["name"]:
            return False, "Por favor, preencha o campo Nome."
        if not data["address"]:
            return False, "Por favor, preencha o campo Endereço."
        if not data["phone"]:
            return False, "Por favor, preencha o campo Telefone."
        if len(data["phone"]) not in (10, 11):
            return False, "Telefone inválido. Deve conter 10 ou 11 dígitos."
        if not data["birth_date"]:
            return False, "Por favor, preencha a Data de Nascimento."
        if not data["occupation"]:
            return False, "Por favor, preencha o campo Ocupação."
        if not data["income"]:
            return False, "Por favor, preencha o campo Renda."
        # Checar renda
        try:
            float(data["income"].replace(",", "."))
        except ValueError:
            return False, "Renda inválida, insira um número válido."

        return True, ""

    def save_record(self, data):
        # Primeiro checar CPF duplicado como adotante, antes de validar outros campos
        cpf = data["cpf"]
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, isAdopter FROM persons WHERE cpf = ?", (cpf,))
        person = cursor.fetchone()

        if person is not None:
            # Se já é adotante
            pid = person[0]
            isAdopter = person[1]
            if isAdopter == 1:
                QMessageBox.warning(self, "Erro", "Este CPF já está cadastrado como Adotante.")
                conn.close()
                return  # Não muda de tela, apenas retorna
        conn.close()

        # Agora validar campos
        valid, msg = self.validate_data(data)
        if not valid:
            QMessageBox.warning(self, "Erro", msg)
            return

        # CPF é válido e não está duplicado como adotante, prosseguir
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, isAdopter, isVolunteer FROM persons WHERE cpf = ?", (cpf,))
        person = cursor.fetchone()

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if person is None:
            # Cria pessoa
            cursor.execute('''
                INSERT INTO persons (name, address, phone, cpf, birth_date, isAdopter, isVolunteer, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data["name"], data["address"], data["phone"], cpf, data["birth_date"], 1, 0, created_at))
            person_id = cursor.lastrowid
        else:
            person_id = person[0]
            # Atualiza pessoa
            cursor.execute('''
                UPDATE persons
                SET name = ?, address = ?, phone = ?, birth_date = ?, isAdopter = 1
                WHERE id = ?
            ''', (data["name"], data["address"], data["phone"], data["birth_date"], person_id))

        income = float(data["income"].replace(",", "."))

        cursor.execute('''
            INSERT INTO adopters (person_id, occupation, income, created_at)
            VALUES (?, ?, ?, ?)
        ''', (person_id, data["occupation"], income, created_at))

        conn.commit()
        conn.close()
        self.load_data()
        self.stacked_layout.setCurrentWidget(self.table_widget)

    def update_record(self, record_id, data):
        # Validar dados primeiro
        valid, msg = self.validate_data(data)
        if not valid:
            QMessageBox.warning(self, "Erro", msg)
            return

        income = float(data["income"].replace(",", "."))

        conn = create_connection()
        cursor = conn.cursor()
        # Obter person_id
        cursor.execute('SELECT person_id FROM adopters WHERE id = ?', (record_id,))
        pid = cursor.fetchone()
        if pid is None:
            conn.close()
            QMessageBox.warning(self, "Erro", "Registro não encontrado.")
            return
        person_id = pid[0]

        # Atualizar persons
        cursor.execute('''
            UPDATE persons
            SET name = ?, address = ?, phone = ?, birth_date = ?
            WHERE id = ?
        ''', (data["name"], data["address"], data["phone"], data["birth_date"], person_id))

        # Atualizar adopters
        cursor.execute('''
            UPDATE adopters
            SET occupation = ?, income = ?
            WHERE id = ?
        ''', (data["occupation"], income, record_id))

        conn.commit()
        conn.close()

        self.load_data()
        self.stacked_layout.setCurrentWidget(self.table_widget)

    def load_record(self, record_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT adopters.id, persons.name, persons.address, persons.phone, persons.cpf, persons.birth_date,
                   adopters.occupation, adopters.income
            FROM adopters
            JOIN persons ON adopters.person_id = persons.id
            WHERE adopters.id = ?
        ''', (record_id,))
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

        bd = record[5]
        if bd:
            self.edit_birth_date_input.setDate(datetime.strptime(bd, "%Y-%m-%d"))
        else:
            self.edit_birth_date_input.setDate(datetime.now())

        self.edit_occupation_input.setText(record[6] if record[6] else "")
        self.edit_income_input.setText(str(record[7]) if record[7] is not None else "")

        self.stacked_layout.setCurrentWidget(self.edit_form_widget)
        
    def initDetailsUI(self):
        # Cria um widget de detalhes (read-only)
        self.details_widget = QWidget()
        details_layout = QVBoxLayout()
        self.details_form = QFormLayout()

        self.details_cpf = QLineEdit(); self.details_cpf.setReadOnly(True)
        self.details_form.addRow("CPF:", self.details_cpf)

        self.details_name = QLineEdit(); self.details_name.setReadOnly(True)
        self.details_form.addRow("Nome:", self.details_name)

        self.details_address = QLineEdit(); self.details_address.setReadOnly(True)
        self.details_form.addRow("Endereço:", self.details_address)

        self.details_phone = QLineEdit(); self.details_phone.setReadOnly(True)
        self.details_form.addRow("Telefone:", self.details_phone)

        self.details_birth_date = QLineEdit(); self.details_birth_date.setReadOnly(True)
        self.details_form.addRow("Data de Nascimento:", self.details_birth_date)

        self.details_occupation = QLineEdit(); self.details_occupation.setReadOnly(True)
        self.details_form.addRow("Ocupação:", self.details_occupation)

        self.details_income = QLineEdit(); self.details_income.setReadOnly(True)
        self.details_form.addRow("Renda:", self.details_income)

        details_layout.addLayout(self.details_form)

        close_button = QPushButton("Fechar")
        close_button.clicked.connect(lambda: self.stacked_layout.setCurrentWidget(self.table_widget))
        details_layout.addWidget(close_button)

        self.details_widget.setLayout(details_layout)
        self.stacked_layout.addWidget(self.details_widget)

    def show_details(self, record_id):
        # Carregar dados do adotante + pessoa
        record = self.load_record(record_id)
        if not record:
            QMessageBox.warning(self, "Erro", "Registro não encontrado.")
            return
        # Preencher campos read-only
        # (mesma ordem do load_record)
        # record: 
        # 0: id, 1: name, 2: address, 3: phone, 4: cpf, 5: birth_date, 6: occupation, 7: income
        self.details_cpf.setText(record[4] if record[4] else "")
        self.details_name.setText(record[1] if record[1] else "")
        self.details_address.setText(record[2] if record[2] else "")
        self.details_phone.setText(record[3] if record[3] else "")
        self.details_birth_date.setText(record[5] if record[5] else "")
        self.details_occupation.setText(record[6] if record[6] else "")
        self.details_income.setText(str(record[7]) if record[7] is not None else "")

        self.stacked_layout.setCurrentWidget(self.details_widget)
