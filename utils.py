from sqlalchemy import or_, and_

from model import Reserva, Session


def verificar_conflito_reserva(sala_id, data_reserva, fim_reserva):
    session = Session()
    # faz a busca no banco para verificar se existem reservas na mesma data e horario
    conflito = session.query(Reserva).filter(
        Reserva.sala == sala_id,
        or_(
            and_(Reserva.data_reserva >= data_reserva, Reserva.data_reserva < fim_reserva),
            and_(Reserva.fim_reserva > data_reserva, Reserva.fim_reserva <= fim_reserva),
            and_(Reserva.data_reserva <= data_reserva, Reserva.fim_reserva >= fim_reserva)
        )
    ).count()

    return conflito
