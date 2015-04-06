#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import re
import argparse
import numpy as np
import json
import commands as cmd

from src.utils import *
from src.importer import *
from src.db_layer import *
from src.feature_extractor import *

if __name__ != '__main__':
    os.sys.exit(1)


parser = argparse.ArgumentParser(\
    description="Imports dataset and trains and computes authors' features.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--cleardataset', metavar="C", nargs=1,
                    default=[0], type=int,
                    help='Clear imported dataset')
parser.add_argument('--clearfeatures', metavar="C", nargs=1,
                    default=[0], type=int,
                    help='Clear previous features (0-1)')
parser.add_argument('--language', metavar="lang", nargs='?',
                    default=['EN','DU','GR','SP'],
                    help='Only handles the given languages')
parser.add_argument('-i', metavar="path", nargs='?',
                    default=[''], help='Importer input path.')
parser.add_argument('-o', metavar="path", nargs='?',
                    default=['dataset/'], help='Output path.')
parser.add_argument('--train', metavar="T", nargs=1,
                    default=[1], type=int,
                    help='Train features (0-1)')
parser.add_argument('--compute', metavar="C", nargs=1,
                    default=[1], type=int,
                    help='Compute features (0-1)')
parser.add_argument('--config', metavar="conf", nargs='?',
                    default="conf/config.json", help='Configuration file')
args = parser.parse_args()

config = get_configuration(args.config)

if type(args.language) == str:
    args.language = [args.language]

if args.i != '':
    clear(args.language , args.o, bool(args.cleardataset[0]))    
    import_languages(config, args.language , args.i, args.o)

db = db_layer(args.config)

fe = concat_fe(args.config,
               [
                   pos_fe(args.config),
                   hapax_fe(args.config),
                   word_distribution_fe(args.config),
                   clear_fe(args.config),
                   num_tokens_fe(args.config),
                   stop_words_fe(args.config),
                   punctuation_fe(args.config),
                   structure_fe(args.config),
                   char_distribution_fe(args.config)
               ])

for ln in args.language:
    print "Language:", ln

    authors = db.get_authors(ln)

    if args.clearfeatures[0]:
        print "Clearing features..."
        for id_author, author in enumerate(authors):
            db.clear_features(author, commit=True)

            if id_author % 10 == 0:
                print "%0.2f%%\r" % (id_author * 100.0 / len(authors)),
                os.sys.stdout.flush()

    if args.train[0]:
        print "Training features..."
        fe.train(authors)

    if args.compute[0]:
        print "Computing features..."
        for id_author, author in enumerate(authors):
            author = fe.compute(author)
            if id_author % 10 == 0:
                print "%0.2f%%\r" % (id_author * 100.0 / len(authors)),
                os.sys.stdout.flush()
        print
    print