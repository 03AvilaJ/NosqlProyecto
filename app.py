from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "secret_key"  # Para manejar mensajes flash

# Configuración de MongoDB Atlas
client = MongoClient("mongodb+srv://johanaavila:123@nosqlproyecto.4r5km.mongodb.net/")
db = client["proyecto"]
pets_collection = db["pets"]

counters_collection = db["counters"]
pets_collection = db["pets"]
# Verificar si ya existe el contador, si no, lo insertamos
if not counters_collection.find_one({"_id": "petId"}):
    counters_collection.insert_one({"_id": "petId", "sequence_value": 0})

def get_next_pet_id():
    # Incrementa el contador 'petId' y devuelve el siguiente valor
    counter = counters_collection.find_one_and_update(
        {"_id": "petId"},  # El identificador del contador
        {"$inc": {"sequence_value": 1}},  # Incrementa el valor del contador
        return_document=True
    )
    return counter["sequence_value"]  # Retorna el nuevo valor de 'petId'

# Ruta: Página principal (Listado de mascotas)
@app.route("/")
def index():
    pets_cursor = pets_collection.find()
    pets = list(pets_cursor)  # Convertir cursor a lista
    return render_template("index.html", pets=pets)

# Ruta: Formulario para agregar una nueva mascota
@app.route("/add", methods=["GET", "POST"])
def add_pet():
    if request.method == "POST":
        # Obtener el siguiente petId autoincremental
        new_pet_id = str(get_next_pet_id())  # Usando la función del contador autoincremental

        # Crear el nuevo documento de mascota con la estructura completa
        new_pet = {
            "petId": new_pet_id,  # ID único
            "isActive": True,  # Por defecto se marca como activo
            "petName": request.form["petName"],
            "species": request.form["species"],
            "breed": request.form["breed"],
            "age": int(request.form["age"]),
            "weight": request.form["weight"],
            "owner": {
                "name": request.form["ownerName"],
                "phone": request.form["ownerPhone"],
                "email": request.form["ownerEmail"],
                "address": request.form["ownerAddress"]
            },
            "medicalHistory": [
                {
                    "date": request.form["medicalHistoryDate1"],
                    "condition": request.form["medicalHistoryCondition1"],
                    "vet": request.form["vetName1"],
                    "notes": request.form["medicalNotes1"]
                }
            ],
            "nextAppointment": request.form["nextAppointment"],
            "favoriteToy": request.form["favoriteToy"],
            "favoriteTreat": request.form["favoriteTreat"]
        }

        # Insertar el documento en la colección de mascotas
        pets_collection.insert_one(new_pet)
        flash("Mascota agregada con éxito.")
        return redirect(url_for("index"))
    
    return render_template("add_pet.html")


# Ruta: Formulario para actualizar una mascota
@app.route("/update/<petId>", methods=["GET", "POST"])
def update_pet(petId):
    if request.method == "POST":
        updated_data = {
            "$set": {
                "petName": request.form["petName"],
                "species": request.form["species"],
                "age": int(request.form["age"]),
                "weight": request.form["weight"],
            }
        }
        pets_collection.update_one({"petId": petId}, updated_data)
        flash("Mascota actualizada con éxito.")
        return redirect(url_for("index"))
    pet = pets_collection.find_one({"petId": petId})
    return render_template("update_pets.html", pet=pet)

# Ruta: Eliminar una mascota
@app.route("/delete/<petId>")
def delete_pet(petId):
    pets_collection.delete_one({"petId": petId})
    flash("Mascota eliminada con éxito.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
