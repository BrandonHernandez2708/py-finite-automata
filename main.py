from reader import Reader
from parsing import Parser
from nfa import NFA
from dfa import DFA
from direct_dfa import DDFA
from direct_reader import DirectReader
from time import process_time

titulo_programa = '''

#        AUTOMATAS FINITOS        #

Genera NFA's o DFA's basados en una expresión regular y compara tiempos simulando una cadena! NOTA: para la expresión epsilon, por favor usa la letra "e"
'''

menu_principal = '''
¿Qué te gustaría hacer?
1. Establecer una expresión regular
2. Probar una cadena con la expresión regular dada
0. Salir del programa
'''

submenu = '''
Selecciona una de las opciones para probar tu expresión regular:

    1. Usar Thompson para generar un NFA y construcción de conjunto de potencias para generar un DFA.
    2. Usar el método de DFA directo.
    0. Volver al menú principal.
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

        if opt == '2':
            if not regex:
                print('\n\tERR: ¡Necesitas establecer una expresión regular primero!')
                opt = None
            else:
                print(submenu)
                metodo = input('> ')

                if metodo == '1':
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
                        dfa.GraphDFA()

                elif metodo == '2':
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

                elif metodo == '3':
                    continue

                else:
                    print(opcion_invalida)

        elif opt == '0':
            print('¡Hasta luego!')
            exit(1)
