#!/usr/bin/python3

import gi
gi.require_version('Rsvg', '2.0')
from gi.repository import Rsvg
gi.require_version('Pango', '1.0')
from gi.repository import Pango
gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo
import cairo
import re
import sys

EXTRACT_WORD_RE = re.compile(r'^[^\t]*\t *([^\t\n]+?) *(?:\t|$)')

POINTS_PER_MM = 2.8346457

PAGE_WIDTH = 210
PAGE_HEIGHT = 297

CARDS_START = (124.0 * 210.0 / 2480.0, 194.0 * 210.0 / 2480.0)
CARD_SIZE = (744.0 * 210.0 / 2480.0, 1039.0 * 210.0 / 2480.0)

COLUMNS_PER_PAGE = 3
LINES_PER_PAGE = 3
CARDS_PER_PAGE = COLUMNS_PER_PAGE * LINES_PER_PAGE
WORDS_PER_CARD = 5

CARD_BORDER_SIZE = 3

WORD_HEIGHT = CARD_SIZE[1] / (WORDS_PER_CARD * 2 + 1)
WORD_WIDTH = CARD_SIZE[0] * 4 / 5
NUMBER_WIDTH = 5
HORIZONTAL_GAP = (CARD_SIZE[0] - NUMBER_WIDTH - WORD_WIDTH) / 2
TEXT_INSET = 3

class CardGenerator:
    def __init__(self):
        self.surface = cairo.PDFSurface("nur_unu.pdf",
                                        PAGE_WIDTH * POINTS_PER_MM,
                                        PAGE_HEIGHT * POINTS_PER_MM)

        self.cr = cairo.Context(self.surface)

        # Use mm for the units from now on
        self.cr.scale(POINTS_PER_MM, POINTS_PER_MM)

        # Use ½mm line width
        self.cr.set_line_width(0.5)

        self.word_num = 0

    def _draw_outlines(self):
        self.cr.set_source_rgb(0, 0, 0)

        self.cr.rectangle(0, 0,
                          CARD_SIZE[0] * COLUMNS_PER_PAGE,
                          CARD_SIZE[1] * LINES_PER_PAGE)

        for i in range(1, COLUMNS_PER_PAGE):
            self.cr.move_to(CARD_SIZE[0] * i, 0)
            self.cr.rel_line_to(0, CARD_SIZE[1] * LINES_PER_PAGE)

        for i in range(1, LINES_PER_PAGE):
            self.cr.move_to(0, CARD_SIZE[1] * i)
            self.cr.rel_line_to(CARD_SIZE[0] * COLUMNS_PER_PAGE, 0)

        self.cr.stroke()

    def add_word(self, word):
        word_in_card = self.word_num % WORDS_PER_CARD
        card_num = self.word_num // WORDS_PER_CARD
        card_in_page = card_num % CARDS_PER_PAGE

        self.cr.save()
        self.cr.translate(card_in_page %
                          COLUMNS_PER_PAGE *
                          CARD_SIZE[0] +
                          CARDS_START[0],
                          card_in_page //
                          COLUMNS_PER_PAGE *
                          CARD_SIZE[1] +
                          CARDS_START[1])

        if word_in_card == 0 and card_in_page == 0:
            if card_num != 0:
                self.cr.show_page()

            self._draw_outlines()

        self.cr.translate(HORIZONTAL_GAP + NUMBER_WIDTH,
                          (word_in_card * 2 + 1) * WORD_HEIGHT)
        self.cr.rectangle(0, 0, WORD_WIDTH, WORD_HEIGHT)
        self.cr.rectangle(-NUMBER_WIDTH, 0, NUMBER_WIDTH, WORD_HEIGHT)
        self.cr.stroke()

        self.cr.set_font_size(WORD_HEIGHT / 1.7)
        font_extents = self.cr.font_extents()
        baseline_pos = WORD_HEIGHT / 2 + font_extents[0] / 2

        num = "{}".format(word_in_card + 1)
        extents = self.cr.text_extents(num)
        self.cr.move_to(-extents.x_bearing -
                        extents.width / 2 -
                        NUMBER_WIDTH / 2,
                        baseline_pos)
        self.cr.show_text(num)

        self.cr.move_to(TEXT_INSET, baseline_pos)
        self.cr.show_text(word)

        self.cr.restore()

        self.word_num += 1

generator = CardGenerator()

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
            generator.add_word(word)
            all_words.add(word)
