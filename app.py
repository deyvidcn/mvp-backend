from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from urllib.parse import unquote
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

from model import Session, Sala, Reserva
from logger import logger
from schemas import *
from utils import verificar_conflito_reserva

info = Info(title="Reserva de salas API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
sala_tag = Tag(name="Salas", description="Adição, visualização e remoção de salas à base")
reserva_tag = Tag(name="Reserva", description="Adição de uma reserva à uma sala cadastrada na base")


@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação."""
    return redirect('/openapi')


@app.post('/sala', tags=[sala_tag],
          responses={"200": SalaViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_sala(form: SalaSchema):
    """Adiciona uma nova Sala à base de dados.

    Retorna uma representação das salas e reservas associadas.
    """
    sala = Sala(
        nome=form.nome,
        capacidade=form.capacidade,
        descricao=form.descricao)
    logger.debug(f"Adicionando sala de nome: '{sala.nome}'")
    try:
        session = Session()
        session.add(sala)
        session.commit()
        logger.debug(f"Adicionada sala de nome: '{sala.nome}'")
        return apresenta_sala(sala), 200

    except IntegrityError as e:
        error_msg = "Sala de mesmo nome já salva na base :/"
        logger.warning(f"Erro ao adicionar sala '{sala.nome}', {error_msg}")
        return {"message": error_msg}, 409

    except Exception as e:
        error_msg = "Não foi possível salvar novo item :/"
        logger.warning(f"Erro ao adicionar sala '{sala.nome}', {error_msg}")
        return {"message": error_msg}, 400


@app.get('/salas', tags=[sala_tag],
         responses={"200": ListagemSalasSchema, "404": ErrorSchema})
def get_salas():
    """Faz a busca por todas as Salas cadastradas.

    Retorna uma representação da listagem de salas.
    """
    logger.debug(f"Coletando salas")
    session = Session()
    salas = session.query(Sala).all()

    if not salas:
        return {"salas": []}, 200
    else:
        logger.debug(f"{len(salas)} salas encontradas")
        return apresenta_salas(salas), 200


@app.get('/sala', tags=[sala_tag],
         responses={"200": SalaViewSchema, "404": ErrorSchema})
def get_sala(query: SalaBuscaSchema):
    """Faz a busca por uma Sala a partir do nome da sala.

    Retorna uma representação da sala e suas reservas associadas.
    """
    sala_nome = unquote(unquote(query.nome))
    logger.debug(f"Coletando dados sobre a sala '{sala_nome}'")
    session = Session()
    sala = session.query(Sala).filter(Sala.nome == sala_nome).first()

    if not sala:
        error_msg = "Sala não encontrada na base :/"
        logger.warning(f"Erro ao buscar sala '{sala_nome}', {error_msg}")
        return {"message": error_msg}, 404
    else:
        logger.debug(f"Sala encontrada: '{sala.nome}'")
        return apresenta_sala(sala), 200


@app.delete('/sala', tags=[sala_tag],
            responses={"200": SalaDelSchema, "404": ErrorSchema})
def del_sala(query: SalaBuscaSchema):
    """Deleta uma Sala a partir do nome da sala informado.

    Retorna uma mensagem de confirmação da remoção.
    """
    sala_nome = unquote(unquote(query.nome))
    logger.debug(f"Deletando dados sobre sala '{sala_nome}'")
    session = Session()
    count = session.query(Sala).filter(Sala.nome == sala_nome).delete()
    session.commit()

    if count:
        logger.debug(f"Sala '{sala_nome}' removida")
        return {"message": "Sala removida", "nome": sala_nome}
    else:
        error_msg = "Sala não encontrada na base :/"
        logger.warning(f"Erro ao deletar sala '{sala_nome}', {error_msg}")
        return {"message": error_msg}, 404


@app.post('/reserva', tags=[reserva_tag],
          responses={"200": SalaViewSchema, "404": ErrorSchema})
def add_reserva(form: ReservaSchema):
    """Adiciona uma nova Reserva a uma sala cadastrada na base identificada pelo id.

    Retorna uma representação da sala e suas reservas associadas.
    """
    sala_id = form.sala_id
    horario_reserva = form.horario_reserva
    h, m = horario_reserva.split(":")
    hora = int(h)
    minuto = int(m)
    data_reserva = datetime.strptime(form.data_reserva, "%d/%m/%Y")  # Converter para objeto datetime
    data_reserva = data_reserva + timedelta(hours=hora, minutes=minuto)
    duracao_reserva = form.duracao_reserva
    fim_reserva = datetime.strptime(form.data_reserva, "%d/%m/%Y") + timedelta(hours=hora, minutes=minuto) + timedelta(hours=duracao_reserva)

    logger.debug(f"Adicionando reserva à sala de id '{sala_id}'")
    session = Session()
    sala = session.query(Sala).filter(Sala.id == sala_id).first()

    if not sala:
        error_msg = "Sala não encontrada na base :/"
        logger.warning(f"Erro ao adicionar uma reserva à sala de id '{sala_id}', {error_msg}")
        return {"message": error_msg}, 404

    # Verificar se a data_reserva é igual ou inferior à data e hora atual
    if data_reserva <= datetime.now():
        error_msg = "A reserva não pode ser cadastrada com data igual ou anterior à data e hora atual."
        logger.warning(f"Erro ao adicionar reserva à sala de id '{sala_id}', {error_msg}")
        return {"message": error_msg}, 400

    # Verifica se ja existe reserva na sala no mesmo periodo
    if verificar_conflito_reserva(sala_id, data_reserva, fim_reserva) > 0:
         error_msg = "Já existe uma reserva para essa sala no mesmo período."
         logger.warning(f"Erro ao adicionar reserva à sala de id '{form.sala_id}', {error_msg}")
         return {"message": error_msg}, 409

    reserva = Reserva(data_reserva, horario_reserva, duracao_reserva, fim_reserva)
    sala.adiciona_reserva(reserva)
    session.commit()

    logger.debug(f"Reserva adicionada à sala de id '{sala_id}'")
    return apresenta_sala(sala), 200

@app.get('/reservas', tags=[reserva_tag],
         responses={"200": ListagemReservaSchema, "404": ErrorSchema})
def get_reservas():
    """Faz a busca por todas as Reservas cadastradas.

    Retorna uma representação da listagem de reservas.
    """
    logger.debug(f"Coletando reservas")
    session = Session()
    reservas = session.query(Reserva).all()

    if not reservas:
        return {"reservas": []}, 200
    else:
        logger.debug(f"{len(reservas)} reservas encontradas")
        return apresenta_reservas(reservas), 200

@app.delete('/reserva', tags=[reserva_tag],
            responses={"200": ReservaDelSchema, "404": ErrorSchema})
def del_reserva(query: ReservaBuscaSchema):
    """Deleta uma reserva a partir do ID da reserva informado.

    Retorna uma mensagem de confirmação da remoção.
    """
    sala_id = query.sala_id
    reserva_id = query.id
    logger.debug(f"Deletando reserva de ID '{reserva_id}'")
    session = Session()
    reserva = session.query(Reserva).filter(Reserva.id == reserva_id and Reserva.sala == sala_id).first()

    if not reserva:
        error_msg = "Reserva não encontrada na base :/"
        logger.warning(f"Erro ao deletar reserva de ID '{reserva_id}', {error_msg}")
        return {"message": error_msg}, 404

    session.delete(reserva)
    session.commit()

    logger.debug(f"Reserva da sala_id: {sala_id} e ID '{reserva_id}' removida")
    return {"message": "Reserva removida", "salaid": reserva_id}