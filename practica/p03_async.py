"""Practica capitulo 3: async / await"""

import asyncio

async def obtener(id: int) -> dict: #async Task<Dictionary<....>>
    await asyncio.sleep(0.1) #await Task.Delay(100)
    return {"id": id}

async def main() -> None:
    uno = await obtener(1)
    varios = await asyncio.gather(obtener(1), obtener(2), obtener(3)) # Task.WhenAll
    print (uno, varios)

if __name__ == "__main__": #solo se ejecuta con "py -m ....", no al importar el modulo
    asyncio.run(main()) # en un script, el bucle de eventos se arranca asi (una sola vez)