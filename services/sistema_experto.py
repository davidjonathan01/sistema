from flask import Blueprint, request, jsonify, make_response
from models.pregunta import Pregunta
from models.regla import Regla
from models.especialidad import Especialidad
from experta import KnowledgeEngine, Fact
from utils.db import db

sistema_experto_routes = Blueprint("sistema_experto_routes", __name__)

# Definimos los hechos (fact) para el sistema experto
class PerfilUsuario(Fact):
    """Información del perfil del usuario"""
    pass

# Sistema experto basado en las reglas obtenidas de la base de datos
class SistemaExpertoEspecializaciones(KnowledgeEngine):

    def __init__(self, reglas):
        super().__init__()
        self.exactas = []
        self.probables = []
        self.reglas = reglas

    # Método para cargar y procesar las reglas manualmente
    def procesar_reglas_manual(self, respuestas):
        for especialidad, condiciones in self.reglas:
            condiciones_dict = {str(cond.split('=')[0]): str(cond.split('=')[1]) for cond in condiciones.split(',')}
            
            # Verificamos si todas las condiciones se cumplen con las respuestas del usuario
            if all(respuestas.get(codigo) == valor for codigo, valor in condiciones_dict.items()):
                # Si cumple todas las condiciones, lo marcamos como exacta
                self.exactas.append(especialidad)
            else:
                # Si no cumple todas pero se aproxima, lo agregamos como probable con la cantidad de coincidencias
                coincidencias = sum(respuestas.get(codigo) == valor for codigo, valor in condiciones_dict.items())
                if coincidencias > 0:
                    self.probables.append((especialidad, coincidencias))

    # Mostrar todas las recomendaciones
    def mostrar_recomendaciones(self, respuestas_usuario):
        if self.exactas:
            # Si hay especialidades exactas, solo las mostramos
            return {
                "mensaje": "Se encontraron especialidades exactas.",
                "especialidades": self.exactas
            }
        else:
            # Si no hay exactas, buscamos las especialidades con mayor coincidencias
            if self.probables:
                # Ordenamos las probables por el número de coincidencias
                max_coincidencias = max(self.probables, key=lambda x: x[1])[1]
                mejores_especialidades = [especialidad for especialidad, coincidencias in self.probables if coincidencias == max_coincidencias]
                
                return {
                    "mensaje": f"No se encontraron especialidades exactas. Se recomienda la(s) especialidad(es) con {max_coincidencias} coincidencias.",
                    "especialidades": mejores_especialidades
                }
            else:
                # Si no hay ninguna especialidad probable
                return {
                    "mensaje": "No se encontró una especialidad probable.",
                    "especialidades": []
                }

# Obtener las preguntas desde la base de datos
def obtener_preguntas():
    preguntas = Pregunta.query.all()
    return [(pregunta.codigo, pregunta.descripcion) for pregunta in preguntas]

# Obtener las reglas desde la base de datos
def obtener_reglas():
    reglas = db.session.query(Regla, Especialidad).join(Especialidad).all()
    return [(regla.Especialidad.nombre, regla.Regla.condiciones) for regla in reglas]

# Ruta para procesar las respuestas del usuario
@sistema_experto_routes.route('/procesar_respuestas', methods=['POST'])
def procesar_respuestas():
    # Obtener las respuestas del usuario desde el request JSON
    respuestas = request.json.get('respuestas')
    
    # Obtener las preguntas y reglas desde la base de datos
    reglas = obtener_reglas()
    
    # Crear el sistema experto con las reglas
    sistema = SistemaExpertoEspecializaciones(reglas)
    
    # Procesar las reglas con las respuestas del usuario
    sistema.procesar_reglas_manual(respuestas)
    
    # Obtener las recomendaciones
    recomendaciones = sistema.mostrar_recomendaciones(respuestas)
    
    # Enviar la respuesta como JSON
    data = {
        'recomendaciones': recomendaciones
    }
    
    return make_response(jsonify(data), 200)
