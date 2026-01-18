# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Forge'
copyright = f'{datetime.now().year}, ning3739'
author = 'ning3739'
release = '0.1.8.5'
version = '0.1.8'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'myst_parser',  # Support for Markdown
    'sphinx_copybutton',  # Copy button for code blocks
    'sphinxcontrib.mermaid',  # Mermaid diagram support
]

# MyST Parser configuration (for Markdown support)
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

# Mermaid configuration
mermaid_version = "latest"  # Use latest Mermaid version
myst_fence_as_directive = ["mermaid"]  # Enable mermaid code blocks in MyST

# Support both .rst and .md files
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Custom CSS files
html_css_files = [
    'custom.css',
]

# Theme options
html_theme_options = {
    'logo_only': False,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
    'style_nav_header_background': '#2980B9',
    # Toc options
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Use ReadTheDocs default logo and favicon
# html_logo = '../assets/logo.svg'
# html_favicon = '../assets/favicon.ico'

# The master toctree document.
master_doc = 'index'

# GitHub repository
html_context = {
    'display_github': True,
    'github_user': 'ning3739',
    'github_repo': 'forge',
    'github_version': 'main',
    'conf_py_path': '/docs/',
}

# -- Options for intersphinx extension ---------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

# -- Options for autodoc extension -------------------------------------------

autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
