from experta import *

class Problema(Fact):
    pass

class DiagnosticoCoche(KnowledgeEngine):
    @Rule(Problema(sintoma='no_arranca'))
    def problema_no_arranca(self):
        print("El coche no arranca. Posibles causas:")
        print("- Batería baja")
        print("- Motor de arranque defectuoso")
        print("- Falta de combustible")

    @Rule(Problema(sintoma='ruido_al_frenar'))
    def problema_ruido_al_frenar(self):
        print("Hay ruido al frenar. Posibles causas:")
        print("- Pastillas de freno desgastadas")
        print("- Discos de freno rayados")
        print("- Caliper atascado")

    @Rule(Problema(sintoma='humo_del_escape'))
    def problema_humo_del_escape(self):
        print("Sale humo del escape. Posibles causas:")
        print("- Aceite en la cámara de combustión")
        print("- Junta de culata dañada")
        print("- Anillos de pistón desgastados")

    @Rule(Problema(sintoma='perdida_potencia'))
    def problema_perdida_potencia(self):
        print("Hay pérdida de potencia. Posibles causas:")
        print("- Filtro de aire sucio")
        print("- Bujías desgastadas")
        print("- Inyectores obstruidos")

    @Rule(Problema(sintoma=MATCH.sintoma))
    def problema_desconocido(self, sintoma):
        print(f"Síntoma '{sintoma}' no reconocido. Por favor, consulte con un mecánico.")

def main():
    engine = DiagnosticoCoche()
    engine.reset()
    print("Bienvenido al Sistema Experto de Diagnóstico de Coches")
    print("Síntomas disponibles: no_arranca, ruido_al_frenar, humo_del_escape, perdida_potencia")
    print("Escriba 'salir' para terminar el programa")
    
    while True:
        sintoma = input("Ingrese el síntoma del coche: ").lower()
        if sintoma == 'salir':
            break
        engine.declare(Problema(sintoma=sintoma))
        engine.run()
        engine.reset()
        print()

if __name__ == "__main__":
    main()