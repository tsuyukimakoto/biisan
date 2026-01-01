"""
Markdown to docutils XML converter for biisan.

This module provides functionality to parse Markdown files and convert them
to docutils-compatible XML structure, allowing both RST and Markdown files
to be processed through the same pipeline.
"""
import re
import xml.etree.ElementTree as ET
import yaml
from marko import Markdown
from marko import block, inline
from marko.ext.gfm import gfm
from marko.ext.gfm.elements import Table, TableRow, TableCell


def extract_yaml_frontmatter(markdown_text):
    """
    Extract YAML Front Matter from Markdown text.

    Args:
        markdown_text: Markdown source text with optional YAML Front Matter

    Returns:
        tuple: (metadata_dict, content_without_frontmatter)
    """
    # print("[DEBUG] === extract_yaml_frontmatter START ===")
    # print(f"[DEBUG] First 200 chars: {markdown_text[:200]}")

    # YAML Front Matter pattern: starts with ---+ and ends with ---+
    # Support both --- and ---- (and any number of dashes >= 3)
    pattern = r'^-{3,}\s*\n(.*?)\n-{3,}\s*\n'
    match = re.match(pattern, markdown_text, re.DOTALL)

    if match:
        # print("[DEBUG] YAML Front Matter found!")
        yaml_content = match.group(1)
        # print(f"[DEBUG] YAML content: {yaml_content}")
        try:
            metadata = yaml.safe_load(yaml_content)
            # print(f"[DEBUG] Parsed metadata: {metadata}")
            # Remove front matter from content
            content = markdown_text[match.end():]
            # print(f"[DEBUG] Content after YAML (first 100 chars): {content[:100]}")
            return metadata or {}, content
        except yaml.YAMLError as e:
            # If YAML parsing fails, return original content
            # print(f"[DEBUG] YAML parsing failed: {e}")
            return {}, markdown_text
    else:
        # print("[DEBUG] No YAML Front Matter found")
        return {}, markdown_text


def parse_markdown_to_xml(markdown_text):
    """
    Parse Markdown text and convert to docutils-compatible XML ElementTree.
    Supports YAML Front Matter for metadata.

    Args:
        markdown_text: Markdown source text with optional YAML Front Matter

    Returns:
        xml.etree.ElementTree.Element: Root element compatible with docutils XML structure
    """
    # Extract YAML Front Matter
    metadata, content = extract_yaml_frontmatter(markdown_text)

    # Parse Markdown content with GFM (GitHub Flavored Markdown) support
    # This includes table support
    ast = gfm.parse(content)

    # Create root document element (docutils compatible)
    root = ET.Element('document')
    root.set('source', '<markdown>')

    # Create docinfo element for metadata
    docinfo = ET.SubElement(root, 'docinfo')

    # Add metadata to docinfo
    _add_metadata_to_docinfo(metadata, docinfo)

    # Process AST nodes and convert to docutils XML
    _convert_ast_to_xml(ast, root, docinfo)

    return root


def _add_metadata_to_docinfo(metadata, docinfo):
    """
    Convert YAML metadata to docutils docinfo structure.

    Args:
        metadata: Dictionary of metadata from YAML Front Matter
        docinfo: docinfo XML element
    """
    import datetime

    # print(f"[DEBUG] === _add_metadata_to_docinfo START ===")
    # print(f"[DEBUG] Metadata: {metadata}")
    # print(f"[DEBUG] Metadata keys: {list(metadata.keys()) if metadata else 'None'}")

    for key, value in metadata.items():
        # print(f"[DEBUG] Adding field: {key} = {value}")
        # Create field element
        field = ET.SubElement(docinfo, 'field')

        # Create field_name
        field_name = ET.SubElement(field, 'field_name')
        field_name.text = key

        # Create field_body
        field_body = ET.SubElement(field, 'field_body')
        paragraph = ET.SubElement(field_body, 'paragraph')

        # Handle different value types
        if isinstance(value, (list, dict)):
            # For complex types, convert to string
            paragraph.text = str(value)
        elif isinstance(value, datetime.datetime):
            # Format datetime to string (YYYY-MM-DD HH:MM format)
            paragraph.text = value.strftime('%Y-%m-%d %H:%M')
        elif isinstance(value, datetime.date):
            # Format date to string (YYYY-MM-DD format)
            paragraph.text = value.strftime('%Y-%m-%d')
        elif value is None:
            # Handle None values as empty string
            paragraph.text = ''
        else:
            # For simple types (str, int, etc.)
            paragraph.text = str(value)

    # print(f"[DEBUG] === _add_metadata_to_docinfo END ===")
    # print(f"[DEBUG] docinfo now has {len(list(docinfo))} children")


def _convert_ast_to_xml_nested(node, parent, docinfo):
    """
    Convert Marko AST nodes to XML with proper nesting (no section tracking).
    Used for nested structures like lists, quotes, etc.

    Args:
        node: Marko AST node
        parent: Parent XML element
        docinfo: docinfo element for metadata fields
    """
    if isinstance(node, block.Document):
        for child in node.children:
            _convert_ast_to_xml_nested(child, parent, docinfo)

    elif isinstance(node, block.Heading):
        # Headings inside nested structures - treat as regular section
        section = ET.SubElement(parent, 'section')
        title = ET.SubElement(section, 'title')
        _process_inline_children(node.children, title)

    elif isinstance(node, block.Paragraph):
        para = ET.SubElement(parent, 'paragraph')
        _process_inline_children(node.children, para)

    elif isinstance(node, block.List):
        if node.ordered:
            list_elem = ET.SubElement(parent, 'enumerated_list')
            list_elem.set('enumtype', 'arabic')
        else:
            list_elem = ET.SubElement(parent, 'bullet_list')
            list_elem.set('bullet', '-')

        for item in node.children:
            _convert_ast_to_xml_nested(item, list_elem, docinfo)

    elif isinstance(node, block.ListItem):
        item_elem = ET.SubElement(parent, 'list_item')
        for child in node.children:
            _convert_ast_to_xml_nested(child, item_elem, docinfo)

    elif isinstance(node, block.Quote):
        quote_elem = ET.SubElement(parent, 'block_quote')
        for child in node.children:
            _convert_ast_to_xml_nested(child, quote_elem, docinfo)

    elif isinstance(node, block.FencedCode):
        literal = ET.SubElement(parent, 'literal_block')
        literal.set('xml:space', 'preserve')
        if node.lang:
            literal.set('language', node.lang)
        literal.text = node.children[0].children if node.children else ''

    elif isinstance(node, block.CodeBlock):
        literal = ET.SubElement(parent, 'literal_block')
        literal.set('xml:space', 'preserve')
        literal.text = node.children[0].children if node.children else ''

    elif isinstance(node, block.ThematicBreak):
        ET.SubElement(parent, 'transition')

    elif isinstance(node, Table):
        _convert_table_to_xml(node, parent)

    elif isinstance(node, block.HTMLBlock):
        raw = ET.SubElement(parent, 'raw')
        raw.set('format', 'html')
        raw.text = node.children[0].children if node.children else ''

    elif hasattr(node, 'children') and isinstance(node.children, list):
        for child in node.children:
            _convert_ast_to_xml_nested(child, parent, docinfo)


def _convert_ast_to_xml(node, parent, docinfo, current_section_holder=None):
    """
    Convert Marko AST nodes to docutils-compatible XML elements.

    Args:
        node: Marko AST node
        parent: Parent XML element
        docinfo: docinfo element for metadata fields
        current_section_holder: List containing current section element [section or None]
    """
    if current_section_holder is None:
        current_section_holder = [None]

    if isinstance(node, block.Document):
        # Process all children of document
        for child in node.children:
            _convert_ast_to_xml(child, parent, docinfo, current_section_holder)

    elif isinstance(node, block.Heading):
        # Create section at document level with explicit depth from Markdown level
        # All sections are direct children of document (flat structure)
        section = ET.SubElement(parent, 'section')
        # Store Markdown heading level as depth attribute for later processing
        section.set('depth', str(node.level))
        title = ET.SubElement(section, 'title')
        _process_inline_children(node.children, title)
        # Update current section for subsequent content
        current_section_holder[0] = section

    elif isinstance(node, block.Paragraph):
        # Add paragraph to current section, or document if no section yet
        para_parent = current_section_holder[0] if current_section_holder[0] is not None else parent
        para = ET.SubElement(para_parent, 'paragraph')
        _process_inline_children(node.children, para)

    elif isinstance(node, block.List):
        # Lists should be added to current section if one exists, otherwise to parent
        # But we should NOT pass current_section_holder to children - they should nest properly
        list_parent = current_section_holder[0] if current_section_holder[0] is not None else parent
        # Determine list type
        if node.ordered:
            list_elem = ET.SubElement(list_parent, 'enumerated_list')
            list_elem.set('enumtype', 'arabic')
        else:
            list_elem = ET.SubElement(list_parent, 'bullet_list')
            list_elem.set('bullet', '-')

        # Process list items - pass list_elem as parent, NOT current_section_holder
        for item in node.children:
            _convert_ast_to_xml_nested(item, list_elem, docinfo)

    elif isinstance(node, block.ListItem):
        # This should be handled by _convert_ast_to_xml_nested
        item_elem = ET.SubElement(parent, 'list_item')
        for child in node.children:
            _convert_ast_to_xml_nested(child, item_elem, docinfo)

    elif isinstance(node, block.Quote):
        # Quotes should nest properly
        quote_parent = current_section_holder[0] if current_section_holder[0] is not None else parent
        quote_elem = ET.SubElement(quote_parent, 'block_quote')
        for child in node.children:
            _convert_ast_to_xml_nested(child, quote_elem, docinfo)

    elif isinstance(node, block.FencedCode):
        code_parent = current_section_holder[0] if current_section_holder[0] is not None else parent
        literal = ET.SubElement(code_parent, 'literal_block')
        literal.set('xml:space', 'preserve')
        if node.lang:
            literal.set('language', node.lang)
        literal.text = node.children[0].children if node.children else ''

    elif isinstance(node, block.CodeBlock):
        code_parent = current_section_holder[0] if current_section_holder[0] is not None else parent
        literal = ET.SubElement(code_parent, 'literal_block')
        literal.set('xml:space', 'preserve')
        literal.text = node.children[0].children if node.children else ''

    elif isinstance(node, block.ThematicBreak):
        break_parent = current_section_holder[0] if current_section_holder[0] is not None else parent
        ET.SubElement(break_parent, 'transition')

    elif isinstance(node, Table):
        # Convert GFM table to docutils table structure
        table_parent = current_section_holder[0] if current_section_holder[0] is not None else parent
        _convert_table_to_xml(node, table_parent)

    elif isinstance(node, block.HTMLBlock):
        html_parent = current_section_holder[0] if current_section_holder[0] is not None else parent
        raw = ET.SubElement(html_parent, 'raw')
        raw.set('format', 'html')
        raw.text = node.children[0].children if node.children else ''

    elif hasattr(node, 'children') and isinstance(node.children, list):
        # Generic block element with children
        for child in node.children:
            _convert_ast_to_xml(child, parent, docinfo, current_section_holder)


def _convert_table_to_xml(table_node, parent):
    """
    Convert GFM Table to docutils table structure.

    Args:
        table_node: Marko Table node
        parent: Parent XML element
    """
    # Create table element
    table_elem = ET.SubElement(parent, 'table')

    # Create tgroup (table group) with column count
    num_cols = table_node.num_of_cols
    tgroup = ET.SubElement(table_elem, 'tgroup')
    tgroup.set('cols', str(num_cols))

    # Add colspec elements for each column
    for i in range(num_cols):
        colspec = ET.SubElement(tgroup, 'colspec')
        colspec.set('colwidth', '1')  # Equal width columns

    # Process table rows
    if len(table_node.children) > 0:
        # First row is the header in GFM tables
        thead = ET.SubElement(tgroup, 'thead')
        _convert_table_row_to_xml(table_node.children[0], thead)

        # Remaining rows are the body
        if len(table_node.children) > 1:
            tbody = ET.SubElement(tgroup, 'tbody')
            for row_node in table_node.children[1:]:
                _convert_table_row_to_xml(row_node, tbody)


def _convert_table_row_to_xml(row_node, parent):
    """
    Convert a table row to XML.

    Args:
        row_node: Marko TableRow node
        parent: Parent XML element (thead or tbody)
    """
    row = ET.SubElement(parent, 'row')

    for cell_node in row_node.children:
        _convert_table_cell_to_xml(cell_node, row)


def _convert_table_cell_to_xml(cell_node, parent):
    """
    Convert a table cell to XML.

    Args:
        cell_node: Marko TableCell node
        parent: Parent XML element (row)
    """
    entry = ET.SubElement(parent, 'entry')

    # Process inline content in the cell
    if cell_node.children:
        para = ET.SubElement(entry, 'paragraph')
        _process_inline_children(cell_node.children, para)


def _extract_text_from_inline(children):
    """
    Extract plain text from inline elements.

    Args:
        children: List of inline AST nodes

    Returns:
        str: Extracted plain text
    """
    if not children:
        return ''

    text_parts = []
    for child in children:
        if isinstance(child, inline.RawText):
            text_parts.append(child.children)
        elif isinstance(child, inline.CodeSpan):
            text_parts.append(child.children)
        elif hasattr(child, 'children'):
            if isinstance(child.children, str):
                text_parts.append(child.children)
            else:
                text_parts.append(_extract_text_from_inline(child.children))
    return ''.join(text_parts)


def _process_inline_children(children, parent):
    """
    Process inline elements (text, emphasis, strong, etc.)

    Args:
        children: List of inline AST nodes
        parent: Parent XML element
    """
    for child in children:
        if isinstance(child, inline.RawText):
            # Add text to parent.text or last child's tail
            if len(parent) == 0:
                # No children yet, add to parent.text
                if parent.text is None:
                    parent.text = child.children
                else:
                    parent.text += child.children
            else:
                # Has children, add to last child's tail
                last = parent[-1]
                if last.tail is None:
                    last.tail = child.children
                else:
                    last.tail += child.children

        elif isinstance(child, inline.Emphasis):
            elem = ET.SubElement(parent, 'emphasis')
            _process_inline_children(child.children, elem)

        elif isinstance(child, inline.StrongEmphasis):
            elem = ET.SubElement(parent, 'strong')
            _process_inline_children(child.children, elem)

        elif isinstance(child, inline.Link):
            ref = ET.SubElement(parent, 'reference')
            ref.set('refuri', child.dest)
            if child.title:
                ref.set('title', child.title)
            # Set the text content from children (for Reference.text property)
            ref.text = _extract_text_from_inline(child.children)
            # Note: We set ref.text for the Reference model, but don't process children
            # to avoid duplicate text in XML

        elif isinstance(child, inline.Image):
            img = ET.SubElement(parent, 'image')
            img.set('uri', child.dest)
            # In Markdown: ![alt text](url "optional title")
            # child.children contains the alt text
            # child.title contains the optional title attribute
            if child.children:
                alt_text = _extract_text_from_inline(child.children)
                img.set('alt', alt_text)
            if child.title:
                img.set('title', child.title)

        elif isinstance(child, inline.CodeSpan):
            # Create literal element for inline code
            literal = ET.SubElement(parent, 'literal')
            literal.text = child.children
            # Don't set tail here - it will be set by next RawText

        elif isinstance(child, inline.LineBreak):
            # Add line break as text
            if parent.text is None:
                parent.text = '\n'
            else:
                if len(parent):
                    last = parent[-1]
                    if last.tail is None:
                        last.tail = '\n'
                    else:
                        last.tail += '\n'
                else:
                    parent.text += '\n'

        elif isinstance(child, inline.InlineHTML):
            raw = ET.SubElement(parent, 'raw')
            raw.set('format', 'html')
            raw.text = child.children

        elif hasattr(child, 'children'):
            _process_inline_children(
                [child.children] if isinstance(child.children, str) else child.children,
                parent
            )
