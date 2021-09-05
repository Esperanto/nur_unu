#!/usr/bin/python3

import re
import sys

EXTRACT_WORD_RE = re.compile(r'^[^\t]*\t *([^\t\n]+?) *(?:\t|$)')

line_num = 0
all_words = set()

with open('vortoj.csv', 'rt') as f:
    for line in f:
        line_num += 1

        md = EXTRACT_WORD_RE.match(line)
        if md is None:
            continue

        word = md.group(1)

        if word in all_words:
            print("Ripetita vorto “{}” trovita ĉe linio {}".
                  format(word, line_num),
                  file=sys.stderr)
        else:
            all_words.add(word)

        print(word)
