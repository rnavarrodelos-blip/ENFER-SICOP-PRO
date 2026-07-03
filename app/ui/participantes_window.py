from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QComboBox
)
from app.db_init import get_session
from app.models import Participante, Curso


class ParticipantesWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestión de Participantes")
        self.setGeometry(100, 100, 900, 600)
        self.session = get_session()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Formulario
        form_layout = QHBoxLayout()
        
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre")
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        
        self.identificacion_input = QLineEdit()
        self.identificacion_input.setPlaceholderText("Identificación")
        
        self.curso_combo = QComboBox()
        self.cargar_cursos_combo()
        
        btn_agregar = QPushButton("Agregar Participante")
        btn_agregar.clicked.connect(self.agregar_participante)

        form_layout.addWidget(QLabel("Nombre:"))
        form_layout.addWidget(self.nombre_input)
        form_layout.addWidget(QLabel("Email:"))
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(QLabel("ID:"))
        form_layout.addWidget(self.identificacion_input)
        form_layout.addWidget(QLabel("Curso:"))
        form_layout.addWidget(self.curso_combo)
        form_layout.addWidget(btn_agregar)

        # Tabla de participantes
        self.tabla_participantes = QTableWidget()
        self.tabla_participantes.setColumnCount(5)
        self.tabla_participantes.setHorizontalHeaderLabels(["ID", "Nombre", "Email", "Curso", "Estado"])
        
        layout.addLayout(form_layout)
        layout.addWidget(self.tabla_participantes)
        self.setLayout(layout)
        
        self.cargar_participantes()

    def cargar_cursos_combo(self):
        cursos = self.session.query(Curso).all()
        for curso in cursos:
            self.curso_combo.addItem(curso.nombre, curso.id)

    def agregar_participante(self):
        nombre = self.nombre_input.text()
        email = self.email_input.text()
        identificacion = self.identificacion_input.text()
        curso_id = self.curso_combo.currentData()

        if nombre and email:
            nuevo_participante = Participante(
                nombre=nombre,
                email=email,
                identificacion=identificacion,
                curso_id=curso_id
            )
            self.session.add(nuevo_participante)
            self.session.commit()
            self.nombre_input.clear()
            self.email_input.clear()
            self.identificacion_input.clear()
            self.cargar_participantes()

    def cargar_participantes(self):
        participantes = self.session.query(Participante).all()
        self.tabla_participantes.setRowCount(len(participantes))

        for row, participante in enumerate(participantes):
            curso_nombre = participante.curso.nombre if participante.curso else "N/A"
            self.tabla_participantes.setItem(row, 0, QTableWidgetItem(str(participante.id)))
            self.tabla_participantes.setItem(row, 1, QTableWidgetItem(participante.nombre))
            self.tabla_participantes.setItem(row, 2, QTableWidgetItem(participante.email))
            self.tabla_participantes.setItem(row, 3, QTableWidgetItem(curso_nombre))
            self.tabla_participantes.setItem(row, 4, QTableWidgetItem(participante.estado))
