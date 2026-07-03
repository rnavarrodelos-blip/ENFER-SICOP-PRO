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
    QFileDialog
)
from app.db_init import get_session
from app.models import Voucher, Participante


class VouchersWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestión de Vouchers")
        self.setGeometry(100, 100, 1000, 600)
        self.session = get_session()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Formulario
        form_layout = QHBoxLayout()
        
        self.numero_input = QLineEdit()
        self.numero_input.setPlaceholderText("Número de Voucher")
        
        self.participante_combo = QComboBox()
        self.cargar_participantes_combo()
        
        self.monto_input = QDoubleSpinBox()
        self.monto_input.setPlaceholderText("Monto")
        
        btn_cargar_imagen = QPushButton("Cargar Imagen")
        btn_cargar_imagen.clicked.connect(self.cargar_imagen)
        
        btn_agregar = QPushButton("Agregar Voucher")
        btn_agregar.clicked.connect(self.agregar_voucher)

        form_layout.addWidget(QLabel("Número:"))
        form_layout.addWidget(self.numero_input)
        form_layout.addWidget(QLabel("Participante:"))
        form_layout.addWidget(self.participante_combo)
        form_layout.addWidget(QLabel("Monto:"))
        form_layout.addWidget(self.monto_input)
        form_layout.addWidget(btn_cargar_imagen)
        form_layout.addWidget(btn_agregar)

        # Tabla de vouchers
        self.tabla_vouchers = QTableWidget()
        self.tabla_vouchers.setColumnCount(6)
        self.tabla_vouchers.setHorizontalHeaderLabels(["ID", "Número", "Participante", "Monto", "Estado", "Verificado"])
        
        layout.addLayout(form_layout)
        layout.addWidget(self.tabla_vouchers)
        self.setLayout(layout)
        
        self.imagen_path = None
        self.cargar_vouchers()

    def cargar_participantes_combo(self):
        participantes = self.session.query(Participante).all()
        for participante in participantes:
            self.participante_combo.addItem(participante.nombre, participante.id)

    def cargar_imagen(self):
        file_dialog = QFileDialog()
        self.imagen_path, _ = file_dialog.getOpenFileName(self, "Seleccionar imagen de voucher")

    def agregar_voucher(self):
        numero = self.numero_input.text()
        participante_id = self.participante_combo.currentData()
        monto = self.monto_input.value()

        if numero and participante_id:
            nuevo_voucher = Voucher(
                numero_voucher=numero,
                participante_id=participante_id,
                monto=monto,
                imagen_path=self.imagen_path
            )
            self.session.add(nuevo_voucher)
            self.session.commit()
            self.numero_input.clear()
            self.monto_input.setValue(0.0)
            self.imagen_path = None
            self.cargar_vouchers()

    def cargar_vouchers(self):
        vouchers = self.session.query(Voucher).all()
        self.tabla_vouchers.setRowCount(len(vouchers))

        for row, voucher in enumerate(vouchers):
            participante_nombre = voucher.participante.nombre if voucher.participante else "N/A"
            verified = "Sí" if voucher.verified else "No"
            self.tabla_vouchers.setItem(row, 0, QTableWidgetItem(str(voucher.id)))
            self.tabla_vouchers.setItem(row, 1, QTableWidgetItem(voucher.numero_voucher))
            self.tabla_vouchers.setItem(row, 2, QTableWidgetItem(participante_nombre))
            self.tabla_vouchers.setItem(row, 3, QTableWidgetItem(str(voucher.monto)))
            self.tabla_vouchers.setItem(row, 4, QTableWidgetItem(voucher.estado))
            self.tabla_vouchers.setItem(row, 5, QTableWidgetItem(verified))
