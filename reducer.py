#!/usr/bin/env python3
"""Status reducer for Server Status over HTTP HEAD"""

# Using
from collections import OrderedDict
from heapq import merge
from re import compile, findall
from time import strftime
from xml.etree.ElementTree import Element, SubElement, tostring


# Configuration
config_tag = "abcwtf"
config_entity_key = "name"
config_entity_from = "_source_from"
config_entity_date = "_source_date"

config_log_path = "access.log"
config_line_limit = 1000

config_page_path = "/usr/share/nginx/ssohh/home.html"
config_page_template = "template.html"
config_page_tag_title = "{{title}}"
config_page_tag_notice = "{{notice}}"
config_page_tag_content = "{{content}}"
config_page_tags = [
    config_page_tag_title,
    config_page_tag_notice,
    config_page_tag_content
]


# Load log file by line
with open(config_log_path, 'r') as log_file:
    log_raw = log_file.readlines()
    log_lines = [line_raw.strip() for line_raw in log_raw if not line_raw.isspace()]


# Only needs latest lines in reverse chronological order
count_line_total = len(log_lines)
log_lines = log_lines[-config_line_limit:][::-1]
count_line_selected = len(log_lines)


# Extract status entity from SSoHH log lines
log_identity = '[ssohh] {:s};'.format(config_tag)
source_pattern = compile(r"^(.*?)\s.*?\[(.*?)\]")
section_pattern = compile(r"\[(.*?)\](.*?);")
def extract_status_entity(log_line):
    # Extract raw status string
    status_pos_start = log_line.find(log_identity)
    if status_pos_start < 0:
        return None, None
    status_pos_end = log_line.rfind('"')
    status_string = log_line[status_pos_start + len(log_identity) : status_pos_end]
    # Save source info into entity
    status_entity = {}
    section_keys = []
    source_match = source_pattern.search(log_line)
    if source_match:
        status_entity[config_entity_from] = source_match.group(1)
        status_entity[config_entity_date] = source_match.group(2)
    # Convert status string into entity
    for (section_key, section_value) in findall(section_pattern, status_string):
        section_key = section_key.strip().lower()
        status_entity[section_key] = section_value.strip()
        section_keys.append(section_key)
    return status_entity, section_keys


# Merge sorted list without duplicate items
def merge_sorted_and_unique_lists(list1, list2):
    list_merged = list(merge(list1, list2))
    items_existed = set()
    list_result = []
    for item in list_merged:
        if item not in items_existed:
            list_result.append(item)
            items_existed.add(item)
    return list_result


# Keep only the latest status entity for each server
status_entities = {}
section_all_keys = []
for line in log_lines:
    status_entity, section_keys = extract_status_entity(line)
    if status_entity and config_entity_key in status_entity:
        entity_key = status_entity[config_entity_key]
        if not entity_key in status_entities:
            status_entities[entity_key] = status_entity
            section_all_keys = merge_sorted_and_unique_lists(section_all_keys, section_keys)

status_entities = OrderedDict(sorted(status_entities.items(), key = lambda x:x[0].lower(), reverse = False))


# Load page template
with open(config_page_template, 'r') as template_file:
    template_lines = template_file.readlines()


# Prepare page entity
page_entity = {}
page_entity[config_page_tag_title] = "SSoHH Summary Page"
page_entity[config_page_tag_notice] = "Report generated at {:s} based on last {:d} of {:d} lines in {:s}".format(strftime("%Y-%m-%d %H:%M:%S %z %Z"), count_line_selected, count_line_total, config_log_path)
# Convert status entities into HTML table
table_root = Element("table")
table_header = SubElement(table_root, "tr")
# Table header
SubElement(table_header, "th").text = "time"
SubElement(table_header, "th").text = "from"
for section_key in section_all_keys:
    SubElement(table_header, "th").text = section_key
section_all_keys = [config_entity_date, config_entity_from] + section_all_keys
# Table content
for entity_key in status_entities:
    status_entity = status_entities[entity_key]
    table_row = SubElement(table_root, "tr")
    for section_key in section_all_keys:
        if section_key in status_entity:
            SubElement(table_row, "td").text = status_entity[section_key]
        else:
            SubElement(table_row, "td").text = "-"
# Show no data message if no result
if not status_entities:
    message_root = Element("div", { "class": "warning" })
    message_root.text = "No Data Extracted!"
    table_root = message_root
page_entity[config_page_tag_content] = tostring(table_root, encoding="unicode")


# Render page with template & entity
page_lines = []
for template_line in template_lines:
    page_line = template_line
    for page_tag in config_page_tags:
        page_line = page_line.replace(page_tag, page_entity[page_tag])
    page_lines.append(page_line)

with open(config_page_path, 'w') as page_file:
    for page_line in page_lines:
        page_file.write(page_line)
