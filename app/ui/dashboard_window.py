from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QWidget,
    QPushButton,
    QSpinBox
)
from PySide6.QtCore import Qt
from app.dashboard_manager import DashboardManager


class DashboardWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dashboard - ENFER-SICOP PRO")
        self.setGeometry(100, 100, 1200, 800)
        self.dashboard = DashboardManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Título
        titulo = QLabel("Dashboard - Estadísticas del Sistema")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #0B5ED7;")
        layout.addWidget(titulo)

        # Tabs
        tabs = QTabWidget()

        # Tab 1: Resumen General
        tab_resumen = self._crear_tab_resumen()
        tabs.addTab(tab_resumen, "Resumen General")

        # Tab 2: Por Curso
        tab_cursos = self._crear_tab_cursos()
        tabs.addTab(tab_cursos, "Estadísticas por Curso")

        # Tab 3: Actividad Reciente
        tab_actividad = self._crear_tab_actividad()
        tabs.addTab(tab_actividad, "Actividad Reciente")

        # Tab 4: Análisis
        tab_analisis = self._crear_tab_analisis()
        tabs.addTab(tab_analisis, "Análisis")

        layout.addWidget(tabs)
        self.setLayout(layout)

    def _crear_tab_resumen(self):
        """Crea la pestaña de resumen general"""
        widget = QWidget()
        layout = QVBoxLayout()

        stats = self.dashboard.obtener_estadisticas_generales()

        # Cuadros de estadísticas
        grid_layout = QHBoxLayout()

        # Cuadro 1: Cursos
        grupo1 = QGroupBox("📚 Cursos")
        layout1 = QVBoxLayout()
        layout1.addWidget(QLabel(f"<b>Total:</b> {stats['total_cursos']}"))
        grupo1.setLayout(layout1)
        grid_layout.addWidget(grupo1)

        # Cuadro 2: Participantes
        grupo2 = QGroupBox("👥 Participantes")
        layout2 = QVBoxLayout()
        layout2.addWidget(QLabel(f"<b>Total:</b> {stats['total_participantes']}"))
        grupo2.setLayout(layout2)
        grid_layout.addWidget(grupo2)

        # Cuadro 3: Vouchers
        grupo3 = QGroupBox("💳 Vouchers")
        layout3 = QVBoxLayout()
        layout3.addWidget(QLabel(f"<b>Total:</b> {stats['total_vouchers']}"))
        layout3.addWidget(QLabel(f"<b>Verificados:</b> {stats['vouchers_verificados']}"))
        layout3.addWidget(QLabel(f"<b>% Verificación:</b> {stats['porcentaje_verificacion']:.1f}%"))
        grupo3.setLayout(layout3)
        grid_layout.addWidget(grupo3)

        # Cuadro 4: Certificados
        grupo4 = QGroupBox("📄 Certificados")
        layout4 = QVBoxLayout()
        layout4.addWidget(QLabel(f"<b>Total:</b> {stats['total_certificados']}"))
        layout4.addWidget(QLabel(f"<b>Generados:</b> {stats['certificados_generados']}"))
        layout4.addWidget(QLabel(f"<b>% Certificación:</b> {stats['porcentaje_certificacion']:.1f}%"))
        grupo4.setLayout(layout4)
        grid_layout.addWidget(grupo4)

        layout.addLayout(grid_layout)

        # Ingresos
        ingresos = self.dashboard.obtener_ingresos_totales()
        grupo_ingresos = QGroupBox("💰 Ingresos Totales")
        layout_ingresos = QVBoxLayout()
        layout_ingresos.addWidget(QLabel(f"<b>S/. {ingresos:.2f}</b>"))
        grupo_ingresos.setLayout(layout_ingresos)
        layout.addWidget(grupo_ingresos)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _crear_tab_cursos(self):
        """Crea la pestaña de estadísticas por curso"""
        widget = QWidget()
        layout = QVBoxLayout()

        stats_cursos = self.dashboard.obtener_estadisticas_por_curso()

        tabla = QTableWidget()
        tabla.setColumnCount(8)
        tabla.setHorizontalHeaderLabels([
            "ID", "Curso", "Participantes", "Vouchers", "Certificados",
            "Monto Total", "% Vouchers", "% Certificados"
        ])

        tabla.setRowCount(len(stats_cursos))
        for row, stat in enumerate(stats_cursos):
            tabla.setItem(row, 0, QTableWidgetItem(str(stat['curso_id'])))
            tabla.setItem(row, 1, QTableWidgetItem(stat['curso_nombre']))
            tabla.setItem(row, 2, QTableWidgetItem(str(stat['participantes'])))
            tabla.setItem(row, 3, QTableWidgetItem(str(stat['vouchers'])))
            tabla.setItem(row, 4, QTableWidgetItem(str(stat['certificados'])))
            tabla.setItem(row, 5, QTableWidgetItem(f"S/. {stat['monto_total']:.2f}"))
            tabla.setItem(row, 6, QTableWidgetItem(f"{stat['porcentaje_vouchers']:.1f}%"))
            tabla.setItem(row, 7, QTableWidgetItem(f"{stat['porcentaje_certificados']:.1f}%"))

        tabla.resizeColumnsToContents()
        layout.addWidget(tabla)
        widget.setLayout(layout)
        return widget

    def _crear_tab_actividad(self):
        """Crea la pestaña de actividad reciente"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Selector de período
        periodo_layout = QHBoxLayout()
        periodo_layout.addWidget(QLabel("Período (días):"))
        spin_periodo = QSpinBox()
        spin_periodo.setValue(7)
        spin_periodo.setMaximum(365)
        btn_actualizar = QPushButton("Actualizar")
        periodo_layout.addWidget(spin_periodo)
        periodo_layout.addWidget(btn_actualizar)
        layout.addLayout(periodo_layout)

        # Tabla de actividad
        tabla_actividad = QTableWidget()
        tabla_actividad.setColumnCount(4)
        tabla_actividad.setHorizontalHeaderLabels([
            "Período", "Participantes Nuevos", "Vouchers Nuevos", "Certificados Nuevos"
        ])
        tabla_actividad.setRowCount(1)

        def actualizar_actividad():
            dias = spin_periodo.value()
            actividad = self.dashboard.obtener_actividad_reciente(dias)
            tabla_actividad.setItem(0, 0, QTableWidgetItem(f"Últimos {dias} días"))
            tabla_actividad.setItem(0, 1, QTableWidgetItem(str(actividad['participantes_nuevos'])))
            tabla_actividad.setItem(0, 2, QTableWidgetItem(str(actividad['vouchers_nuevos'])))
            tabla_actividad.setItem(0, 3, QTableWidgetItem(str(actividad['certificados_nuevos'])))

        btn_actualizar.clicked.connect(actualizar_actividad)
        actualizar_actividad()  # Cargar datos iniciales

        layout.addWidget(tabla_actividad)
        widget.setLayout(layout)
        return widget

    def _crear_tab_analisis(self):
        """Crea la pestaña de análisis"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Top Cursos
        grupo_top = QGroupBox("🏆 Top 5 Cursos por Participantes")
        layout_top = QVBoxLayout()
        top_cursos = self.dashboard.obtener_top_cursos(5)
        for curso in top_cursos:
            layout_top.addWidget(QLabel(f"{curso['curso_nombre']}: {curso['participantes']} participantes"))
        grupo_top.setLayout(layout_top)
        layout.addWidget(grupo_top)

        # Participantes sin certificado
        grupo_sin_cert = QGroupBox("⚠️ Participantes sin Certificado")
        layout_sin_cert = QVBoxLayout()
        sin_cert = self.dashboard.obtener_participantes_sin_certificado()
        
        tabla_sin_cert = QTableWidget()
        tabla_sin_cert.setColumnCount(4)
        tabla_sin_cert.setHorizontalHeaderLabels(["ID", "Nombre", "Email", "Curso"])
        tabla_sin_cert.setRowCount(len(sin_cert))

        for row, participante in enumerate(sin_cert):
            tabla_sin_cert.setItem(row, 0, QTableWidgetItem(str(participante['id'])))
            tabla_sin_cert.setItem(row, 1, QTableWidgetItem(participante['nombre']))
            tabla_sin_cert.setItem(row, 2, QTableWidgetItem(participante['email']))
            tabla_sin_cert.setItem(row, 3, QTableWidgetItem(participante['curso']))

        layout_sin_cert.addWidget(tabla_sin_cert)
        grupo_sin_cert.setLayout(layout_sin_cert)
        layout.addWidget(grupo_sin_cert)

        layout.addStretch()
        widget.setLayout(layout)
        return widget
