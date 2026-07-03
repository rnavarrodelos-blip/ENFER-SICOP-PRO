from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout
)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

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
        btnParticipantes = QPushButton("👥 Participantes")
        btnVouchers = QPushButton("💳 Vouchers")
        btnCertificados = QPushButton("📄 Certificados")
        btnReportes = QPushButton("📊 Reportes")

        botones.addWidget(btnCurso)
        botones.addWidget(btnParticipantes)
        botones.addWidget(btnVouchers)
        botones.addWidget(btnCertificados)
        botones.addWidget(btnReportes)

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addLayout(botones)

        central.setLayout(layout)
