from datetime import datetime
from app.db_init import get_session
from app.models import Auditoria, Voucher, Certificado, Participante, Curso
import json


class AuditoriaManager:
    """Gestiona la auditoría de cambios en el sistema"""

    def __init__(self):
        self.session = get_session()

    def registrar_cambio(self, tabla, accion, registro_id, datos_anteriores=None, datos_nuevos=None, usuario="sistema"):
        """
        Registra un cambio en la auditoría
        accion: CREATE, UPDATE, DELETE
        """
        try:
            auditoria = Auditoria(
                tabla=tabla,
                accion=accion,
                registro_id=registro_id,
                datos_anteriores=datos_anteriores,
                datos_nuevos=datos_nuevos,
                usuario=usuario,
                timestamp=datetime.utcnow()
            )
            self.session.add(auditoria)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"Error registrando auditoría: {e}")

    def obtener_historial(self, tabla=None, registro_id=None, limite=100):
        """Obtiene el historial de cambios"""
        query = self.session.query(Auditoria)

        if tabla:
            query = query.filter_by(tabla=tabla)
        if registro_id:
            query = query.filter_by(registro_id=registro_id)

        return query.order_by(Auditoria.timestamp.desc()).limit(limite).all()

    def obtener_estadisticas_auditoria(self):
        """Obtiene estadísticas de cambios"""
        total_cambios = self.session.query(Auditoria).count()
        cambios_por_tabla = {}
        cambios_por_accion = {}

        for tabla in ["vouchers", "certificados", "participantes", "cursos"]:
            cambios_por_tabla[tabla] = self.session.query(Auditoria).filter_by(tabla=tabla).count()

        for accion in ["CREATE", "UPDATE", "DELETE"]:
            cambios_por_accion[accion] = self.session.query(Auditoria).filter_by(accion=accion).count()

        return {
            "total_cambios": total_cambios,
            "cambios_por_tabla": cambios_por_tabla,
            "cambios_por_accion": cambios_por_accion
        }
