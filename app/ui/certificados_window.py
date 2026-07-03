from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QFileDialog
)
from datetime import datetime
from app.db_init import get_session
from app.models import Certificado, Participante, Curso


class CertificadosWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestión de Certificados")
        self.setGeometry(100, 100, 900, 600)
        self.session = get_session()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Formulario
        form_layout = QHBoxLayout()
        
        self.participante_combo = QComboBox()
        self.cargar_participantes_combo()
        
        self.curso_combo = QComboBox()
        self.cargar_cursos_combo()
        
        btn_generar = QPushButton("Generar Certificado")
        btn_generar.clicked.connect(self.generar_certificado)

        form_layout.addWidget(QLabel("Participante:"))
        form_layout.addWidget(self.participante_combo)
        form_layout.addWidget(QLabel("Curso:"))
        form_layout.addWidget(self.curso_combo)
        form_layout.addWidget(btn_generar)

        # Tabla de certificados
        self.tabla_certificados = QTableWidget()
        self.tabla_certificados.setColumnCount(5)
        self.tabla_certificados.setHorizontalHeaderLabels(["ID", "Número", "Participante", "Curso", "Estado"])
        
        layout.addLayout(form_layout)
        layout.addWidget(self.tabla_certificados)
        self.setLayout(layout)
        
        self.cargar_certificados()

    def cargar_participantes_combo(self):
        participantes = self.session.query(Participante).all()
        for participante in participantes:
            self.participante_combo.addItem(participante.nombre, participante.id)

    def cargar_cursos_combo(self):
        cursos = self.session.query(Curso).all()
        for curso in cursos:
            self.curso_combo.addItem(curso.nombre, curso.id)

    def generar_certificado(self):
        participante_id = self.participante_combo.currentData()
        curso_id = self.curso_combo.currentData()

        if participante_id and curso_id:
            numero_certificado = f"CERT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            nuevo_certificado = Certificado(
                numero_certificado=numero_certificado,
                participante_id=participante_id,
                curso_id=curso_id
            )
            self.session.add(nuevo_certificado)
            self.session.commit()
            self.cargar_certificados()

    def cargar_certificados(self):
        certificados = self.session.query(Certificado).all()
        self.tabla_certificados.setRowCount(len(certificados))

        for row, certificado in enumerate(certificados):
            participante_nombre = certificado.participante.nombre if certificado.participante else "N/A"
            curso_nombre = certificado.curso.nombre if certificado.curso else "N/A"
            self.tabla_certificados.setItem(row, 0, QTableWidgetItem(str(certificado.id)))
            self.tabla_certificados.setItem(row, 1, QTableWidgetItem(certificado.numero_certificado))
            self.tabla_certificados.setItem(row, 2, QTableWidgetItem(participante_nombre))
            self.tabla_certificados.setItem(row, 3, QTableWidgetItem(curso_nombre))
            self.tabla_certificados.setItem(row, 4, QTableWidgetItem(certificado.estado))
