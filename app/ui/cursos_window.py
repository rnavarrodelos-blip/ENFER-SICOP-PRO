from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QDialog,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox
)
from PySide6.QtCore import Qt
from app.db_init import get_session
from app.models import Curso


class CursosWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestión de Cursos")
        self.setGeometry(100, 100, 800, 600)
        self.session = get_session()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Formulario
        form_layout = QHBoxLayout()
        
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre del curso")
        
        self.horas_input = QSpinBox()
        self.horas_input.setPlaceholderText("Horas")
        
        self.precio_input = QDoubleSpinBox()
        self.precio_input.setPlaceholderText("Precio")
        
        btn_agregar = QPushButton("Agregar Curso")
        btn_agregar.clicked.connect(self.agregar_curso)

        form_layout.addWidget(QLabel("Nombre:"))
        form_layout.addWidget(self.nombre_input)
        form_layout.addWidget(QLabel("Horas:"))
        form_layout.addWidget(self.horas_input)
        form_layout.addWidget(QLabel("Precio:"))
        form_layout.addWidget(self.precio_input)
        form_layout.addWidget(btn_agregar)

        # Tabla de cursos
        self.tabla_cursos = QTableWidget()
        self.tabla_cursos.setColumnCount(4)
        self.tabla_cursos.setHorizontalHeaderLabels(["ID", "Nombre", "Horas", "Precio"])
        
        layout.addLayout(form_layout)
        layout.addWidget(self.tabla_cursos)
        self.setLayout(layout)
        
        self.cargar_cursos()

    def agregar_curso(self):
        nombre = self.nombre_input.text()
        horas = self.horas_input.value()
        precio = self.precio_input.value()

        if nombre:
            nuevo_curso = Curso(nombre=nombre, horas=horas, precio=precio)
            self.session.add(nuevo_curso)
            self.session.commit()
            self.nombre_input.clear()
            self.horas_input.setValue(0)
            self.precio_input.setValue(0.0)
            self.cargar_cursos()

    def cargar_cursos(self):
        cursos = self.session.query(Curso).all()
        self.tabla_cursos.setRowCount(len(cursos))

        for row, curso in enumerate(cursos):
            self.tabla_cursos.setItem(row, 0, QTableWidgetItem(str(curso.id)))
            self.tabla_cursos.setItem(row, 1, QTableWidgetItem(curso.nombre))
            self.tabla_cursos.setItem(row, 2, QTableWidgetItem(str(curso.horas)))
            self.tabla_cursos.setItem(row, 3, QTableWidgetItem(str(curso.precio)))
