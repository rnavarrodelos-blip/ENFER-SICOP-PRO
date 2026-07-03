from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout
)
from app.ui.cursos_window import CursosWindow
from app.ui.participantes_window import ParticipantesWindow
from app.ui.vouchers_window import VouchersWindow
from app.ui.certificados_window import CertificadosWindow
from app.ui.reportes_window import ReportesWindow
from app.db_init import init_db


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Inicializar base de datos
        init_db()

        self.setWindowTitle("ENFER-SICOP PRO")
        self.resize(1400, 850)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout()

        titulo = QLabel("ENFER-SICOP PRO")
        titulo.setStyleSheet("""
            font-size:28px;
            font-weight:bold;
            color:#0B5ED7;
        """)

        subtitulo = QLabel(
            "Sistema Inteligente de Gestión de Cursos de Enfermería"
        )

        botones = QHBoxLayout()

        btnCurso = QPushButton("📚 Cursos")
        btnCurso.clicked.connect(self.abrir_cursos)
        
        btnParticipantes = QPushButton("👥 Participantes")
        btnParticipantes.clicked.connect(self.abrir_participantes)
        
        btnVouchers = QPushButton("💳 Vouchers")
        btnVouchers.clicked.connect(self.abrir_vouchers)
        
        btnCertificados = QPushButton("📄 Certificados")
        btnCertificados.clicked.connect(self.abrir_certificados)
        
        btnReportes = QPushButton("📊 Reportes")
        btnReportes.clicked.connect(self.abrir_reportes)

        botones.addWidget(btnCurso)
        botones.addWidget(btnParticipantes)
        botones.addWidget(btnVouchers)
        botones.addWidget(btnCertificados)
        botones.addWidget(btnReportes)

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addLayout(botones)
        layout.addStretch()

        central.setLayout(layout)

    def abrir_cursos(self):
        self.cursos_window = CursosWindow(self)
        self.cursos_window.show()

    def abrir_participantes(self):
        self.participantes_window = ParticipantesWindow(self)
        self.participantes_window.show()

    def abrir_vouchers(self):
        self.vouchers_window = VouchersWindow(self)
        self.vouchers_window.show()

    def abrir_certificados(self):
        self.certificados_window = CertificadosWindow(self)
        self.certificados_window.show()

    def abrir_reportes(self):
        self.reportes_window = ReportesWindow(self)
        self.reportes_window.show()
