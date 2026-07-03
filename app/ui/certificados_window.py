from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QMessageBox,
    QCheckBox
)
from PySide6.QtCore import Qt
from app.db_init import get_session
from app.models import Certificado, Participante, Curso, Voucher
from app.certificado_generator import CertificadoGenerator
import os


class CertificadosWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generación de Certificados Word")
        self.setGeometry(100, 100, 1000, 700)
        self.session = get_session()
        self.generator = CertificadoGenerator()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Título
        titulo = QLabel("Generación de Certificados en Word")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #0B5ED7;")
        layout.addWidget(titulo)

        # Sección de generación individual
        form_layout = QHBoxLayout()
        
        self.participante_combo = QComboBox()
        self.cargar_participantes_combo()
        
        self.curso_combo = QComboBox()
        self.cargar_cursos_combo()
        
        btn_generar = QPushButton("📄 Generar Certificado")
        btn_generar.clicked.connect(self.generar_certificado_individual)
        
        form_layout.addWidget(QLabel("Participante:"))
        form_layout.addWidget(self.participante_combo)
        form_layout.addWidget(QLabel("Curso:"))
        form_layout.addWidget(self.curso_combo)
        form_layout.addWidget(btn_generar)
        
        layout.addLayout(form_layout)

        # Sección de generación por lote
        lote_layout = QHBoxLayout()
        self.curso_combo_lote = QComboBox()
        self.cargar_cursos_combo_lote()
        btn_lote = QPushButton("📦 Generar Lote (Todos con Voucher)")
        btn_lote.clicked.connect(self.generar_certificados_lote)
        lote_layout.addWidget(QLabel("Generar para Curso:"))
        lote_layout.addWidget(self.curso_combo_lote)
        lote_layout.addWidget(btn_lote)
        layout.addLayout(lote_layout)

        # Tabla de certificados generados
        self.tabla_certificados = QTableWidget()
        self.tabla_certificados.setColumnCount(6)
        self.tabla_certificados.setHorizontalHeaderLabels([
            "ID", "Número", "Participante", "Curso", "Estado", "Archivo"
        ])
        layout.addWidget(QLabel("Certificados Generados:"))
        layout.addWidget(self.tabla_certificados)

        # Botón para abrir carpeta de certificados
        btn_abrir_carpeta = QPushButton("📁 Abrir Carpeta de Certificados")
        btn_abrir_carpeta.clicked.connect(self.abrir_carpeta_certificados)
        layout.addWidget(btn_abrir_carpeta)

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

    def cargar_cursos_combo_lote(self):
        cursos = self.session.query(Curso).all()
        for curso in cursos:
            self.curso_combo_lote.addItem(curso.nombre, curso.id)

    def generar_certificado_individual(self):
        participante_id = self.participante_combo.currentData()
        curso_id = self.curso_combo.currentData()

        if not participante_id or not curso_id:
            QMessageBox.warning(self, "Error", "Seleccione participante y curso")
            return

        resultado = self.generator.generar_certificado_word(participante_id, curso_id)

        if resultado["success"]:
            QMessageBox.information(
                self, "Éxito",
                f"✅ Certificado generado exitosamente\n\nArchivo: {resultado['archivo_path']}"
            )
        else:
            if resultado.get("duplicado"):
                QMessageBox.warning(self, "Duplicado", resultado["mensaje"])
            else:
                QMessageBox.critical(self, "Error", resultado["mensaje"])

        self.cargar_certificados()

    def generar_certificados_lote(self):
        curso_id = self.curso_combo_lote.currentData()

        if not curso_id:
            QMessageBox.warning(self, "Error", "Seleccione un curso")
            return

        resultados = self.generator.generar_certificados_lote(curso_id)
        
        exitosos = sum(1 for r in resultados if r["resultado"]["success"])
        duplicados = sum(1 for r in resultados if r["resultado"].get("duplicado"))
        
        mensaje = f"""Procesados: {len(resultados)}
✅ Exitosos: {exitosos}
⚠️ Duplicados: {duplicados}
❌ Errores: {len(resultados) - exitosos - duplicados}"""
        
        QMessageBox.information(self, "Generación por Lote", mensaje)
        self.cargar_certificados()

    def cargar_certificados(self):
        certificados = self.session.query(Certificado).all()
        self.tabla_certificados.setRowCount(len(certificados))

        for row, certificado in enumerate(certificados):
            participante_nombre = certificado.participante.nombre if certificado.participante else "N/A"
            curso_nombre = certificado.curso.nombre if certificado.curso else "N/A"
            archivo_nombre = os.path.basename(certificado.archivo_path) if certificado.archivo_path else "N/A"
            
            self.tabla_certificados.setItem(row, 0, QTableWidgetItem(str(certificado.id)))
            self.tabla_certificados.setItem(row, 1, QTableWidgetItem(certificado.numero_certificado))
            self.tabla_certificados.setItem(row, 2, QTableWidgetItem(participante_nombre))
            self.tabla_certificados.setItem(row, 3, QTableWidgetItem(curso_nombre))
            self.tabla_certificados.setItem(row, 4, QTableWidgetItem(certificado.estado))
            self.tabla_certificados.setItem(row, 5, QTableWidgetItem(archivo_nombre))

    def abrir_carpeta_certificados(self):
        if os.path.exists('certificados'):
            os.startfile('certificados' if os.name == 'nt' else 'open certificados')
        else:
            QMessageBox.information(self, "Info", "No hay certificados generados aún")
