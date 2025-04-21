import os
import sys
import django


# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------

project = 'Orange County Lettings - Site'
copyright = '2025, OC Lettings'
author = 'OC Lettings'

# -- General configuration ---------------------------------------------------

extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

sys.path.insert(0, os.path.abspath('..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'oc_lettings_site.settings'
django.setup()

templates_path = ['_templates']

exclude_patterns = [
    '_build', 'Thumbs.db', '.DS_Store', '.venv', '.github', '.pytest_cache',
    '.__pycache__', '._unused', '.docs', '.reports', '.static', '.venv',
    '.CHECK_BDD.py', '.oc-lettings-site.sqlite3',
    '.oc_lettings_site/__pycache__', '.oc_lettings_site/migrations',
    '.oc_lettings_site/templates', '.oc_lettings_site/tests_app.py',
    '.lettings/__pycache__', '.lettings/migrations', '.lettings/templates',
    '.lettings/tests_app.py', '.lettings/tests_migrations.py',
    '.profiles/__pycache__', '.profiles/migrations', '.profiles/templates',
    '.profiles/tests_app.py', '.profiles/tests_migrations.py',
]

# -- Options for HTML output -------------------------------------------------

master_doc = 'index'
html_theme = 'alabaster'
html_static_path = ['_static']

# -- Options for language output ---------------------------------------------

language = 'en'

if os.environ.get('READTHEDOCS_LANGUAGE') == 'fr':
    language = 'fr'
