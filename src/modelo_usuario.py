import json 
import re
from typing import Optional,List, Dict, Any
from redis import Redis

PREFIJO_USUARIO = 'usuario:'

def validar_id_usuario(id_usuario:str) -> None:
    if not re.fullmatch(r'[A-Za-z0-9_-]{3,40}', id_usuario):
        raise ValueError('id_usuario invalido. Usa 3-40 caracteres alfanumericos, _ o -')
    
def construir_clave_usuario(id_usuario:str) -> str:
    return f'{PREFIJO_USUARIO}{id_usuario}'

def normalizar_id_usuario(datos:Dict[str,Any]) ->str:
    id_usuario = datos.get('id_usuario' , datos.get('id'))
    if id_usuario is None:
        raise ValueError("El JSON debe incluir 'id_usuario' o 'id'.")
    id_usuario = str(id_usuario).strip()
    validar_id_usuario(id_usuario)
    return id_usuario

def crear_usuario_json(conexion: Redis, usuario_json : str) -> bool:
    datos = json.loads(usuario_json) 
    if not isinstance(datos, dict): 
        raise ValueError("El JSON debe ser un objeto.") 
 
    id_usuario = normalizar_id_usuario(datos) 
    datos["id_usuario"] = id_usuario 
 
    clave = construir_clave_usuario(id_usuario) 
    valor = json.dumps(datos, ensure_ascii=False) 
 
    creado = conexion.set(clave, valor, nx=True) 
    return bool(creado) 

def leer_usuario_json(conexion: Redis, id_usuario:str) -> Optional[Dict[str,Any]]:
    id_usuario = str(id_usuario).strip()
    validar_id_usuario(id_usuario)
    
    valor = conexion.get(construir_clave_usuario(id_usuario))
    if valor is None:
        return None
    datos = json.loads(valor)
    if isinstance(datos,dict) and 'id_usuario'not in datos:
        datos['id_usuario'] = id_usuario
    return datos

def actualizar_usuario_json(
    conexion: Redis, 
    id_usuario:str,
    json_actualizacion:str,
    modo : str = 'mezclar'
) ->bool: 
    actual = leer_usuario_json(conexion, id_usuario)
    if actual is None:
        return False
    nuevos_datos = json.loads(json_actualizacion)
    if not isinstance(nuevos_datos, dict):
        raise ValueError("El JSON de actualización debe ser un objeto.")
    if modo == 'reemplazar':
        resultado = nuevos_datos
    elif modo == 'mezclar':
        resultado = dict(actual)
        resultado.update(nuevos_datos)
    else: 
        raise ValueError("Modo invalido. Usa 'reemplazar' o 'mezclar'.")
    resultado["id_usuario"] = id_usuario
    conexion.set(
        construir_clave_usuario(id_usuario), 
        json.dumps(resultado, ensure_ascii=False)
    )
    return True

def eliminar_usuario(conexion: Redis, id_usuario:str) -> bool:
    eliminado = conexion.delete(construir_clave_usuario(id_usuario))
    return eliminado == 1

def listar_usuarios(conexion: Redis) -> List[Dict[str,Any]]:
    ids = sorted(conexion.keys('*'))
    resultado = []
    for id_usuario in ids:
        datos = leer_usuario_json(conexion,id_usuario.replace(PREFIJO_USUARIO,''))
        if datos:
            resultado.append(datos)
    return resultado
