from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from urllib.parse import unquote

from schemas.error import ErrorSchema
from sqlalchemy.exc import IntegrityError

from schemas.game import *
from schemas.player import  *
from model import Session, Game, Player
from logger import logger
from flask_cors import CORS

info = Info(title="Golzinho API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
game_tag = Tag(name="Game", description="Games at the database viewing, addition and deletion")
player_tag = Tag(name="Player", description="Players at the database viewing, addition and deletion")


@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')


@app.post('/game', tags=[game_tag],
          responses={"200": GameViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_game(form: GameSchema):
    """Register a new game scheduling to the database.
    """
    
    game = Game(
        game_scheduling_id=form.id,
        label=form.label,
        # created_by=form.created_by,
        creation_date=form.creation_date,
        cost=form.cost,
        location=form.location,
        game_date=form.game_date,
        duration_minutes=form.duration_minutes
        )

    logger.debug(f"Adicionando game de nome: '{game.label}'")
    try:
        # criando conexão com a base
        session = Session()
        # adicionando produto
        session.add(game)
        # efetivando o camando de adição de novo item na tabela
        session.commit()
        logger.debug(f"Adicionado game de nome: '{game.label}'")
        return detail_game(game), 200

    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = "Game de mesmo nome já salvo na base :/"
        logger.warning(f"Erro ao adicionar game '{game.label}', {error_msg}")
        return {"message": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item :/"
        logger.warning(f"Erro ao adicionar game '{game.label}', {error_msg}")
        return {"message": error_msg}, 400


@app.get('/games', tags=[game_tag],
         responses={"200": ListGamesSchema, "404": ErrorSchema})
def get_games():
    """Gets the list of games registered.
    """
    logger.debug(f"Getting games")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    games = session.query(Game).all()

    if not games:
        # se não há produtos cadastrados
        return {"games": []}, 200
    else:
        logger.debug(f"%d games found" % len(games))
        # retorna a representação de produto
        print(games)
        return list_games(games), 200



@app.delete('/game', tags=[game_tag],
            responses={"200": GameDeleteSchema, "404": ErrorSchema})
def delete_game(query: GameSearchSchema):
    """Delete a registered game by Id.
    """
    game_id = query.id
    print(query.id)
    # print(query.)
    logger.debug(f"Deletando dados sobre game #{query.id}")
    # criando conexão com a base
    session = Session()
    # fazendo a remoção
    count = session.query(Game).filter(Game.game_scheduling_id == game_id).delete()
    session.commit()

    if count:
        # retorna a representação da mensagem de confirmação
        logger.debug(f"Deletado game #{game_id}")
        return {"message": "Produto removido", "id": game_id}
    else:
        # se o produto não foi encontrado
        error_msg = "game não encontrado na base :/"
        logger.warning(f"Erro ao deletar game #'{game_id}', {error_msg}")
        return {"message": error_msg}, 404


# @app.post('/player', tags=[player_tag],
#           responses={"200": PlayerViewSchema, "404": ErrorSchema})
# def add_player(form: PlayerSchema):
#     """Register a new game scheduling to the database

#     Retorna uma representação dos produtos e comentários associados.
#     """
#     player = Player(
#         player_id=form.game_player_id,
#         player_name=form.player_name,
#         player_email=form.player_email,
#         game_scheduling_id=form.game_scheduling_id
#         )

#     logger.debug(f"Adicionando produto de nome: '{player.label}'")
#     try:
#         # criando conexão com a base
#         session = Session()
#         # adicionando produto
#         session.add(player)
#         # efetivando o camando de adição de novo item na tabela
#         session.commit()
#         logger.debug(f"Adicionado produto de nome: '{player.label}'")
#         return detail_player(player), 200

#     except IntegrityError as e:
#         # como a duplicidade do nome é a provável razão do IntegrityError
#         error_msg = "Produto de mesmo nome já salvo na base :/"
#         logger.warning(f"Erro ao adicionar produto '{player.label}', {error_msg}")
#         return {"message": error_msg}, 409

#     except Exception as e:
#         # caso um erro fora do previsto
#         error_msg = "Não foi possível salvar novo item :/"
#         logger.warning(f"Erro ao adicionar produto '{player.label}', {error_msg}")
#         return {"message": error_msg}, 400


# @app.get('/players', tags=[player_tag],
#          responses={"200": ListPlayersSchema, "404": ErrorSchema})
# def get_players(game_id):
#     """Faz a busca por todos os Players cadastrados

#     Retorna uma representação da listagem de produtos.
#     """
#     logger.debug(f"Getting players")
#     # criando conexão com a base
#     session = Session()
#     # fazendo a busca
#     players = session.query(Player).filter_by(game_scheduling_id = game_id )

#     if not players:
#         # se não há produtos cadastrados
#         return {"players": []}, 200
#     else:
#         logger.debug(f"%d games found" % len(players))
#         # retorna a representação de produto
#         print(players)
#         return list_players(players), 200
