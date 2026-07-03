from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Curso(Base):
    __tablename__ = "cursos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text)
    horas = Column(Integer)
    precio = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    participantes = relationship("Participante", back_populates="curso")
    certificados = relationship("Certificado", back_populates="curso")


class Participante(Base):
    __tablename__ = "participantes"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    telefono = Column(String(20))
    identificacion = Column(String(50), unique=True)
    curso_id = Column(Integer, ForeignKey("cursos.id"))
    estado = Column(String(50), default="activo")
    created_at = Column(DateTime, default=datetime.utcnow)

    curso = relationship("Curso", back_populates="participantes")
    vouchers = relationship("Voucher", back_populates="participante")
    certificados = relationship("Certificado", back_populates="participante")


class Voucher(Base):
    __tablename__ = "vouchers"

    id = Column(Integer, primary_key=True)
    numero_voucher = Column(String(100), unique=True)
    participante_id = Column(Integer, ForeignKey("participantes.id"))
    monto = Column(Float)
    fecha_emision = Column(DateTime, default=datetime.utcnow)
    estado = Column(String(50), default="pendiente")
    imagen_path = Column(String(500))
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    participante = relationship("Participante", back_populates="vouchers")


class Certificado(Base):
    __tablename__ = "certificados"

    id = Column(Integer, primary_key=True)
    numero_certificado = Column(String(100), unique=True)
    participante_id = Column(Integer, ForeignKey("participantes.id"))
    curso_id = Column(Integer, ForeignKey("cursos.id"))
    fecha_emision = Column(DateTime, default=datetime.utcnow)
    estado = Column(String(50), default="generado")
    archivo_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    participante = relationship("Participante", back_populates="certificados")
    curso = relationship("Curso", back_populates="certificados")


class Auditoria(Base):
    __tablename__ = "auditoria"

    id = Column(Integer, primary_key=True)
    tabla = Column(String(100), nullable=False)
    accion = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE
    registro_id = Column(Integer)
    datos_anteriores = Column(JSON)
    datos_nuevos = Column(JSON)
    usuario = Column(String(255), default="sistema")
    timestamp = Column(DateTime, default=datetime.utcnow)
