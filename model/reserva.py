from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from typing import Union

from model import Base


class Reserva(Base):
    __tablename__ = 'reserva'

    id = Column(Integer, primary_key=True)
    data_reserva = Column(DateTime)
    horario_reserva = Column(String(10))
    duracao_reserva = Column(Integer)
    fim_reserva = Column(DateTime)
    sala = Column(Integer, ForeignKey("sala.pk_sala"), nullable=False)

    def __init__(self, data_reserva: Union[DateTime, None] = None, horario_reserva: str = "", duracao_reserva: int = 1, fim_reserva: Union[DateTime, None] = None):
        self.data_reserva = data_reserva
        self.horario_reserva = horario_reserva
        self.duracao_reserva = duracao_reserva
        self.fim_reserva = fim_reserva
