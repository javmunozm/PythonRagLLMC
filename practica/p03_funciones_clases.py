"""Practica capitulo 3: funciones, clases, dataclass, Pydantic, excepciones, with y decoradores"""

import functools
import json
import tempfile
import time
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, Field, ValidationError

# Funciones

def saludar(nombre: str, saludo: str = "Hola") -> str:
    return f"{saludo}, {nombre}"

def sumar(*numeros: float) -> float: # params float[] / ... numeros
    return sum(numeros)

def configurar(**opciones) -> dict: # recibe cualquier argumento con nombre como dict
    return opciones

def dividir(a: float, b: float) -> tuple[float, float]:
    return a // b, a % b # devolver varios valores = devolver una tupla

def agregar( item, lista: list | None = None) -> list:
    if lista is None: #en Python nunca usar lista=[] como valor por defecto
        lista = []
    lista.append(item)
    return lista

print(saludar("Ana"), "|", saludar("Ana", saludo="Buenas"))
print(sumar(1, 2, 3), configurar(modelo="gemini", temperatura=0.2))
cociente, resto = dividir(7, 2)
print(cociente, resto)
print(saludar(**{"nombre": "Ana", "saludo": "Hola"})) #desempaqueta un dict como argumentos
print(agregar(1), agregar(2)) # [1] [2]: cada llamada tiene su propia lista

# Clases
class Cuenta:
    tasa = 0.01 #atributo de clase (como static)
    def __init__(self, titular: str, saldo: float = 0) -> None: #constructor
        self.titular = titular # self = this, y es OBLIGATORIO escribirlo
        self._saldo = saldo # _ = "privado" por convencion

    @property
    def saldo(self) -> float: #propiedad de solo lectura (get;)
        return self._saldo

    def depositar(self, monto: float) -> None:
        if monto <= 0:
            raise ValueError("El monto debe ser positivo") # throw new ArgumentException

        self._saldo += monto

    def __str__(self) -> str: #TosString()
        return f"Cuenta({self.titular}, {self._saldo})"

class CuentaAhorro(Cuenta): #herencia: class CuentaAhorro: cuenta
    def __init__(self, titular: str, saldo: float = 0, interes: float = 0.05) -> None:
        super().__init__(titular, saldo) # : base(titular, saldo)
        self.interes = interes

    def depositar(self, monto: float) ->None: #override (implicito)
        super().depositar(monto * (1 + self.interes))

c = CuentaAhorro("Ana", 100) # sin "new"
c.depositar(100)
print(c, c.saldo) # 205.0

# Protocol: la interfaz de typescript (pato typing, sin heredar)
class Repositorio(Protocol):
    def obtener(self, id: int) -> dict: ...

class RepoMemoria: #no hereda: cumple porque tiene obtener()
    def obtener(self, id: int) -> dict:
        return {"id": id}

def usar(repo: Repositorio) -> dict:
    return repo.obtener(1)

print(usar(RepoMemoria()))

#Dataclass, enum y pydantic

@dataclass
class Producto: #como un record de C#
    nombre: str
    precio: float
    tags: list[str] = field(default_factory=list)

print(Producto("Mouse", 10.0) == Producto("Mouse", 10.0)) # True: igualdad por valor

class Rol(StrEnum):
    ADMIN = "admin"
    VIEWER = "viewer"

print(Rol("viewer"), Rol.ADMIN == "admin") #True

class UsuarioIn(BaseModel): # DTO que valida al crearse
    nombre: str = Field(min_length=2)
    edad: int = Field(ge=0, le=120)
    email: str
    tags: list[str] = []

u = UsuarioIn.model_validate({"nombre": "Ana", "edad": "30", "email":"a@x.com"})
print(u.edad +1, u.model_dump_json()) # 31:convirtio "30" a int

try:
    UsuarioIn(nombre="A", edad=-1, email="x")
except ValidationError as e:
    print(e.error_count(), "errores") # 2 erroers


# Excepciones y with
class SaldoInsuficienteError(Exception):
    pass

def retirar(saldo: float, monto: float) -> float:
    if monto > saldo:
        raise SaldoInsuficienteError(f"Saldo {saldo} < {monto}")

try:
    retirar(10, 50)
except SaldoInsuficienteError as e:
    print("Error de negocio:", e)
else:
    print("solo si no hubo erro")
finally:
    print("always?")

with tempfile.TemporaryDirectory() as carpeta: # with = using: se borra al salir
    ruta = Path(carpeta) / "datos" / "config.json" # Path.Combine con el operador /
    ruta.parent.mkdir(exist_ok = True)
    with open(ruta, "w", encoding="utf-8") as f: # en Windows deberia siempRe utilizar el encoding="utf-8" o si no hay que reconvertir
        json.dump({"modelo": "gemini", "temp": 0.2}, f, ensure_ascii=False, indent=2)
    with open(ruta, encoding="utf-8") as f:
        print(json.load(f))

#Generadores y decoradores
def en_bloques(items, tam):
    for i in range(0, len(items), tam):
        yield items[i : i + tam] # yield = yield return de C#

print(list(en_bloques([1, 2, 3, 4, 5], 2))) # [[1, 2], [3, 4], [5]]

def medir(func):
    @functools.wraps(func)
    def envoltura(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = func(*args, **kwargs)
        print(f"{func.__name__} tardo {time.perf_counter() - inicio:4f}s")
        return resultado
    return envoltura

@medir
def proceso():
    return sum(range((1_000_000)))

proceso()
