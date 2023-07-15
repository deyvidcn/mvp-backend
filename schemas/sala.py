from pydantic import BaseModel
from typing import Optional, List

from model.sala import Sala
from schemas.reserva import ReservaSchema


class SalaSchema(BaseModel):
    nome: str = "sala1"
    capacidade: int = 12
    descricao: str = "Descrição da sala"


class SalaBuscaSchema(BaseModel):
    nome: str = "sala1"


class ListagemSalasSchema(BaseModel):
    salas: List[SalaSchema]


def apresenta_salas(salas: List[Sala]):
    result = []
    for sala in salas:
        result.append({
            "nome": sala.nome,
            "capacidade": sala.capacidade,
            "descricao": sala.descricao,
        })
    return {"salas": result}


class SalaViewSchema(BaseModel):
    id: int = 1
    nome: str = "sala1"
    capacidade: Optional[int] = 12
    descricao: str = "Descrição da sala"
    total_reservas: int = 1
    reservas: List[ReservaSchema]


class SalaDelSchema(BaseModel):
    mesage: str
    nome: str


def apresenta_sala(sala: Sala):
    result = {
        "sala_id": sala.id,
        "nome": sala.nome,
        "capacidade": sala.capacidade,
        "descricao": sala.descricao,
        "total_reservas": len(sala.reservas),
        "reservas": []
    }

    for reserva in sala.reservas:
        # Formatando a data da reserva no formato brasileiro
        reserva_data = reserva.data_reserva.strftime("%d/%m/%Y")
        reserva_info = {
            "id": reserva.id,
            "data_reserva": reserva_data,
            "horario_reserva": reserva.horario_reserva,
            "duracao_reserva": reserva.duracao_reserva,
        }
        result["reservas"].append(reserva_info)

    return result
