"""Practica capitulo 3: variables, strings, colecciones, comprehensions y control de flujo"""

# Variables, tipos y strings
nombre = "Ana" # str
edad = 30 # int (sin limite de tamaño)
precio = 19.99 # float
activo = True # bool
nada = None # NoneType

print(f"{nombre} tiene {edad} años y paga {precio:.2f}")
print(type(edad), isinstance(edad, int)) #equivalente a <class 'int' > True
print(activo, nada)

#Conversiones explicitas (no hay conversion implica como en JS)
print(int("42") + 1) 
print(str(42) + "!")
try:
    print("1"+1)
except TypeError as e:
    print("TypeError:", e) # en JS daria "11"; en Python es error

#Operadores numericos
print (7 / 2, 7 // 2, 7 % 2, 2**10) #3. 3 1 1024

#Strings
s = "   Hola mundo   "
print(s.strip().lower()) # 'hola mundo' (Trim().ToLower())
print(s.split()) # ['Hola', 'Mundo']
print("-".join(["a", "b"])) # 'a-b (string.join / arr.join)
print("Mundo" in s, len(s.strip())) # True

#Colecciones
nums = [3, 1, 2]
nums.append(4) #Add / push
nums.extend([5, 6]) # AddRange / push(...arr)
print(nums.pop()) #quita y devuelve el  ultimo: 6
print(nums[0], nums[-1], nums[1:3], nums[::-1], sorted(nums))

x, y = (10,20) # tupla + destructuracion
primero, *resto = [1, 2, 3, 4] # 1, [2, 3, 4] (como const [a, ...b] = arr)
print(x, y, primero, resto)

persona = {"nombre": "Ana", "edad": 30}
persona["email"] = "ana@x.com"
print(persona["nombre"], persona.get("tel"), persona.get("tel", "sin tel"), "edad" in persona)
try:
    persona["tel"]
except KeyError as e:
    print("KeyError:", e) # un dict no devuelve undefined, sino un KeyError
for clave, valor in persona.items():
    print(clave, valor)
copia = {**persona, "edad": 31} # como {...persona, edad: 31}
print(copia)

tags = set(["python", "ia", "python"]) #set: elimina el duplicado
print(sorted(tags)) #['ia','python']

# --- linq y mapfilter comparison to python
usuarios = [
    {"nombre":"Ana","edad": 30},
    {"nombre":"Luis","edad": 17},
    {"nombre":"Eva","edad": 25},
]
adultos = [u["nombre"] for u in usuarios if u["edad"] >= 18] # Where + Select
print(adultos) # ['Ana', 'Eva']
print([n * n for n in range(5)]) # [0, 1, 4, 9, 16]
print({u["nombre"]: u["edad"] for u in usuarios}) #ToDictionary
print(sum(u["edad"] for u in usuarios)) # sum
print(max(usuarios, key=lambda u: u["edad"])["nombre"]) #MaxBy
print([u["nombre"] for u in sorted(usuarios, key=lambda u: u["edad"],reverse=True)])
print(any(u["edad"] < 18 for u in usuarios), all(u["edad"] > 0 for u in usuarios))

# --- Control de flujo
nota = 75
if nota >= 90:
    print("A")
elif nota >= 70: " else if"
else:
    print("C")

for i, fruta in enumerate(["manzana", "pera"]): # indice + valor
    print(i, fruta)
for nombre_, edad_ in zip(["Ana", "Luis"], [30, 17], strict=True): #dos listas a la vez
    print(nombre_, edad_)

n = 0
while n < 3:
    n+= 1 # no existe n++
print("n =", n)
status = 404
match status: #switch con patrones
    case 200 | 201:
        resultado = "ok"
    case 404:
        resultado = "no encontrado"
    case _: #default
        resultado = "otro"
print (resultado)