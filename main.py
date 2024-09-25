from reader import Reader
from parsing import Parser
from nfa import NFA
from dfa import DFA
from direct_dfa import DDFA
from direct_reader import DirectReader
from time import process_time
import re

# Función para guardar la expresión regular en un archivo
def guardar_expresion(expresion_regular):
    with open("expresiones_regulares.txt", "a") as archivo:
        archivo.write("\nER:\n")
        archivo.write(f"{expresion_regular}\n")
    print("Expresión regular guardada en 'expresiones_regulares.txt'.")

# Función para validar una cadena con una expresión regular
def validar_cadena(expresion_regular, cadena):
    try:
        return re.fullmatch(expresion_regular, cadena) is not None
    except re.error:
        return False

titulo_programa = '''

#        AUTOMATAS FINITOS        #

Genera NFA's o DFA's basados en una expresión regular y compara tiempos simulando una cadena! NOTA: para la expresión epsilon, por favor usa la letra "e"
'''

menu_principal = '''
¿Qué te gustaría hacer?
1. Establecer una expresión regular
2. Generar AFN usando Thompson y construcción de conjunto de potencias para generar un DFA
3. Usar el método de DFA directo
4. Validación de cadenas
5. Mostrar Gramatica
6. Guardar
7. Salir del programa
'''

mensaje_thompson = '''
    # THOMPSON Y CONSTRUCCIÓN DE CONJUNTO DE POTENCIAS # '''
mensaje_dfa_directo = '''
    # CONSTRUCCIÓN DE DFA DIRECTO # '''
opcion_invalida = '''
Err: ¡Esa no es una opción válida!
'''
mensaje_generar_diagrama = '''
¿Te gustaría generar y ver el diagrama? [y/n] (por defecto: n)'''
mensaje_tipo_regex = '''
Escribe una expresión regular '''
mensaje_tipo_cadena = '''
Escribe una cadena '''

if __name__ == "__main__":
    print(titulo_programa)
    opt = None
    regex = None
    metodo = None

    while opt != 0:
        print(menu_principal)
        opt = input('> ')

        if opt == '1':
            print(mensaje_tipo_regex)
            regex = input('> ')
            guardar_expresion(regex)  # Guardar la expresión regular

            try:
                reader = Reader(regex)
                tokens = reader.CreateTokens()
                parser = Parser(tokens)
                arbol = parser.Parse()

                direct_reader = DirectReader(regex)
                direct_tokens = direct_reader.CreateTokens()
                direct_parser = Parser(direct_tokens)
                direct_arbol = direct_parser.Parse()
                print('\n\t¡Expresión aceptada!')
                print('\tÁrbol parseado:', arbol)

            except AttributeError as e:
                print(f'\n\tERR: Expresión inválida (falta paréntesis)')

            except Exception as e:
                print(f'\n\tERR: {e}')

        elif opt == '2':
            if not regex:
                print('\n\tERR: ¡Necesitas establecer una expresión regular primero!')
                opt = None
            else:
                print(mensaje_thompson)
                print(mensaje_tipo_cadena)
                entrada_regex = input('> ')

                nfa = NFA(arbol, reader.GetSymbols(), entrada_regex)
                tiempo_inicio = process_time()
                nfa_regex = nfa.EvalRegex()
                tiempo_fin = process_time()

                print('\nTiempo para evaluar: {:.5E} segundos'.format(
                    tiempo_fin - tiempo_inicio))
                print('¿Pertenece la cadena a la expresión regular (NFA)?')
                print('>', nfa_regex)

                dfa = DFA(nfa.trans_func, nfa.symbols,
                          nfa.curr_state, nfa.accepting_states, entrada_regex)
                dfa.TransformNFAToDFA()
                tiempo_inicio = process_time()
                dfa_regex = dfa.EvalRegex()
                tiempo_fin = process_time()
                print('\nTiempo para evaluar: {:.5E} segundos'.format(
                    tiempo_fin - tiempo_inicio))
                print('¿Pertenece la cadena a la expresión regular (DFA)?')
                print('>', dfa_regex)

                print(mensaje_generar_diagrama)
                generar_diagrama = input('> ')

                if generar_diagrama == 'y':
                    nfa.WriteNFADiagram()
                    

        elif opt == '3':
            if not regex:
                print('\n\tERR: ¡Necesitas establecer una expresión regular primero!')
                opt = None
            else:
                print(mensaje_dfa_directo)
                print(mensaje_tipo_cadena)
                entrada_regex = input('> ')
                ddfa = DDFA(
                    direct_arbol, direct_reader.GetSymbols(), entrada_regex)
                tiempo_inicio = process_time()
                ddfa_regex = ddfa.EvalRegex()
                tiempo_fin = process_time()
                print('\nTiempo para evaluar: {:.5E} segundos'.format(
                    tiempo_fin - tiempo_inicio))
                print('¿Pertenece la cadena a la expresión regular?')
                print('>', ddfa_regex)

                print(mensaje_generar_diagrama)
                generar_diagrama = input('> ')

                if generar_diagrama == 'y':
                    ddfa.GraphDFA()

                ddfa = None

        elif opt == '4':
            if regex is None:
                print("\nPrimero debes ingresar una expresión regular (opción 1).")
                continue

            while True:
                # Pedir al usuario que ingrese una cadena para validar
                cadena = input("\nIngresa una cadena para validar (o 'salir' para volver al menú): ")

                if cadena.lower() == 'salir' or cadena =='$':
                    break  # Volver al menú

                # Validar la cadena con la expresión regular
                if validar_cadena(regex, cadena):
                    print(f"La cadena '{cadena}' es válida para la expresión regular.")
                else:
                    print(f"La cadena '{cadena}' no es válida para la expresión regular.")
            
        elif opt == '7':
            print('¡Hasta luego!')
            exit(1)
