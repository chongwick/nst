import json
import codecs
import os
import sys
from tree_sitter import Parser, Language
import tree_sitter_ruby as tsruby
import tree_sitter_python as tspython
import tree_sitter_php as tsphp

#Let's build this slowly. We have a little time for this one.
#USE field names WHEN AVAILABLE otherwise we need to use the stupid list...

        
class nst_node():
    def __init__(self,ntype,children,str_val,lang=None):
        self.ntype = ntype
        self.children = children
        self.str_val = str_val
        self.lang = lang

class BsNormalizer():
    def __init__(self):
        self.language = None
        self.nst_nodes = {
                          }
        #self.op_nodes = ["="]
        self.file_string = None
        self.trash = []

    def _get_field_names(self,node):
        for i in range(len(node.children)):
            print(node.field_name_for_child(i))
        quit()

    def _print_tree(self,node, indent=0):
        print("  " * indent + node.type)
        for child in node.children:
            self._print_tree(child, indent + 1)

    def _print_nst(self,node, indent=0):
        if node.str_val != None:
            print("  " * indent + node.ntype, node.str_val.replace("\n",""))
        else:
            print("  " * indent + node.ntype)
        for child in node.children:
            self._print_nst(child, indent + 1)

    def parse_file_string(self, start_token, stop_token):
        return self.file_string[start_token:stop_token+1].lstrip().rstrip()

    def normalize_type(self,node):
        if node.type in self.nst_nodes:
            return self.nst_nodes[node.type]
        elif node.type in self.trash:
            return node.type
        else:
            self._print_tree(node)
            raise NotImplementedError(f"No handler for {node.type}")

    def eval_nst(self,node):
        print(node.ntype)
        for child in node.children:
            self.eval_nst(child)

    def eval_node(self,node,parent=None):
        if isinstance(node,list):
            new_node = nst_node('root',[],None)
            for child in node:
                child_node = self.eval_node(child,new_node)
                if child_node != None:
                    new_node.children.append(child_node)
            return new_node

        else:
            node_string=self.parse_file_string(
                node.byte_range[0],node.byte_range[1])
            node_type = self.normalize_type(node)

            if node.type not in self.trash: 
                #print(node_type,node_string)
                new_node = nst_node(node_type,[],node_string)

                for child in node.children:
                    child_node = self.eval_node(child,new_node)
                    if child_node != None:
                        new_node.children.append(child_node)
                return new_node
            else:
                for child in node.children:
                    #assign trash's children to parent
                    child_node = self.eval_node(child,parent)
                    if child_node != None:
                        parent.children.append(child_node)
                return None

    def analyze(self,target_file):
        LANGUAGE = Language(tspython.language())
        parser = Parser(LANGUAGE)

        with codecs.open(target_file,"r",
                         encoding='utf-8',
                         errors='ignore') as f:
            self.file_string = f.read()

        tree = parser.parse(self.file_string.encode('utf-8'))

        nst = []

        #for node in tree.root_node.children:
        #    _print_tree(node)

        nst_root = self.eval_node(tree.root_node.children,nst)
        self._print_nst(nst_root)

        #for node in nst:
        #    self.eval_nst(node)


        #nst = []
        #for node in tree.root_node.children:
        #    nst.append(node)
        #    self.eval_node(node,nst)


def main():
    n = RbNormalizer()
    n.analyze(sys.argv[1])


if __name__ == "__main__":
    main()

