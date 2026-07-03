import requests
import json
from app.db_init import get_session
from app.models import Voucher, Participante


class LinkIntegration:
    """Integración para recibir vouchers por link/formulario"""

    def __init__(self):
        self.session = get_session()

    def validar_numero_voucher(self, numero_voucher):
        """Valida que el número de voucher sea único"""
        existente = self.session.query(Voucher).filter_by(
            numero_voucher=numero_voucher
        ).first()
        return not bool(existente)

    def procesar_voucher_link(self, datos):
        """
        Procesa un voucher recibido por formulario/link
        datos = {
            'numero_voucher': str,
            'participante_id': int,
            'monto': float,
            'imagen_url': str (opcional)
        }
        """
        try:
            numero_voucher = datos.get('numero_voucher')
            participante_id = datos.get('participante_id')
            monto = datos.get('monto')
            imagen_url = datos.get('imagen_url')

            # Validar que el participante existe
            participante = self.session.query(Participante).get(participante_id)
            if not participante:
                return {"success": False, "mensaje": "Participante no encontrado"}

            # Verificar duplicado
            if not self.validar_numero_voucher(numero_voucher):
                return {
                    "success": False,
                    "mensaje": f"Voucher {numero_voucher} ya está registrado",
                    "duplicado": True
                }

            # Descargar imagen si se proporciona URL
            imagen_path = None
            if imagen_url:
                imagen_path = self._descargar_imagen(numero_voucher, imagen_url)

            # Crear voucher
            nuevo_voucher = Voucher(
                numero_voucher=numero_voucher,
                participante_id=participante_id,
                monto=monto,
                imagen_path=imagen_path,
                estado="verificado",
                verified=True
            )
            self.session.add(nuevo_voucher)
            self.session.commit()

            return {
                "success": True,
                "mensaje": "Voucher registrado exitosamente",
                "voucher_id": nuevo_voucher.id,
                "numero_voucher": numero_voucher,
                "participante": participante.nombre
            }
        except Exception as e:
            self.session.rollback()
            return {"success": False, "mensaje": str(e)}

    def _descargar_imagen(self, numero_voucher, imagen_url):
        """Descarga una imagen desde URL"""
        try:
            import os
            if not os.path.exists('uploads'):
                os.makedirs('uploads')

            response = requests.get(imagen_url)
            if response.status_code == 200:
                imagen_path = f"uploads/{numero_voucher}.jpg"
                with open(imagen_path, 'wb') as f:
                    f.write(response.content)
                return imagen_path
        except Exception as e:
            print(f"Error descargando imagen: {e}")
        return None
