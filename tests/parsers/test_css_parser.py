import pytest
from bs4 import BeautifulSoup
from intelligent_data_platform.parsers.css_parser import CSSParser

# Sample HTML content for testing
SAMPLE_HTML_SINGLE = """
<div class="product-card">
    <h2 class="product-title">Laptop Pro</h2>
    <span class="product-price">$1200.00</span>
    <a class="product-link" href="/products/laptop-pro">View Details</a>
    <div class="description">
        <p>Powerful laptop for professionals.</p>
    </div>
</div>
"""

SAMPLE_HTML_MULTIPLE = """
<div class="product-list">
    <div class="product-card">
        <h2 class="product-title">Laptop Pro</h2>
        <span class="product-price">$1200.00</span>
        <a class="product-link" href="/products/laptop-pro">View Details</a>
    </div>
    <div class="product-card">
        <h2 class="product-title">Smartphone X</h2>
        <span class="product-price">$800.50</span>
        <a class="product-link" href="/products/smartphone-x">View Details</a>
    </div>
    <div class="product-card">
        <h2 class="product-title">Monitor Ultra</h2>
        <span class="product-price">$300.00</span>
        <a class="product-link" href="/products/monitor-ultra">View Details</a>
    </div>
</div>
"""

SAMPLE_HTML_MISSING_ELEMENTS = """
<div class="product-card">
    <h2 class="product-title">Laptop Pro</h2>
    <!-- Price missing -->
    <a class="product-link" href="/products/laptop-pro">View Details</a>
</div>
"""

@pytest.fixture
def css_parser():
    return CSSParser()

def test_parse_single_item_text_and_attr(css_parser):
    config = {
        'container': '.product-card',
        'fields': {
            'title': 'h2.product-title::text',
            'price': '.product-price::text',
            'link': '.product-link::attr(href)'
        }
    }
    result = css_parser.parse(SAMPLE_HTML_SINGLE, config)
    assert len(result) == 1
    assert result[0]['title'] == 'Laptop Pro'
    assert result[0]['price'] == '$1200.00'
    assert result[0]['link'] == '/products/laptop-pro'

def test_parse_multiple_items(css_parser):
    config = {
        'container': '.product-card',
        'fields': {
            'title': 'h2.product-title::text',
            'price': '.product-price::text'
        }
    }
    result = css_parser.parse(SAMPLE_HTML_MULTIPLE, config)
    assert len(result) == 3
    assert result[0]['title'] == 'Laptop Pro'
    assert result[1]['title'] == 'Smartphone X'
    assert result[2]['title'] == 'Monitor Ultra'
    assert result[0]['price'] == '$1200.00'
    assert result[1]['price'] == '$800.50'
    assert result[2]['price'] == '$300.00'

def test_parse_missing_field_element(css_parser):
    config = {
        'container': '.product-card',
        'fields': {
            'title': 'h2.product-title::text',
            'price': '.non-existent-price::text' # This selector will not find anything
        }
    }
    result = css_parser.parse(SAMPLE_HTML_MISSING_ELEMENTS, config)
    assert len(result) == 1
    assert result[0]['title'] == 'Laptop Pro'
    assert result[0]['price'] is None # Should be None if not found

def test_parse_missing_container(css_parser):
    config = {
        'container': '.non-existent-container',
        'fields': {
            'title': 'h2.product-title::text'
        }
    }
    result = css_parser.parse(SAMPLE_HTML_SINGLE, config)
    assert len(result) == 0 # No containers found, so no results

def test_parse_empty_html(css_parser):
    config = {
        'container': '.product-card',
        'fields': {
            'title': 'h2.product-title::text'
        }
    }
    result = css_parser.parse("", config)
    assert len(result) == 0

def test_parse_invalid_html(css_parser):
    config = {
        'container': '.product-card',
        'fields': {
            'title': 'h2.product-title::text'
        }
    }
    result = css_parser.parse("<!DOCTYPE html><html", config) # Incomplete HTML
    assert len(result) == 0

def test_parse_no_fields_in_config(css_parser):
    config = {
        'container': '.product-card',
        'fields': {} # No fields specified
    }
    result = css_parser.parse(SAMPLE_HTML_SINGLE, config)
    assert len(result) == 0 # Should return empty if no fields to extract

def test_parse_no_container_in_config(css_parser):
    config = {
        'fields': {
            'title': 'h2.product-title::text'
        }
    }
    result = css_parser.parse(SAMPLE_HTML_SINGLE, config)
    assert len(result) == 0 # Should return empty if no container specified
