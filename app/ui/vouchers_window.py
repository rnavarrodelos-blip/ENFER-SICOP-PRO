from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QMessageBox,
    QProgressBar,
    QSpinBox
)
from PySide6.QtCore import Qt
from app.db_init import get_session
from app.models import Voucher, Participante
from app.ocr_processor import OCRProcessor
from app.link_integration import LinkIntegration


class VouchersWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestión de Vouchers")
        self.setGeometry(100, 100, 1200, 700)
        self.session = get_session()
        self.ocr = OCRProcessor()
        self.link = LinkIntegration()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Título
        titulo = QLabel("Gestión de Vouchers con OCR Automático")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #0B5ED7;")
        layout.addWidget(titulo)

        # Sección 1: Carga automática por imagen (OCR)
        seccion_ocr = QHBoxLayout()
        btn_cargar_imagen = QPushButton("📷 Cargar Voucher (OCR)")
        btn_cargar_imagen.clicked.connect(self.cargar_voucher_ocr)
        self.label_archivo = QLabel("No hay archivo seleccionado")
        self.combo_participante_ocr = QComboBox()
        self.cargar_participantes_combo(self.combo_participante_ocr)
        seccion_ocr.addWidget(QLabel("OCR Automático:"))
        seccion_ocr.addWidget(btn_cargar_imagen)
        seccion_ocr.addWidget(self.label_archivo)
        seccion_ocr.addWidget(QLabel("Participante:"))
        seccion_ocr.addWidget(self.combo_participante_ocr)
        layout.addLayout(seccion_ocr)

        # Sección 2: Carga manual por link/formulario
        seccion_manual = QHBoxLayout()
        self.numero_input = QLineEdit()
        self.numero_input.setPlaceholderText("Número de Voucher")
        self.participante_combo = QComboBox()
        self.cargar_participantes_combo(self.participante_combo)
        self.monto_input = QDoubleSpinBox()
        self.monto_input.setPlaceholderText("Monto")
        btn_agregar = QPushButton("➕ Agregar Voucher Manual")
        btn_agregar.clicked.connect(self.agregar_voucher_manual)
        seccion_manual.addWidget(QLabel("Manual:"))
        seccion_manual.addWidget(self.numero_input)
        seccion_manual.addWidget(self.participante_combo)
        seccion_manual.addWidget(self.monto_input)
        seccion_manual.addWidget(btn_agregar)
        layout.addLayout(seccion_manual)

        # Tabla de vouchers
        self.tabla_vouchers = QTableWidget()
        self.tabla_vouchers.setColumnCount(7)
        self.tabla_vouchers.setHorizontalHeaderLabels([
            "ID", "Número", "Participante", "Monto", "Estado", "Verificado", "Duplicado"
        ])
        layout.addWidget(QLabel("Vouchers Registrados:"))
        layout.addWidget(self.tabla_vouchers)

        self.setLayout(layout)
        self.cargar_vouchers()

    def cargar_participantes_combo(self, combo):
        participantes = self.session.query(Participante).all()
        for participante in participantes:
            combo.addItem(participante.nombre, participante.id)

    def cargar_voucher_ocr(self):
        file_dialog = QFileDialog()
        archivo_path, _ = file_dialog.getOpenFileName(
            self, "Seleccionar imagen de voucher", "", "Imágenes (*.jpg *.png *.jpeg)"
        )

        if archivo_path:
            self.label_archivo.setText(archivo_path.split('/')[-1])
            participante_id = self.combo_participante_ocr.currentData()

            # Procesar con OCR
            resultado = self.ocr.procesar_voucher_automatico(archivo_path, participante_id)

            if resultado["success"]:
                QMessageBox.information(
                    self, "Éxito",
                    f"✅ Voucher {resultado['numero_voucher']}\nMonto: S/. {resultado['monto']}"
                )
            else:
                if resultado.get("duplicado"):
                    QMessageBox.warning(self, "Duplicado", resultado["mensaje"])
                else:
                    QMessageBox.critical(self, "Error", resultado["mensaje"])

            self.label_archivo.setText("No hay archivo seleccionado")
            self.cargar_vouchers()

    def agregar_voucher_manual(self):
        numero = self.numero_input.text()
        participante_id = self.participante_combo.currentData()
        monto = self.monto_input.value()

        if not numero:
            QMessageBox.warning(self, "Error", "Ingrese número de voucher")
            return

        datos = {
            'numero_voucher': numero,
            'participante_id': participante_id,
            'monto': monto
        }

        resultado = self.link.procesar_voucher_link(datos)

        if resultado["success"]:
            QMessageBox.information(self, "Éxito", resultado["mensaje"])
            self.numero_input.clear()
            self.monto_input.setValue(0.0)
        else:
            if resultado.get("duplicado"):
                QMessageBox.warning(self, "Duplicado", resultado["mensaje"])
            else:
                QMessageBox.critical(self, "Error", resultado["mensaje"])

        self.cargar_vouchers()

    def cargar_vouchers(self):
        vouchers = self.session.query(Voucher).all()
        self.tabla_vouchers.setRowCount(len(vouchers))

        for row, voucher in enumerate(vouchers):
            participante_nombre = voucher.participante.nombre if voucher.participante else "N/A"
            verified = "✅ Sí" if voucher.verified else "❌ No"
            self.tabla_vouchers.setItem(row, 0, QTableWidgetItem(str(voucher.id)))
            self.tabla_vouchers.setItem(row, 1, QTableWidgetItem(voucher.numero_voucher))
            self.tabla_vouchers.setItem(row, 2, QTableWidgetItem(participante_nombre))
            self.tabla_vouchers.setItem(row, 3, QTableWidgetItem(f"S/. {voucher.monto}"))
            self.tabla_vouchers.setItem(row, 4, QTableWidgetItem(voucher.estado))
            self.tabla_vouchers.setItem(row, 5, QTableWidgetItem(verified))
            # Marcar duplicados potenciales
            duplicados = self.session.query(Voucher).filter_by(
                numero_voucher=voucher.numero_voucher
            ).count()
            duplicado_text = f"⚠️ {duplicados}" if duplicados > 1 else "✓"
            self.tabla_vouchers.setItem(row, 6, QTableWidgetItem(duplicado_text))
