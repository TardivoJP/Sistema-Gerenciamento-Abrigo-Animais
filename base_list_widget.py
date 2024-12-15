from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QStackedLayout, QFormLayout, QSizePolicy
)
from PyQt6.QtCore import Qt
from math import ceil
from database import create_connection

class BaseListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_page = 0
        self.page_size = 25
        self.order_by_column = None
        self.order_direction = "ASC"
        self.filter_field = None
        self.filter_value = None
        self.total_pages = 0
        self.initUI()
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
    def initUI(self):
        self.layout = QVBoxLayout()
        self.stacked_layout = QStackedLayout()

        self.table_widget = QWidget()
        self.initTableUI()
        self.stacked_layout.addWidget(self.table_widget)

        self.form_widget = QWidget()
        self.initFormUI()
        self.stacked_layout.addWidget(self.form_widget)

        self.edit_form_widget = QWidget()
        self.initEditFormUI()
        self.stacked_layout.addWidget(self.edit_form_widget)

        self.layout.addLayout(self.stacked_layout)
        self.setLayout(self.layout)
        self.stacked_layout.setCurrentWidget(self.table_widget)

    # Métodos que antes eram abstratos agora levantam NotImplementedError
    def get_table_name(self):
        raise NotImplementedError("Subclasse deve implementar get_table_name().")

    def get_table_headers(self):
        raise NotImplementedError("Subclasse deve implementar get_table_headers().")

    def get_column_mapping(self):
        raise NotImplementedError("Subclasse deve implementar get_column_mapping().")

    def initFormFields(self, form_layout):
        raise NotImplementedError("Subclasse deve implementar initFormFields().")

    def initEditFormFields(self, form_layout):
        raise NotImplementedError("Subclasse deve implementar initEditFormFields().")

    def build_record_query(self, count_only=False):
        raise NotImplementedError("Subclasse deve implementar build_record_query().")

    def save_record(self, data):
        raise NotImplementedError("Subclasse deve implementar save_record().")

    def update_record(self, record_id, data):
        raise NotImplementedError("Subclasse deve implementar update_record().")

    def delete_record(self, record_id):
        raise NotImplementedError("Subclasse deve implementar delete_record().")

    def load_record(self, record_id):
        raise NotImplementedError("Subclasse deve implementar load_record().")

    def validate_data(self, data):
        # Pode ser sobrescrito, se não sobrescrever, considera sempre válido
        return True, ""

    def initTableUI(self):
        main_layout = QVBoxLayout()

        # Título
        title = QLabel(self.get_title())
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title)

        # Barra de busca
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Filtrar por:"))
        self.search_field_combo = QComboBox()
        # Será a subclasse que define as opções de filtragem (por padrão id, name, etc.)
        self.init_search_fields()
        top_layout.addWidget(self.search_field_combo)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite o termo de pesquisa...")
        top_layout.addWidget(self.search_input)

        search_button = QPushButton("Buscar")
        search_button.clicked.connect(self.apply_filter)
        top_layout.addWidget(search_button)

        clear_button = QPushButton("Limpar")
        clear_button.clicked.connect(self.clear_filter)
        top_layout.addWidget(clear_button)

        top_layout.addStretch()
        main_layout.addLayout(top_layout)

        # Tabela
        self.table = QTableWidget()
        headers = self.get_table_headers()
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        header = self.table.horizontalHeader()
        header.sectionClicked.connect(self.header_clicked)
        main_layout.addWidget(self.table)

        # Paginação
        pagination_layout = QHBoxLayout()
        pagination_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.first_button = QPushButton("<<")
        self.first_button.clicked.connect(lambda: self.go_to_page(1))
        pagination_layout.addWidget(self.first_button)

        self.prev_button = QPushButton("<")
        self.prev_button.clicked.connect(lambda: self.go_to_page(self.current_page + 1 - 1))
        pagination_layout.addWidget(self.prev_button)

        self.page_buttons = []
        for i in range(5):
            btn = QPushButton("")
            btn.setEnabled(False)
            btn.setMinimumWidth(30)
            self.page_buttons.append(btn)
            pagination_layout.addWidget(btn)

        self.next_button = QPushButton(">")
        self.next_button.clicked.connect(lambda: self.go_to_page(self.current_page + 1 + 1))
        pagination_layout.addWidget(self.next_button)

        self.last_button = QPushButton(">>")
        self.last_button.clicked.connect(lambda: self.go_to_page(self.total_pages))
        pagination_layout.addWidget(self.last_button)

        main_layout.addLayout(pagination_layout)

        # Ir para página
        goto_layout = QHBoxLayout()
        goto_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        goto_layout.addWidget(QLabel("Ir para página:"))
        self.goto_page_input = QLineEdit()
        self.goto_page_input.setFixedWidth(50)
        self.goto_page_input.setPlaceholderText("Pg")
        policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.goto_page_input.setSizePolicy(policy)
        goto_layout.addWidget(self.goto_page_input)

        goto_button = QPushButton("Ir")
        goto_button.clicked.connect(self.goto_page)
        goto_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        goto_button.setMaximumWidth(50)
        goto_layout.addWidget(goto_button)

        main_layout.addLayout(goto_layout)

        # Página atual
        current_page_layout = QHBoxLayout()
        current_page_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_page_label = QLabel("Página atual: 0 de 0")
        current_page_layout.addWidget(self.current_page_label)
        main_layout.addLayout(current_page_layout)

        # Botão Novo Cadastro
        self.new_button = QPushButton(self.get_new_button_text())
        self.new_button.setStyleSheet("font-weight: bold; background-color: #ADD8E6; padding: 5px; margin-top: 10px;")
        main_layout.addWidget(self.new_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.new_button.clicked.connect(self.show_form)

        self.table_widget.setLayout(main_layout)

    def get_title(self):
        raise NotImplementedError("Subclasse deve implementar get_title().")

    def get_new_button_text(self):
        raise NotImplementedError("Subclasse deve implementar get_new_button_text().")

    def init_search_fields(self):
        # Subclasse deve adicionar itens no self.search_field_combo
        raise NotImplementedError("Subclasse deve implementar init_search_fields().")

    def initFormUI(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Campos específicos da subclasse
        self.initFormFields(form_layout)

        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.save_record_action)
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.cancel_form)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        self.form_widget.setLayout(layout)

    def initEditFormUI(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.edit_id = None

        # Campos de edição, similares ao de criação
        self.initEditFormFields(form_layout)

        button_layout = QHBoxLayout()
        self.update_button = QPushButton("Confirmar Edição")
        self.update_button.clicked.connect(self.update_record_action)
        self.cancel_edit_button = QPushButton("Cancelar")
        self.cancel_edit_button.clicked.connect(self.cancel_form)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.cancel_edit_button)

        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        self.edit_form_widget.setLayout(layout)

    def load_data(self):
        conn = create_connection()
        cursor = conn.cursor()
        # Conta total de registros
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

        query = self.build_record_query(count_only=False)
        cursor.execute(query)
        records = cursor.fetchall()
        self.table.setRowCount(len(records))

        self.fill_table(records)
        conn.close()

        self.update_pagination_bar()
        self.update_current_page_label()

    def fill_table(self, records):
        """Preenche a tabela com os registros. Deve ser sobrescrito se precisar de lógica extra."""
        for row_idx, row_data in enumerate(records):
            for col_idx, col_data in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
            self.add_actions_to_row(row_idx, row_data)
    
    def add_actions_to_row(self, row_idx, row_data):
        raise NotImplementedError("Subclasse deve implementar add_actions_to_row().")

    def update_current_page_label(self):
        if self.total_pages == 0:
            self.current_page_label.setText("Página atual: 0 de 0")
        else:
            self.current_page_label.setText(f"Página atual: {self.current_page + 1} de {self.total_pages}")

    def update_pagination_bar(self):
        current_page_1 = self.current_page + 1

        self.first_button.setEnabled(self.total_pages > 1 and current_page_1 > 1)
        self.prev_button.setEnabled(self.total_pages > 1 and current_page_1 > 1)
        self.next_button.setEnabled(self.total_pages > 1 and current_page_1 < self.total_pages)
        self.last_button.setEnabled(self.total_pages > 1 and current_page_1 < self.total_pages)

        if self.total_pages <= 1:
            # Apenas 1 ou 0 páginas
            if self.total_pages == 1:
                # 1 página
                self.page_buttons[0].setText("1")
                self.page_buttons[0].setStyleSheet("font-weight: bold; background-color: #DDD;")
                self.page_buttons[0].setEnabled(False)
                for btn in self.page_buttons[1:]:
                    btn.setText("")
                    btn.setEnabled(False)
            else:
                # 0 páginas
                for btn in self.page_buttons:
                    btn.setText("")
                    btn.setEnabled(False)
            return

        # total_pages > 1
        if self.total_pages <= 5:
            pages = list(range(1, self.total_pages + 1))
        else:
            current = current_page_1
            if current <= 3:
                pages = list(range(1, 6))
            elif current > self.total_pages - 3:
                pages = list(range(self.total_pages - 4, self.total_pages + 1))
            else:
                pages = list(range(current - 2, current + 3))

        for i, btn in enumerate(self.page_buttons):
            try:
                btn.clicked.disconnect()
            except TypeError:
                pass
            if i < len(pages):
                p = pages[i]
                btn.setText(str(p))
                btn.setEnabled(True)
                btn.setStyleSheet("font-weight: normal;")
                if p == current_page_1:
                    btn.setStyleSheet("font-weight: bold; background-color: #DDD;")
                    btn.setEnabled(False)
                else:
                    btn.clicked.connect(lambda checked, page=p: self.go_to_page(page))
            else:
                btn.setText("")
                btn.setEnabled(False)

    def go_to_page(self, page):
        if self.total_pages == 0:
            return
        if page < 1:
            page = 1
        if page > self.total_pages:
            page = self.total_pages
        self.current_page = page - 1
        self.load_data()

    def header_clicked(self, logicalIndex):
        mapping = self.get_column_mapping()
        if logicalIndex in mapping:
            column_name = mapping[logicalIndex]
            if self.order_by_column == column_name:
                self.order_direction = "DESC" if self.order_direction == "ASC" else "ASC"
            else:
                self.order_by_column = column_name
                self.order_direction = "ASC"
            self.current_page = 0
            self.load_data()

    def apply_filter(self):
        field = self.search_field_combo.currentData()
        value = self.search_input.text().strip()
        if value:
            self.filter_field = field
            self.filter_value = value
        else:
            self.filter_field = None
            self.filter_value = None
        self.current_page = 0
        self.load_data()

    def clear_filter(self):
        self.filter_field = None
        self.filter_value = None
        self.search_input.clear()
        self.current_page = 0
        self.load_data()

    def goto_page(self):
        if self.total_pages == 0:
            QMessageBox.warning(self, "Erro", "Não há páginas disponíveis.")
            return
        val = self.goto_page_input.text().strip()
        if val.isdigit():
            page = int(val)
            if page < 1:
                page = 1
            if page > self.total_pages:
                page = self.total_pages
            self.go_to_page(page)
        else:
            QMessageBox.warning(self, "Erro", "Por favor, insira um número de página válido.")

    def show_form(self):
        self.clear_form()
        self.stacked_layout.setCurrentWidget(self.form_widget)

    def cancel_form(self):
        self.stacked_layout.setCurrentWidget(self.table_widget)

    def save_record_action(self):
        data = self.collect_form_data()
        valid, msg = self.validate_data(data)
        if not valid:
            QMessageBox.warning(self, "Erro", msg)
            return
        self.save_record(data)
        self.stacked_layout.setCurrentWidget(self.table_widget)
        self.load_data()

    def update_record_action(self):
        data = self.collect_edit_form_data()
        valid, msg = self.validate_data(data)
        if not valid:
            QMessageBox.warning(self, "Erro", msg)
            return
        self.update_record(self.edit_id, data)
        self.stacked_layout.setCurrentWidget(self.table_widget)
        self.load_data()


    def clear_form(self):
        raise NotImplementedError("Subclasse deve implementar clear_form().")

    def clear_edit_form(self):
        raise NotImplementedError("Subclasse deve implementar clear_edit_form().")

    def collect_form_data(self):
        raise NotImplementedError("Subclasse deve implementar collect_form_data().")

    def collect_edit_form_data(self):
        raise NotImplementedError("Subclasse deve implementar collect_edit_form_data().")

    def edit_record(self, record_id):
        record = self.load_record(record_id)
        if record:
            self.edit_id = record_id
            self.fill_edit_form(record)
            self.stacked_layout.setCurrentWidget(self.edit_form_widget)
        else:
            QMessageBox.warning(self, "Erro", "Registro não encontrado.")

    def fill_edit_form(self, record):
        raise NotImplementedError("Subclasse deve implementar fill_edit_form().")