from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from model import Base, Reserva


class Sala(Base):
    __tablename__ = 'sala'

    id = Column("pk_sala", Integer, primary_key=True)
    nome = Column(String(40), unique=True)
    capacidade = Column(Integer)
    descricao = Column(String(400))
    data_insercao = Column(DateTime, default=datetime.now())

    reservas = relationship("Reserva")

    def __init__(self, nome: str, capacidade: int, descricao: str,
                 data_insercao: DateTime = None):
        self.nome = nome
        self.capacidade = capacidade
        self.descricao = descricao
        if data_insercao:
            self.data_insercao = data_insercao

    def adiciona_reserva(self, reserva: Reserva):
        self.reservas.append(reserva)
