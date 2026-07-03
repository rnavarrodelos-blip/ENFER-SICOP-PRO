from twilio.rest import Client
import os
from dotenv import load_dotenv
from app.db_init import get_session
from app.models import Voucher, Participante

load_dotenv()


class WhatsAppIntegration:
    """Integración con WhatsApp para recibir vouchers"""

    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')
        self.session = get_session()

        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None

    def enviar_mensaje(self, numero_whatsapp, mensaje):
        """Envía un mensaje por WhatsApp"""
        if not self.client:
            return {"success": False, "mensaje": "WhatsApp no configurado"}

        try:
            message = self.client.messages.create(
                from_=f"whatsapp:{self.whatsapp_number}",
                body=mensaje,
                to=f"whatsapp:{numero_whatsapp}"
            )
            return {"success": True, "message_sid": message.sid}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def procesar_voucher_whatsapp(self, numero_telefono, numero_voucher, monto, participante_id):
        """Procesa un voucher recibido por WhatsApp"""
        try:
            # Verificar duplicado
            existente = self.session.query(Voucher).filter_by(
                numero_voucher=numero_voucher
            ).first()

            if existente:
                self.enviar_mensaje(
                    numero_telefono,
                    f"⚠️ Voucher {numero_voucher} ya está registrado."
                )
                return {"success": False, "mensaje": "Voucher duplicado"}

            # Crear voucher
            nuevo_voucher = Voucher(
                numero_voucher=numero_voucher,
                participante_id=participante_id,
                monto=monto,
                estado="verificado",
                verified=True
            )
            self.session.add(nuevo_voucher)
            self.session.commit()

            # Enviar confirmación
            self.enviar_mensaje(
                numero_telefono,
                f"✅ Voucher {numero_voucher} registrado exitosamente por S/. {monto}"
            )

            return {"success": True, "voucher_id": nuevo_voucher.id}
        except Exception as e:
            self.session.rollback()
            return {"success": False, "error": str(e)}
