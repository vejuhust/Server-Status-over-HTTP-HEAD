#!/usr/bin/env python3
"""Status reducer for Server Status over HTTP HEAD"""

# Using
from collections import OrderedDict
from heapq import merge
from re import compile, findall
from time import strftime
from xml.etree.ElementTree import Element, SubElement, tostring


# Configuration
config_tag = "YOUR_PRIVATE_TAG_FOR_SSOHH"
config_entity_key = "name"
config_entity_from = "_source_from"
config_entity_date = "_source_date"

config_log_path = "/var/log/nginx/access.log"
config_line_limit = 1000
config_time_format = "%Y-%m-%d %H:%M:%S %z %Z"

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


# Load file by lines
def load_file_lines(file_path, allow_blank = True):
    with open(file_path, 'r') as input_file:
        lines_raw = input_file.readlines()
        if allow_blank:
            lines = lines_raw
        else:
            lines = [line.strip() for line in lines_raw if not line.isspace()]
    return lines


# Save file lines
def save_file_lines(file_path, lines):
    with open(file_path, 'w') as output_file:
        for line in lines:
            output_file.write(line)


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


# Extract the latest status entity for each server
def extract_all_status_entities_and_keys(log_lines):
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
    return status_entities, section_all_keys


# Prepare page entity with valid data
def fill_page_entity_data(status_entities, section_all_keys, count_line_total, count_line_selected):
    page_entity = {}
    page_entity[config_page_tag_title] = "SSoHH Summary Page :-)"
    page_entity[config_page_tag_notice] = "Report generated at {:s} based on last {:d} of {:d} lines from {:s}".format(strftime(config_time_format), count_line_selected, count_line_total, config_log_path)
    # Convert status entities into HTML table
    table_root = Element("table")
    table_header = SubElement(table_root, "tr")
    # Table header
    SubElement(table_header, "th").text = "no"
    SubElement(table_header, "th").text = "time"
    SubElement(table_header, "th").text = "from"
    for section_key in section_all_keys:
        SubElement(table_header, "th").text = section_key
    section_all_keys = [config_entity_date, config_entity_from] + section_all_keys
    # Table content
    entity_index = 0
    for entity_key, status_entity in status_entities.items():
        table_row = SubElement(table_root, "tr")
        entity_index += 1
        SubElement(table_row, "td").text = str(entity_index)
        for section_key in section_all_keys:
            if section_key in status_entity:
                SubElement(table_row, "td").text = status_entity[section_key]
            else:
                SubElement(table_row, "td").text = "-"
    page_entity[config_page_tag_content] = tostring(table_root, encoding="unicode")
    return page_entity


# Prepare page entity with error message
def fill_page_entity_error(message):
    page_entity = {}
    page_entity[config_page_tag_title] = "SSoHH Error Page :-("
    page_entity[config_page_tag_notice] = "Report generated at {:s} from {:s}".format(strftime(config_time_format), config_log_path)
    message_root = Element("div", { "class": "warning" })
    message_root.text = message
    page_entity[config_page_tag_content] = tostring(message_root, encoding="unicode")
    return page_entity


# Main function
if __name__ == '__main__':
    error_message = ""
    try:
        # Load latest log lines in reverse chronological order
        log_lines = load_file_lines(config_log_path, False)
        count_line_total = len(log_lines)
        log_lines = log_lines[-config_line_limit:][::-1]
        count_line_selected = len(log_lines)
    except Exception as e:
        error_message = "Failed to Load Log: {:s}".format(str(e))
    else:
        # Get the status entities and section keys
        status_entities, section_all_keys = extract_all_status_entities_and_keys(log_lines)
        if not status_entities:
            error_message = "No Data Extracted!"

    # Prepare page entity
    if error_message:
        page_entity = fill_page_entity_error(error_message)
    else:
        page_entity = fill_page_entity_data(status_entities, section_all_keys, count_line_total, count_line_selected)

    # Load page template
    template_lines = load_file_lines(config_page_template)

    # Render page with template & entity
    page_lines = []
    for template_line in template_lines:
        page_line = template_line
        for page_tag in config_page_tags:
            page_line = page_line.replace(page_tag, page_entity[page_tag])
        page_lines.append(page_line)

    # Save as text/HTML file
    save_file_lines(config_page_path, page_lines)
