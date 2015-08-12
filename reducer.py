#!/usr/bin/env python3
"""Status reducer for Server Status over HTTP HEAD"""

# Using
from re import compile, findall
from collections import OrderedDict


# Configuration
config_tag = "abcwtf"
config_entity_key = "name"
config_entity_from = "_source_from"
config_entity_date = "_source_date"

config_log_name = "access.log"
config_line_limit = 1000

config_page_name = "home.html"
config_page_directory = ""


# Load log file by line
with open(config_log_name, 'r') as log_file:
    log_raw = log_file.readlines()
    log_lines = [line_raw.strip() for line_raw in log_raw if not line_raw.isspace()]


# Only needs latest lines in reverse chronological order
log_lines = log_lines[-config_line_limit:][::-1]


# Extract status entity from SSoHH log lines
log_identity = '[ssohh] {:s};'.format(config_tag)
source_pattern = compile(r"^(.*?)\s.*?\[(.*?)\]")
section_pattern = compile(r"\[(.*?)\](.*?);")
def extract_status_entity(log_line):
    # Extract raw status string
    status_pos_start = log_line.find(log_identity)
    if status_pos_start < 0:
        return
    status_pos_end = log_line.rfind('"')
    status_string = log_line[status_pos_start + len(log_identity) : status_pos_end]
    # Save source info into entity
    status_entity = OrderedDict()
    source_match = source_pattern.search(log_line)
    if source_match:
        status_entity[config_entity_from] = source_match.group(1)
        status_entity[config_entity_date] = source_match.group(2)
    # Convert status string into entity
    for (section_key, section_value) in findall(section_pattern, status_string):
        status_entity[section_key.strip().lower()] = section_value.strip()
    return status_entity


# Keep only the latest status entity for each server
status_entities = {}
for line in log_lines:
    status_entity = extract_status_entity(line)
    if status_entity and config_entity_key in status_entity:
        entity_key = status_entity[config_entity_key]
        if not entity_key in status_entities:
            status_entities[entity_key] = status_entity
status_entities = OrderedDict(sorted(status_entities.items(), key = lambda x:x[0].lower(), reverse = False))


for entity_key in status_entities:
    print(entity_key, status_entities[entity_key], "\n")
