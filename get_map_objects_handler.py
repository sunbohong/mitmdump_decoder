import os
import numpy
import math
# Make pokedex requests async
from requests_futures.sessions import FuturesSession
from geojson import GeometryCollection, Point, Feature, FeatureCollection
import geojson

from protocol.bridge_pb2 import *
from protocol.clientrpc_pb2 import *
from protocol.gymbattlev2_pb2 import *
from protocol.holoholo_shared_pb2 import *
from protocol.platform_actions_pb2 import *
from protocol.remaining_pb2 import *
from protocol.rpc_pb2 import *
from protocol.settings_pb2 import *
from protocol.sfida_pb2 import *
from protocol.signals_pb2 import *

class GetMapObjectsHandler:
  def __init__(self):
    self.session = FuturesSession()

  def request(self, mor, env):
    features = []
    props = {
        "id": "player",
        "marker-symbol": "pitch",
        "title": "You",
        "marker-size": "large",
        "marker-color": "663399",
        "type": "player"
    }
    p = Point((mor.PlayerLng, mor.PlayerLat))
    f = Feature(geometry=p, id="player", properties=props)
    features.append(f)
    fc = FeatureCollection(features)
    dump = geojson.dumps(fc, sort_keys=True)
    self._player = dump
    f = open('ui/player.json', 'w')
    f.write(dump)

  def response(self, mor, env, req_env):
    gps = (req_env.lat, req_env.long)
    features = []

    for cell in mor.MapCell:
      for fort in cell.Fort:
        props = {
            "id": fort.FortId,
            "LastModifiedMs": fort.LastModifiedMs,
            }

        if fort.FortType == CHECKPOINT:
          props["title"] = "PokeStop"
          props["type"] = "pokestop"
          props["lure"] = fort.HasField('FortLureInfo')
        else:
          props["type"] = "gym"

        props["team"] = Team.Name(fort.Team)
        if fort.Team == BLUE:
          props["title"] = "Blue Gym"
        elif fort.Team == RED:
          props["title"] = "Red Gym"
        elif fort.Team == YELLOW:
          props["title"] = "Yellow Gym"

        p = Point((fort.Longitude, fort.Latitude))
        f = Feature(geometry=p, id=fort.FortId, properties=props)
        features.append(f)

      for spawn in cell.SpawnPoint:
        p = Point((spawn.Longitude, spawn.Latitude))
        f = Feature(geometry=p, id=len(features), properties={
          "type": "spawn",
          "id": len(features),
          "title": "spawn",
          "marker-color": "00FF00",
          "marker-symbol": "garden",
          "marker-size": "small",
          })
        features.append(f)

      for spawn in cell.DecimatedSpawnPoint:
        p = Point((spawn.Longitude, spawn.Latitude))
        f = Feature(geometry=p, id=len(features), properties={
          "id": len(features),
          "type": "decimatedspawn",
          "title": "Decimated spawn",
          "marker-color": "000000",
          "marker-symbol": "monument"
          })
        features.append(f)

      for pokemon in cell.WildPokemon:
        p = Point((pokemon.Longitude, pokemon.Latitude))
        f = Feature(geometry=p, id="wild%s" % pokemon.EncounterId, properties={
          "id": "wild%s" % pokemon.EncounterId,
          "type": "pokemon",
          "pokemonNumber": pokemon.Pokemon.PokemonId,
          "TimeTillHiddenMs": pokemon.TimeTillHiddenMs,
          "WillDisappear": pokemon.TimeTillHiddenMs + pokemon.LastModifiedMs,
          "title": "Wild %s" % Custom_PokemonName.Name(pokemon.Pokemon.PokemonId),
          })
        features.append(f)

      for pokemon in cell.CatchablePokemon:
        p = Point((pokemon.Longitude, pokemon.Latitude))
        f = Feature(geometry=p, id="catchable%s" % pokemon.EncounterId, properties={
          "id": "catchable%s"  % pokemon.EncounterId,
          "type": "pokemon",
          "ExpirationTimeMs": pokemon.ExpirationTimeMs,
          "title": "Catchable %s" % Custom_PokemonName.Name(pokemon.PokedexTypeId),
          "marker-color": "000000",
          "marker-symbol": "circle"
          })
        features.append(f)

      for pokemon in cell.NearbyPokemon:
        p = Point((req_env.long, req_env.lat))
        f = Feature(geometry=p, id="nearby%s" % pokemon.EncounterId, properties={
          "id": "nearby%s"  % pokemon.EncounterId,
          "type": "nearby",
          "pokedex": pokemon.PokedexNumber,
          "title": Custom_PokemonName.Name(pokemon.PokedexNumber),
          "distance": pokemon.DistanceMeters
        })
        features.append(f)

    fc = FeatureCollection(features)
    dump = geojson.dumps(fc, sort_keys=True)
    f = open('ui/get_map_objects.json', 'w')
    f.write(dump)

# vim: set tabstop=2 shiftwidth=2 expandtab : #
