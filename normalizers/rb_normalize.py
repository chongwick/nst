import json
import codecs
import os
import sys
from tree_sitter import Parser, Language
import tree_sitter_ruby as tsruby
import tree_sitter_python as tspython
import tree_sitter_php as tsphp
from base_normalize import BsNormalizer,nst_node

class RbNormalizer(BsNormalizer):
    def __init__(self):
        self.language = None
        self.nst_nodes = {"expression_statement": "stmt_expr",
                          "assignment": "assign",
                          "identifier": "identifier",
                          "integer": "integer",
                          "if": "if_stmt",
                          "elsif": "elif_clause",
                          "else": "else_clause",
                          "comparison_operator": "middle_op_node",
                          "binary_operator": "middle_op_node",
                          "binary":"middle_op_node"}
        #with open("lang_description.json","r") as f:
        #    self.nst_nodes = json.load(f)
        self.file_string = None
        self.trash = ["end","then","comment","-","==","/","*",";",">","+","=",":","block"]

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

            #if node_type == "middle_op_node":
            #    node_string = self.parse_file_string(
            #            node.children[1].byte_range[0],
            #            node.children[1].byte_range[1])


            if node.type not in self.trash: 
                #print(node_type,node_string)
                new_node = nst_node(node_type,[],node_string)

                #We gotta do this because ruby ast is differently stupid
                if new_node.ntype == "if_stmt" and (
                        parent.ntype == "if_stmt"):
                    new_node.ntype = "if_clause"
                elif ((new_node.ntype == "elif_clause" and 
                      parent.ntype == "elif_clause") or
                      new_node.ntype == "else_clause" and 
                      parent.ntype == "else_clause"):
                    new_node


                #if new_node.ntype == "if_stmt":
                #    tmp = nst_node("if_clause",[],None)
                #    #We gotta pop these off the list because we don't want to 
                #    #repeat add them to the nst in the main for loop
                #    while len(node.children) != 0:
                #        child = node.children[0]
                #    #for child in node.children:
                #        if self.normalize_type(child) == "else_clause" or (
                #                self.normalize_type(child) == "elif_clause"):
                #            break;
                #        else:
                #            node.children.pop(0)
                #            child_node = self.eval_node(child,tmp)
                #            if child_node != None:
                #                tmp.children.append(child_node)
                #    new_node.children.append(tmp)

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
        LANGUAGE = Language(tsruby.language())
        parser = Parser(LANGUAGE)

        with codecs.open(target_file,"r",
                         encoding='utf-8',
                         errors='ignore') as f:
            self.file_string = f.read()

        tree = parser.parse(self.file_string.encode('utf-8'))

        nst = []

        for node in tree.root_node.children:
            self._print_tree(node)

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

