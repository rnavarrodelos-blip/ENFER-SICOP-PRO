from app.db_init import get_session
from app.models import Participante, Voucher, Certificado, Curso
from sqlalchemy import func
from datetime import datetime, timedelta


class DashboardManager:
    """Gestiona estadísticas y datos del dashboard"""

    def __init__(self):
        self.session = get_session()

    def obtener_estadisticas_generales(self):
        """Obtiene estadísticas generales del sistema"""
        total_cursos = self.session.query(Curso).count()
        total_participantes = self.session.query(Participante).count()
        total_vouchers = self.session.query(Voucher).count()
        total_certificados = self.session.query(Certificado).count()

        vouchers_verificados = self.session.query(Voucher).filter_by(verified=True).count()
        certificados_generados = self.session.query(Certificado).filter_by(estado="generado").count()

        return {
            "total_cursos": total_cursos,
            "total_participantes": total_participantes,
            "total_vouchers": total_vouchers,
            "total_certificados": total_certificados,
            "vouchers_verificados": vouchers_verificados,
            "certificados_generados": certificados_generados,
            "porcentaje_verificacion": (vouchers_verificados / total_vouchers * 100) if total_vouchers > 0 else 0,
            "porcentaje_certificacion": (certificados_generados / total_participantes * 100) if total_participantes > 0 else 0
        }

    def obtener_estadisticas_por_curso(self):
        """Obtiene estadísticas desglosadas por curso"""
        cursos = self.session.query(Curso).all()
        estadisticas = []

        for curso in cursos:
            participantes = self.session.query(Participante).filter_by(curso_id=curso.id).count()
            vouchers = self.session.query(Voucher).join(Participante).filter(
                Participante.curso_id == curso.id
            ).count()
            certificados = self.session.query(Certificado).filter_by(curso_id=curso.id).count()
            monto_total = self.session.query(func.sum(Voucher.monto)).join(Participante).filter(
                Participante.curso_id == curso.id
            ).scalar() or 0

            estadisticas.append({
                "curso_id": curso.id,
                "curso_nombre": curso.nombre,
                "participantes": participantes,
                "vouchers": vouchers,
                "certificados": certificados,
                "monto_total": monto_total,
                "porcentaje_vouchers": (vouchers / participantes * 100) if participantes > 0 else 0,
                "porcentaje_certificados": (certificados / participantes * 100) if participantes > 0 else 0
            })

        return estadisticas

    def obtener_actividad_reciente(self, dias=7):
        """Obtiene la actividad de los últimos N días"""
        fecha_inicio = datetime.utcnow() - timedelta(days=dias)

        participantes_nuevos = self.session.query(Participante).filter(
            Participante.created_at >= fecha_inicio
        ).count()

        vouchers_nuevos = self.session.query(Voucher).filter(
            Voucher.created_at >= fecha_inicio
        ).count()

        certificados_nuevos = self.session.query(Certificado).filter(
            Certificado.created_at >= fecha_inicio
        ).count()

        return {
            "periodo_dias": dias,
            "participantes_nuevos": participantes_nuevos,
            "vouchers_nuevos": vouchers_nuevos,
            "certificados_nuevos": certificados_nuevos
        }

    def obtener_top_cursos(self, limite=5):
        """Obtiene los cursos con más participantes"""
        cursos = self.session.query(
            Curso.id,
            Curso.nombre,
            func.count(Participante.id).label('cantidad')
        ).join(Participante).group_by(Curso.id).order_by(
            func.count(Participante.id).desc()
        ).limit(limite).all()

        return [
            {"curso_id": c[0], "curso_nombre": c[1], "participantes": c[2]}
            for c in cursos
        ]

    def obtener_ingresos_totales(self):
        """Calcula ingresos totales por vouchers verificados"""
        ingresos = self.session.query(func.sum(Voucher.monto)).filter_by(
            verified=True
        ).scalar() or 0

        return float(ingresos)

    def obtener_participantes_sin_certificado(self):
        """Obtiene participantes que no tienen certificado"""
        participantes_sin_cert = self.session.query(Participante).filter(
            ~Participante.id.in_(
                self.session.query(Certificado.participante_id)
            )
        ).all()

        return [
            {
                "id": p.id,
                "nombre": p.nombre,
                "email": p.email,
                "curso": p.curso.nombre if p.curso else "N/A"
            }
            for p in participantes_sin_cert
        ]
