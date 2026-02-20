import json
from typing import Any
from dotenv import load_dotenv
from cliente_redis import obtener_conexion
from modelo_usuario import crear_usuario_json, leer_usuario_json, actualizar_usuario_json, listar_usuarios, eliminar_usuario

load_dotenv()
def imprimir(obj: Any) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))

def prompt_json(prompt:str) -> str:
    texto = input(prompt).strip()
    if not texto:
        raise ValueError('Entrada JSON vacía.')
    json.loads(texto)
    return texto
def menu():
    try:
        conexion = obtener_conexion
    except Exception as e:
        print(f'ERROR: No se pudo conectar a Redis: {e}')
        return
    while True:
        print("\n--- Menú usuarios Redis ---") 
        print("1) Crear usuario (introduce JSON)") 
        print("2) Leer usuario (id)") 
        print("3) Actualizar usuario (id + JSON)") 
        print("4) Eliminar usuario (id)") 
        print("5) Listar usuarios") 
        print("6) Salir")
        
        opcion = input("Selecciona una opción: ").strip()
        try:
            if opcion in ('1', 'crear'):
                try:
                    datos = prompt_json('JSON usuario: ')
                except Exception as e:
                    print(f'JSON invalido: {e}')
                    continue
                creado = crear_usuario_json(conexion, datos)
                imprimir({'creado': bool(creado)})
                
            elif opcion in ('2', 'leer'):
                idu = input('id_usuario: ').strip()
                usuario = leer_usuario_json(conexion, idu)
                imprimir({'usuario': usuario})
                
            elif opcion in ('3', 'actualizar'):
                idu = input('id_usuario: ').strip()
                try:
                    datos = prompt_json('JSON actualización: ')
                except Exception as e:
                    print(f'JSON invalido: {e}')
                    continue
                modo = input('modo (mezclar/reemplazar) [mezclar]: ').strip() or 'mezclar'
                actualizado = actualizar_usuario_json(conexion, idu, datos, modo=modo)
                
            elif opcion in ('4', 'eliminar'):
                idu = input('id_usuario: ').strip()
                eliminado = eliminar_usuario(conexion, idu)
                imprimir({'eliminado': bool(eliminado)})
                
            elif opcion in ('5', 'listar'):
                usuarios = listar_usuarios(conexion)
                imprimir({'total': len(usuarios), 'usuarios': usuarios})
            
            elif opcion in ('6', 'salir'):
                print('Adios')
                break
            else:
                print('Opción no válida.')
        except Exception as e:
            print(f'ERROR: {e}')
            
def main() -> int:
    try:
        menu()
        return 0
    except KeyboardInterrupt:
        print("\nInterrumpido")
        return 1
    
if __name__ == "__main__":
    raise SystemExit(main())