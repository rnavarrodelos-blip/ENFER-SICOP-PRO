import pytesseract
from PIL import Image
import re
from app.db_init import get_session
from app.models import Voucher, Participante


class OCRProcessor:
    """Procesa imágenes de vouchers usando OCR"""

    def __init__(self):
        self.session = get_session()

    def extraer_texto_voucher(self, imagen_path):
        """Extrae texto de una imagen de voucher"""
        try:
            imagen = Image.open(imagen_path)
            texto = pytesseract.image_to_string(imagen, lang='spa')
            return texto
        except Exception as e:
            print(f"Error al procesar imagen: {e}")
            return None

    def extraer_numero_voucher(self, texto):
        """Extrae el número de voucher del texto OCR"""
        # Busca patrones comunes de números de voucher
        patrones = [
            r'Voucher[\s:]*(\d{5,20})',
            r'V[\s:]*(\d{5,20})',
            r'Número[\s:]*(\d{5,20})',
            r'N°[\s:]*(\d{5,20})',
            r'(\d{10,20})'
        ]
        
        for patron in patrones:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def extraer_monto(self, texto):
        """Extrae el monto del voucher del texto OCR"""
        patrones = [
            r'\$\s*([\d,]+\.?\d*)',
            r'Monto[\s:]*\$?\s*([\d,]+\.?\d*)',
            r'([\d,]+\.?\d*)\s*(?:soles|S/)',
        ]
        
        for patron in patrones:
            match = re.search(patron, texto)
            if match:
                monto_str = match.group(1).replace(',', '')
                try:
                    return float(monto_str)
                except ValueError:
                    continue
        return 0.0

    def verificar_duplicado(self, numero_voucher):
        """Verifica si el voucher ya existe en la BD"""
        existente = self.session.query(Voucher).filter_by(
            numero_voucher=numero_voucher
        ).first()
        return existente is not None

    def procesar_voucher_automatico(self, imagen_path, participante_id):
        """Procesa un voucher automáticamente desde una imagen"""
        # Extraer texto de la imagen
        texto = self.extraer_texto_voucher(imagen_path)
        if not texto:
            return {"success": False, "mensaje": "No se pudo procesar la imagen"}

        # Extraer número y monto
        numero_voucher = self.extraer_numero_voucher(texto)
        monto = self.extraer_monto(texto)

        if not numero_voucher:
            return {"success": False, "mensaje": "No se encontró número de voucher"}

        # Verificar duplicado
        if self.verificar_duplicado(numero_voucher):
            return {
                "success": False,
                "mensaje": f"Voucher {numero_voucher} ya está registrado",
                "duplicado": True
            }

        # Crear nuevo voucher
        try:
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
                "mensaje": "Voucher procesado exitosamente",
                "numero_voucher": numero_voucher,
                "monto": monto,
                "voucher_id": nuevo_voucher.id
            }
        except Exception as e:
            self.session.rollback()
            return {"success": False, "mensaje": str(e)}
