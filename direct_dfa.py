from pythomata import SimpleDFA
from graphviz import Digraph
from utils import WriteToFile
from pprint import pprint

RAW_STATES = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

class DDFA:
    def __init__(self, tree, symbols, regex):
        # Útil para el árbol de sintaxis
        self.nodes = list()

        # Propiedades del autómata finito
        self.symbols = symbols
        self.states = list()
        self.trans_func = dict()
        self.accepting_states = set()
        self.initial_state = 'A'

        # Propiedades de la clase
        self.tree = tree
        self.regex = regex
        self.augmented_state = None
        self.iter = 1

        self.STATES = iter(RAW_STATES)
        try:
            self.symbols.remove('e')
        except:
            pass

        # Inicializar la construcción del DFA
        self.ParseTree(self.tree)
        self.CalcFollowPos()

    def CalcFollowPos(self):
        # Calcular followpos para cada nodo
        for node in self.nodes:
            if node.value == '*':
                for i in node.lastpos:
                    child_node = next(filter(lambda x: x._id == i, self.nodes))
                    child_node.followpos += node.firstpos
            elif node.value == '.':
                for i in node.c1.lastpos:
                    child_node = next(filter(lambda x: x._id == i, self.nodes))
                    child_node.followpos += node.c2.firstpos

        # Iniciar la generación de estados
        initial_state = self.nodes[-1].firstpos

        # Filtrar los nodos que tienen un símbolo
        self.nodes = list(filter(lambda x: x._id, self.nodes))
        self.augmented_state = self.nodes[-1]._id

        # Recursión
        self.CalcNewStates(initial_state, next(self.STATES))

    def CalcNewStates(self, state, curr_state):
        # Calcular nuevos estados
        if not self.states:
            self.states.append(set(state))
            if self.augmented_state in state:
                self.accepting_states.update(curr_state)

        # Iterar por cada símbolo
        for symbol in self.symbols:
            # Obtener todos los nodos con el mismo símbolo en followpos
            same_symbols = list(
                filter(lambda x: x.value == symbol and x._id in state, self.nodes))

            # Crear un nuevo estado con los nodos
            new_state = set()
            for node in same_symbols:
                new_state.update(node.followpos)

            # Si el nuevo estado no está en la lista de estados
            if new_state not in self.states and new_state:
                # Obtener la letra de este nuevo estado
                self.states.append(new_state)
                next_state = next(self.STATES)

                # Agregar estado a la función de transición
                try:
                    self.trans_func[next_state]
                except:
                    self.trans_func[next_state] = dict()

                try:
                    existing_states = self.trans_func[curr_state]
                except:
                    self.trans_func[curr_state] = dict()
                    existing_states = self.trans_func[curr_state]

                # Agregar la referencia
                existing_states[symbol] = next_state
                self.trans_func[curr_state] = existing_states

                # ¿Es un estado de aceptación?
                if self.augmented_state in new_state:
                    self.accepting_states.update(next_state)

                # Repetir con este nuevo estado
                self.CalcNewStates(new_state, next_state)

            elif new_state:
                # El estado ya existe... ¿cuál es?
                for i in range(0, len(self.states)):
                    if self.states[i] == new_state:
                        state_ref = RAW_STATES[i]
                        break

                # Agregar la transición del símbolo
                try:
                    existing_states = self.trans_func[curr_state]
                except:
                    self.trans_func[curr_state] = {}
                    existing_states = self.trans_func[curr_state]

                existing_states[symbol] = state_ref
                self.trans_func[curr_state] = existing_states

    def ParseTree(self, node):
        # Parsear el árbol de sintaxis
        method_name = node.__class__.__name__ + 'Node'
        method = getattr(self, method_name)
        return method(node)

    def LetterNode(self, node):
        # Procesar nodo de letra
        new_node = Node(self.iter, [self.iter], [
                        self.iter], value=node.value, nullable=False)
        self.nodes.append(new_node)
        return new_node

    def OrNode(self, node):
        # Procesar nodo OR
        node_a = self.ParseTree(node.a)
        self.iter += 1
        node_b = self.ParseTree(node.b)

        is_nullable = node_a.nullable or node_b.nullable
        firstpos = node_a.firstpos + node_b.firstpos
        lastpos = node_a.lastpos + node_b.lastpos

        self.nodes.append(Node(None, firstpos, lastpos,
                               is_nullable, '|', node_a, node_b))
        return Node(None, firstpos, lastpos, is_nullable, '|', node_a, node_b)

    def AppendNode(self, node):
        # Procesar nodo de concatenación
        node_a = self.ParseTree(node.a)
        self.iter += 1
        node_b = self.ParseTree(node.b)

        is_nullable = node_a.nullable and node_b.nullable
        if node_a.nullable:
            firstpos = node_a.firstpos + node_b.firstpos
        else:
            firstpos = node_a.firstpos

        if node_b.nullable:
            lastpos = node_b.lastpos + node_a.lastpos
        else:
            lastpos = node_b.lastpos

        self.nodes.append(
            Node(None, firstpos, lastpos, is_nullable, '.', node_a, node_b))

        return Node(None, firstpos, lastpos, is_nullable, '.', node_a, node_b)

    def KleeneNode(self, node):
        # Procesar nodo de estrella de Kleene
        node_a = self.ParseTree(node.a)
        firstpos = node_a.firstpos
        lastpos = node_a.lastpos
        self.nodes.append(Node(None, firstpos, lastpos, True, '*', node_a))
        return Node(None, firstpos, lastpos, True, '*', node_a)

    def PlusNode(self, node):
        # Procesar nodo de más
        node_a = self.ParseTree(node.a)

        self.iter += 1

        node_b = self.KleeneNode(node)

        is_nullable = node_a.nullable and node_b.nullable
        if node_a.nullable:
            firstpos = node_a.firstpos + node_b.firstpos
        else:
            firstpos = node_a.firstpos

        if node_b.nullable:
            lastpos = node_b.lastpos + node_a.lastpos
        else:
            lastpos = node_b.lastpos

        self.nodes.append(
            Node(None, firstpos, lastpos, is_nullable, '.', node_a, node_b))

        return Node(None, firstpos, lastpos, is_nullable, '.', node_a, node_b)

    def QuestionNode(self, node):
        # Procesar nodo de interrogación
        # Node_a es epsilon
        node_a = Node(None, list(), list(), True)
        self.iter += 1
        node_b = self.ParseTree(node.a)

        is_nullable = node_a.nullable or node_b.nullable
        firstpos = node_a.firstpos + node_b.firstpos
        lastpos = node_a.lastpos + node_b.lastpos

        self.nodes.append(Node(None, firstpos, lastpos,
                               is_nullable, '|', node_a, node_b))
        return Node(None, firstpos, lastpos, is_nullable, '|', node_a, node_b)

    def EvalRegex(self):
        # Evaluar la expresión regular
        curr_state = 'A'
        for symbol in self.regex:
            if not symbol in self.symbols:
                return 'No'

            try:
                curr_state = self.trans_func[curr_state][symbol]
            except:
                if curr_state in self.accepting_states and symbol in self.trans_func['A']:
                    curr_state = self.trans_func['A'][symbol]
                else:
                    return 'No'

        return 'Yes' if curr_state in self.accepting_states else 'No'

    def GraphDFA(self):
        # Graficar el DFA
        states = set(self.trans_func.keys())
        alphabet = set(self.symbols)

        dfa = SimpleDFA(states, alphabet, self.initial_state,
                        self.accepting_states, self.trans_func)

        graph = dfa.trim().to_graphviz()
        graph.attr(rankdir='LR')

        source = graph.source
        WriteToFile('./output/DirectDFA.gv', source)
        graph.render('./output/DirectDFA.gv', format='pdf', view=True)

class Node:
    def __init__(self, _id, firstpos=None, lastpos=None, nullable=False, value=None, c1=None, c2=None):
        self._id = _id
        self.firstpos = firstpos
        self.lastpos = lastpos
        self.followpos = list()
        self.nullable = nullable
        self.value = value
        self.c1 = c1
        self.c2 = c2

    def __repr__(self):
        return f'''
    id: {self._id}
    value: {self.value}
    firstpos: {self.firstpos}
    lastpos: {self.lastpos}
    followpos: {self.followpos}
    nullabe: {self.nullable}
    '''
