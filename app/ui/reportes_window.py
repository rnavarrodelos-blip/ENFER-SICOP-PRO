from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QFileDialog
)
from PySide6.QtCore import Qt
from datetime import datetime, timedelta
from app.db_init import get_session
from app.models import Participante, Certificado, Voucher, Curso


class ReportesWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reportes y Análisis")
        self.setGeometry(100, 100, 1000, 700)
        self.session = get_session()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Tabs
        tabs = QTabWidget()

        # Tab 1: Resumen General
        tab_resumen = QWidget()
        resumen_layout = QVBoxLayout()
        btn_resumen = QPushButton("Generar Resumen General")
        btn_resumen.clicked.connect(self.generar_resumen)
        self.label_resumen = QLabel("")
        resumen_layout.addWidget(btn_resumen)
        resumen_layout.addWidget(self.label_resumen)
        tab_resumen.setLayout(resumen_layout)
        tabs.addTab(tab_resumen, "Resumen General")

        # Tab 2: Reporte por Curso
        tab_cursos = QWidget()
        cursos_layout = QVBoxLayout()
        curso_combo = QComboBox()
        self.cargar_cursos_combo(curso_combo)
        btn_curso = QPushButton("Generar Reporte")
        btn_curso.clicked.connect(lambda: self.generar_reporte_curso(curso_combo.currentData()))
        self.tabla_curso = QTableWidget()
        self.tabla_curso.setColumnCount(4)
        self.tabla_curso.setHorizontalHeaderLabels(["Participante", "Estado", "Certificado", "Voucher"])
        cursos_layout.addWidget(QLabel("Seleccionar Curso:"))
        cursos_layout.addWidget(curso_combo)
        cursos_layout.addWidget(btn_curso)
        cursos_layout.addWidget(self.tabla_curso)
        tab_cursos.setLayout(cursos_layout)
        tabs.addTab(tab_cursos, "Reporte por Curso")

        # Tab 3: Exportar Reportes
        tab_exportar = QWidget()
        exportar_layout = QVBoxLayout()
        btn_excel = QPushButton("Exportar a Excel")
        btn_excel.clicked.connect(self.exportar_excel)
        btn_word = QPushButton("Exportar a Word")
        btn_word.clicked.connect(self.exportar_word)
        btn_pdf = QPushButton("Exportar a PDF")
        btn_pdf.clicked.connect(self.exportar_pdf)
        exportar_layout.addWidget(btn_excel)
        exportar_layout.addWidget(btn_word)
        exportar_layout.addWidget(btn_pdf)
        exportar_layout.addStretch()
        tab_exportar.setLayout(exportar_layout)
        tabs.addTab(tab_exportar, "Exportar")

        layout.addWidget(tabs)
        self.setLayout(layout)

    def cargar_cursos_combo(self, combo):
        cursos = self.session.query(Curso).all()
        for curso in cursos:
            combo.addItem(curso.nombre, curso.id)

    def generar_resumen(self):
        total_cursos = self.session.query(Curso).count()
        total_participantes = self.session.query(Participante).count()
        total_certificados = self.session.query(Certificado).count()
        total_vouchers = self.session.query(Voucher).count()

        resumen_text = f"""
        RESUMEN GENERAL DEL SISTEMA
        ============================
        Total de Cursos: {total_cursos}
        Total de Participantes: {total_participantes}
        Total de Certificados Generados: {total_certificados}
        Total de Vouchers Registrados: {total_vouchers}
        """
        self.label_resumen.setText(resumen_text)

    def generar_reporte_curso(self, curso_id):
        if not curso_id:
            return
        
        participantes = self.session.query(Participante).filter_by(curso_id=curso_id).all()
        self.tabla_curso.setRowCount(len(participantes))

        for row, participante in enumerate(participantes):
            certificado = self.session.query(Certificado).filter_by(participante_id=participante.id).first()
            voucher = self.session.query(Voucher).filter_by(participante_id=participante.id).first()
            
            cert_status = "Sí" if certificado else "No"
            voucher_status = "Sí" if voucher else "No"

            self.tabla_curso.setItem(row, 0, QTableWidgetItem(participante.nombre))
            self.tabla_curso.setItem(row, 1, QTableWidgetItem(participante.estado))
            self.tabla_curso.setItem(row, 2, QTableWidgetItem(cert_status))
            self.tabla_curso.setItem(row, 3, QTableWidgetItem(voucher_status))

    def exportar_excel(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar Excel", "", "Excel Files (*.xlsx)")
        if file_path:
            # Aquí irá la lógica de exportación a Excel
            pass

    def exportar_word(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar Word", "", "Word Files (*.docx)")
        if file_path:
            # Aquí irá la lógica de exportación a Word
            pass

    def exportar_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar PDF", "", "PDF Files (*.pdf)")
        if file_path:
            # Aquí irá la lógica de exportación a PDF
            pass
