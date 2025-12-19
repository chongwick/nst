import os
import sys
#from tree_sitter import Parser, Language
#import tree_sitter_ruby as tsruby
#import tree_sitter_python as tspython
#import tree_sitter_php as tsphp
from normalizers.py_normalize import PyNormalizer
from normalizers.ph_normalize import PhNormalizer
from normalizers.rb_normalize import RbNormalizer
#import json
#import codecs


def main():
    target_file = sys.argv[1]
    normalizer = None
    if target_file.split(".")[-1] == "rb":
        normalizer = RbNormalizer()
    elif target_file.split(".")[-1] == "py":
        normalizer = PyNormalizer()
    elif target_file.split(".")[-1] == "php":
        normalizer = PhNormalizer()

    normalizer.analyze(target_file)



if __name__ == "__main__":
    main()
