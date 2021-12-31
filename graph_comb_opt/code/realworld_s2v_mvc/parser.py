#!/usr/bin/python2
import cPickle as cp
import networkx as nx
import sys


class Token:
    T_PROBLEM = "T_PROBLEM"
    T_PROBLEM_DESCRIPTOR = "T_PROBLEM_DESCRIPTOR"
    T_NUMBER = "T_NUMBER"
    T_EOL = "T_EOL"
    T_EOF = "T_EOF"

    def __init__(self, tid, line, column, value=None):
        self.tid = tid
        self.line = line
        self.column = column
        self.value = value


class Lexer:
    def __init__(self, file_name):
        self.line = 1
        self.column = 0
        self.c = b''
        self.t = None
        self.reader = open(file_name, 'r')
        self.next_char()

    def next_char(self):
        self.column += 1
        if self.c == '\n':
            self.line += 1
            self.column = 1

        self.c = self.reader.read(1)
        return self.c

    def next_token(self):
        while True:
            line = self.line
            column = self.column

            # End of file
            if self.c == '':
                self.t = Token(Token.T_EOF, line, column)
                return self.t
            # Comments
            if self.c == 'c':
                while self.next_char() != '\n' and self.c != '':
                    # Eat remaining comment
                    pass
                # Continue searching for token
                self.next_char()
                continue
            # Problem line
            if self.c == 'p':
                if self.next_char() != ' ':
                    raise Exception(
                        "Expected" + ' ' + "but got" + {self.c} + " at line" + {self.line} + ":" + {self.column})
                self.t = Token(Token.T_PROBLEM, line, column)
                return self.t
            # Problem descriptor
            if self.c == 't':
                tmp = self.c
                while self.next_char() != '\n' and self.c != ' ' and self.c != '':
                    tmp += self.c
                if tmp != "td":
                    raise Exception("Expected td but got " + tmp + " at line" + str(self.line) + ":" + str(self.column))
                self.t = Token(Token.T_PROBLEM_DESCRIPTOR, line, column)
                return self.t
            # End of line
            if self.c == '\n':
                self.next_char()
                self.t = Token(Token.T_EOL, line, column)
                return self.t
            # Numbers
            if 47 < ord(self.c) < 58:
                value = ord(self.c) - 48

                # Read all following digits
                while self.next_char() != '' and 47 < ord(self.c) < 58:
                    value = value * 10 + (ord(self.c) - 48)

                if self.c != '' and self.c != ' ' and self.c != '\n':
                    raise Exception(
                        "Expected digit, ' ', EOL or EOF but got '{self.c}' at {self.line}:{self.column}")

                self.t = Token(Token.T_NUMBER, line, column, value)
                return self.t
            # Spaces
            if self.c == ' ':
                while self.next_char() == ' ':
                    pass
                continue

            raise Exception("Unexpected " + self.c + " at" + str(self.line) + ":" + str(self.column))
        assert False


class Parser:
    def __init__(self, file_name):
        self.lexer = Lexer(file_name)
        self.graph = None

    # XXX: This implementation currently does not verify that the graph does not contain multiple edges or loops as
    #      specified by PACE
    def parse(self):
        n_edges = 0
        while self.lexer.next_token().tid != Token.T_EOF:
            tid = self.lexer.t.tid

            # Problem description
            if tid == Token.T_PROBLEM:
                # Preconditions
                if self.graph is not None:
                    raise Exception(
                        "Unexpected T_PROBLEM, expected T_NUMBER at {self.lexer.t.line}:{self.lexer.t.column}")

                # Problem descriptor
                if self.lexer.next_token().tid != Token.T_PROBLEM_DESCRIPTOR:
                    raise Exception(
                        "Unexpected {self.lexer.t.tid}, expected T_PROBLEM_DESCRIPTOR at {self.lexer.t.line}:{self.lexer.t.column}")
                self.graph = nx.Graph()

                # Number of vertices
                if self.lexer.next_token().tid != Token.T_NUMBER:
                    raise Exception(
                        "Unexpected {self.lexer.t.tid}, expected T_NUMBER at {self.lexer.t.line}:{self.lexer.t.column}")
                number_of_vertices = self.lexer.t.value
                for i in range(1, number_of_vertices + 1):
                    self.graph.add_node(i - 1)
                # Number of edges
                if self.lexer.next_token().tid != Token.T_NUMBER:
                    raise Exception(
                        "Unexpected {self.lexer.t.tid}, expected T_NUMBER at {self.lexer.t.line}:{self.lexer.t.column}")
                n_edges = self.lexer.t.value
                continue

            # Edge data
            if tid == Token.T_NUMBER:
                # Preconditions
                if self.graph is None:
                    raise Exception(
                        "Unexpected T_NUMBER, expected T_PROBLEM at {self.lexer.t.line}:{self.lexer.t.column}")
                if len(self.graph.edges()) == n_edges:
                    raise Exception("Surplus edge at {self.lexer.t.line}:{self.lexer.t.column}")

                # First vertex
                v1 = self.lexer.t.value
                if v1 < 0 or v1 > len(self.graph.nodes()):
                    raise Exception("Invalid vertex at {self.lexer.t.line}:{self.lexer.t.column}")

                # Second vertex
                if self.lexer.next_token().tid != Token.T_NUMBER:
                    raise Exception(
                        "Unexpected {self.lexer.t.tid}, expected T_NUMBER at {self.lexer.t.line}:{self.lexer.t.column}")
                v2 = self.lexer.t.value
                if v2 < 0 or v2 > len(self.graph.nodes()):
                    raise Exception("Invalid vertex at" + str(self.lexer.t.line) + ":" + str(self.lexer.t.column))

                # There must be no additional tokens on this line
                if self.lexer.next_token().tid != Token.T_EOL and self.lexer.t.tid != Token.T_EOF:
                    raise Exception(
                        "Unexpected {self.lexer.t.tid}, expected T_EOL or T_EOF at {self.lexer.t.line}:{self.lexer.t.column}")
                self.graph.add_edge(v1 - 1, v2 - 1)
                if self.lexer.t.tid == Token.T_EOF:
                    break
                continue

            # Empty line
            if tid == Token.T_EOL:
                continue
        return self.graph


# Driver function to use this in our moduar system.
def paceLoader(i):
    if i < 10:
        path = "./public/vc-exact_00" + str(i) + ".gr"
    if 10 < i < 100:
        path = "./public/vc-exact_0" + str(i) + ".gr"
    if i > 100:
        path = "./public/vc-exact_" + str(i) + ".gr"
    print("Parsing i=" + str(i))
    print("Path to source file:" + path)
    p = Parser(path)
    g = p.parse()
    print("done!")
    return g


if __name__ == '__main__':
    paceLoader()
