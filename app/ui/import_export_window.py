from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
    QMessageBox,
    QComboBox
)
from app.import_export_manager import ImportExportManager


class ImportExportWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Importación/Exportación de Datos")
        self.setGeometry(100, 100, 900, 600)
        self.manager = ImportExportManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Título
        titulo = QLabel("Importación/Exportación de Datos")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #0B5ED7;")
        layout.addWidget(titulo)

        # Sección de Importación
        seccion_importar = QVBoxLayout()
        titulo_import = QLabel("📥 IMPORTAR DATOS")
        titulo_import.setStyleSheet("font-weight: bold; color: #0B5ED7;")
        seccion_importar.addWidget(titulo_import)

        # Importar Participantes
        layout_import_part = QHBoxLayout()
        self.combo_curso_import = QComboBox()
        self._cargar_cursos()
        btn_import_part = QPushButton("Importar Participantes desde Excel")
        btn_import_part.clicked.connect(self.importar_participantes)
        layout_import_part.addWidget(QLabel("Curso:"))
        layout_import_part.addWidget(self.combo_curso_import)
        layout_import_part.addWidget(btn_import_part)
        seccion_importar.addLayout(layout_import_part)

        # Importar Vouchers
        layout_import_vouch = QHBoxLayout()
        btn_import_vouch = QPushButton("Importar Vouchers desde Excel")
        btn_import_vouch.clicked.connect(self.importar_vouchers)
        layout_import_vouch.addWidget(btn_import_vouch)
        seccion_importar.addLayout(layout_import_vouch)

        layout.addLayout(seccion_importar)
        layout.addSpacing(20)

        # Sección de Exportación
        seccion_exportar = QVBoxLayout()
        titulo_export = QLabel("📤 EXPORTAR DATOS")
        titulo_export.setStyleSheet("font-weight: bold; color: #0B5ED7;")
        seccion_exportar.addWidget(titulo_export)

        # Tipo de reporte
        layout_tipo = QHBoxLayout()
        self.combo_tipo_reporte = QComboBox()
        self.combo_tipo_reporte.addItems(["Completo", "Participantes", "Vouchers", "Certificados"])
        layout_tipo.addWidget(QLabel("Tipo de reporte:"))
        layout_tipo.addWidget(self.combo_tipo_reporte)
        seccion_exportar.addLayout(layout_tipo)

        # Botones de exportación
        layout_export = QHBoxLayout()
        btn_export_excel = QPushButton("📊 Exportar a Excel")
        btn_export_excel.clicked.connect(self.exportar_excel)
        layout_export.addWidget(btn_export_excel)
        seccion_exportar.addLayout(layout_export)

        layout.addLayout(seccion_exportar)
        layout.addStretch()
        self.setLayout(layout)

    def _cargar_cursos(self):
        """Carga los cursos en el combo"""
        from app.db_init import get_session
        from app.models import Curso
        session = get_session()
        cursos = session.query(Curso).all()
        for curso in cursos:
            self.combo_curso_import.addItem(curso.nombre, curso.id)

    def importar_participantes(self):
        archivo_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo Excel", "", "Excel Files (*.xlsx)"
        )
        if not archivo_path:
            return

        curso_id = self.combo_curso_import.currentData()
        resultado = self.manager.importar_participantes_excel(archivo_path, curso_id)

        mensaje = f"""Importación completada:
        
✅ Exitosos: {resultado['exitosos']}
⚠️ Duplicados: {resultado['duplicados']}
❌ Errores: {resultado['errores']}

Detalles:
" + "\n".join(resultado['detalles'][:10])

        QMessageBox.information(self, "Importación Participantes", mensaje)

    def importar_vouchers(self):
        archivo_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo Excel", "", "Excel Files (*.xlsx)"
        )
        if not archivo_path:
            return

        resultado = self.manager.importar_vouchers_excel(archivo_path)

        mensaje = f"""Importación completada:
        
✅ Exitosos: {resultado['exitosos']}
⚠️ Duplicados: {resultado['duplicados']}
❌ Errores: {resultado['errores']}

Detalles:
" + "\n".join(resultado['detalles'][:10])

        QMessageBox.information(self, "Importación Vouchers", mensaje)

    def exportar_excel(self):
        archivo_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar archivo Excel", "", "Excel Files (*.xlsx)"
        )
        if not archivo_path:
            return

        tipo_reporte = self.combo_tipo_reporte.currentText().lower()
        resultado = self.manager.exportar_reporte_excel(archivo_path, tipo_reporte)

        if resultado["success"]:
            QMessageBox.information(self, "Éxito", f"Archivo guardado en: {archivo_path}")
        else:
            QMessageBox.critical(self, "Error", resultado["error"])
