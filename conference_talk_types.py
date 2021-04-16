#!/usr/bin/env python3
# *_* coding: utf-8 *_*

"""Constants and utility functions for the types of talks in conferences.json"""

__version__ = "1.0.0"
__author__ = "Kevin Goldsmith"
__copyright__ = "Copyright 2021, Kevin Goldsmith"
__license__ = "MIT"
__status__ = "Production"                               # Prototype, Development or Production

# --------------------------------------------------------------------------------

#string constants
TALK_TYPE_KEYNOTE = 'keynote'
TALK_TYPE_TALK = 'talk'
TALK_TYPE_PANEL = 'panel'
TALK_TYPE_PANEL_CHAIR = 'panel (chair)'
TALK_TYPE_LAB = 'lab'
TALK_TYPE_WORKSHOP = 'workshop'

def has_valid_talk_type(talk):
    """Is this a known type of talk or something new (or missing)?"""
    return talk.get('talk-type') in [
        TALK_TYPE_KEYNOTE,
        TALK_TYPE_TALK,
        TALK_TYPE_PANEL,
        TALK_TYPE_PANEL_CHAIR,
        TALK_TYPE_LAB,
        TALK_TYPE_WORKSHOP]

def is_workshop(talk):
    """is this talk a workshop?"""
    return talk.get('talk-type') in [TALK_TYPE_LAB, TALK_TYPE_WORKSHOP]

def is_talk(talk):
    """is this talk a talk (versus workshop or panel)?"""
    return talk.get('talk-type') in [TALK_TYPE_TALK, TALK_TYPE_KEYNOTE]

def is_panel(talk):
    """is this talk a panel?"""
    return talk.get('talk-type') in [TALK_TYPE_PANEL, TALK_TYPE_PANEL_CHAIR]
