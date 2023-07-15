from typing import List

from pydantic import BaseModel, validator
from datetime import datetime

from model import Reserva


class ReservaSchema(BaseModel):
    sala_id: int = 1
    data_reserva: str = "20/08/2023"  # Exemplo de data no formato "dia/mês/ano"
    horario_reserva: str = "10:00"
    duracao_reserva: int = 1

    def to_model(self):
        # Convertendo a data da reserva para o formato datetime
        data_reserva = datetime.strptime(self.data_reserva, "%d/%m/%Y")

        return {
            "sala_id": self.sala_id,
            "data_reserva": data_reserva,
            "horario_reserva": self.horario_reserva,
            "duracao_reserva": self.duracao_reserva,
            "fim_reserva": self.fim_reserva
        }

    @validator('data_reserva')
    def validate_data_reserva(cls, value):
        try:
            # Verificar se a data está no formato correto "dia/mês/ano"
            datetime.strptime(value, "%d/%m/%Y")
        except ValueError:
            raise ValueError("A data da reserva deve estar no formato 'dia/mês/ano'")
        return value

    @validator('horario_reserva')
    def validate_horario_reserva(cls, value):
        try:
            # Verificar se o horário está no formato correto "hora:minuto"
            datetime.strptime(value, "%H:%M")
        except ValueError:
            raise ValueError("O horário da reserva deve estar no formato 'hora:minuto'")
        return value


class ListagemReservaSchema(BaseModel):
    id: int = 1
    sala_id: int = 1
    data_reserva: str = "20/08/2023"  # Exemplo de data no formato "dia/mês/ano"
    horario_reserva: str = "10:00"
    duracao_reserva: int = 1


def apresenta_reservas(reservas: List[Reserva]):
    result = []
    for reserva in reservas:
        # Formatando a data da reserva e o fim_reserva para o formato brasileiro
        reserva_data = reserva.data_reserva.strftime("%d/%m/%Y")
        reserva_fim = reserva.fim_reserva.strftime("%m/%d/%Y, %H:%M")
        result.append({
            "id": reserva.id,
            "sala_id": reserva.sala,
            "data_reserva": reserva_data,
            "horario_reserva": reserva.horario_reserva,
            "duracao_reserva": reserva.duracao_reserva,
            "fim_reserva": reserva_fim,
        })
    return {"reservas": result}


class ReservaDelSchema(BaseModel):
    sala_id: int
    id: int
    message: str


class ReservaBuscaSchema(BaseModel):
    sala_id: int
    id: int

