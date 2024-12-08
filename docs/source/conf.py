# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
from urllib.request import urlopen
from pathlib import Path
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'snotes'
copyright = '2024, xuzizheng'
author = 'xuzizheng'
release = '1.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "ablog",
    "myst_nb",
    "numpydoc",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinxcontrib.youtube",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_examples",
    "sphinx_tabs.tabs",
    "sphinx_thebe",
    "sphinx_togglebutton",
    "sphinxcontrib.bibtex",
    "runthis.sphinxext",
    # For the kitchen sink
    "sphinx.ext.todo",
    "sphinx_sitemap"
]

# 设置网站的基本 URL
html_baseurl = 'https://snotes.readthedocs.io/'

# 可选：设置 sitemap 的文件名
# html_extra_path = ['sitemap.xml']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3.8", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
    "pst": ("https://pydata-sphinx-theme.readthedocs.io/en/latest/", None),
}
nitpick_ignore = [
    ("py:class", "docutils.nodes.document"),
    ("py:class", "docutils.parsers.rst.directives.body.Sidebar"),
]

suppress_warnings = ["myst.domains", "ref.ref"]

numfig = True

myst_enable_extensions = [
    "dollarmath",
    "amsmath",
    "deflist",
    # "html_admonition",
    # "html_image",
    "colon_fence",
    # "smartquotes",
    # "replacements",
    # "linkify",
    # "substitution",
]

language = 'zh-cn'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_book_theme'
html_logo = "_static/logo-wide.svg"
html_title = "学习笔记"
html_copy_source = True
html_favicon = "_static/logo-square.svg"
html_last_updated_fmt = ""
html_static_path = ['_static']

html_sidebars = {
    "reference/blog/*": [
        "navbar-logo.html",
        "search-field.html",
        "ablog/postcard.html",
        "ablog/recentposts.html",
        "ablog/tagcloud.html",
        "ablog/categories.html",
        "ablog/archives.html",
        "sbt-sidebar-nav.html",
    ]
}
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = ["custom.css"]
nb_execution_mode = "cache"
thebe_config = {
    "repository_url": "https://github.com/Abner1995/snotes.git",
    "repository_branch": "main",
}

html_theme_options = {
    "path_to_docs": "docs",
    "repository_url": "https://github.com/Abner1995/snotes.git",
    "repository_branch": "main",
    "launch_buttons": {
        "binderhub_url": "https://mybinder.org",
        "colab_url": "https://colab.research.google.com/",
        "deepnote_url": "https://deepnote.com/",
        "notebook_interface": "jupyterlab",
        "thebe": True,
        # "jupyterhub_url": "https://datahub.berkeley.edu",  # For testing
    },
    "use_edit_page_button": True,
    "use_source_button": True,
    "use_issues_button": True,
    # "use_repository_button": True,
    "use_download_button": True,
    "use_sidenotes": True,
    "show_toc_level": 2,
    "announcement": (
        # "⚠️The latest release refactored our HTML, "
        # "so double-check your custom CSS rules!⚠️"
    ),
    "logo": {
        "image_dark": "_static/logo-wide-dark.svg",
        # "text": html_title,  # Uncomment to try text with logo
    },
    "icon_links": [
        {
            "name": "notes",
            "url": "https://snotes.readthedocs.io/zh-cn/latest/",
            "icon": "_static/ebp-logo.png",
            "type": "local",
        },
        {
            "name": "GitHub",
            "url": "https://github.com/Abner1995/snotes.git",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "PyPI",
            "url": "https://github.com/Abner1995/snotes.git",
            "icon": "https://img.shields.io/pypi/dw/sphinx-book-theme",
            "type": "url",
        },
    ],
    # For testing
    # "use_fullscreen_button": False,
    # "home_page_in_toc": True,
    # "extra_footer": "<a href='https://google.com'>Test</a>",  # DEPRECATED KEY
    # "show_navbar_depth": 2,
    # Testing layout areas
    # "navbar_start": ["test.html"],
    # "navbar_center": ["test.html"],
    # "navbar_end": ["test.html"],
    # "navbar_persistent": ["test.html"],
    # "footer_start": ["test.html"],
    # "footer_end": ["test.html"]
}

html_context = {
    "extra_meta": """
        <meta name="description" content="这是全局描述">
        <meta name="keywords" content="sphinx, book theme, meta 标签">
    """
}

# sphinxext.opengraph
ogp_social_cards = {
    "image": "_static/logo-square.png",
}

# -- sphinx-copybutton config -------------------------------------
copybutton_exclude = ".linenos, .gp"

# -- ABlog config -------------------------------------------------
blog_path = "reference/blog"
blog_post_pattern = "reference/blog/*.md"
blog_baseurl = "https://snotes.readthedocs.io"
fontawesome_included = True
post_auto_image = 1
post_auto_excerpt = 2
nb_execution_show_tb = "READTHEDOCS" in os.environ
bibtex_bibfiles = ["references.bib"]
# To test that style looks good with common bibtex config
bibtex_reference_style = "author_year"
bibtex_default_style = "plain"
numpydoc_show_class_members = False  # for automodule:: urllib.parse stub file issue
linkcheck_ignore = [
    "http://someurl/release",  # This is a fake link
    "https://doi.org",  # These don't resolve properly and cause SSL issues
]
linkcheck_exclude_documents = ["changelog"]

# -- Download latest theme elements page from PyData -----------------------------

# path_pydata_content = "https://raw.githubusercontent.com/pydata/pydata-sphinx-theme/main/docs/user_guide/theme-elements.md"  # noqa
# path_content_file = Path(__file__).parent / "content/pydata-content-blocks.md"
# if not path_content_file.exists():
#     with urlopen(path_pydata_content) as resp:
#         # Read in the content page file, then update the title and add context
#         content = resp.read().decode().split("\n")
#         ix_title = content.index("# Theme-specific elements")
#         content[ix_title] = "# PyData Theme Elements"
#         content.insert(
#             ix_title + 1,
#             "\nThis is a collection of content blocks with special support from this theme's parent theme, [the PyData Sphinx Theme](https://pydata-sphinx-theme.readthedocs.io/en/latest/user_guide/theme-elements.html)\n",  # noqa
#         )  # noqa
#         content = "\n".join(content)
#         # Replace a relative link in the pydata docs w/ the respective one here
#         content = content.replace("../examples/pydata.ipynb", "notebooks.md")
#         # Write to disk in a location that will be ignored by git
#         path_content_file.write_text(content)


def setup(app):
    # -- To demonstrate ReadTheDocs switcher -------------------------------------
    # This links a few JS and CSS files that mimic the environment that RTD uses
    # so that we can test RTD-like behavior. We don't need to run it on RTD and we
    # don't wanted it loaded in GitHub Actions because it messes up the lighthouse
    # results.
    if not os.environ.get("READTHEDOCS") and not os.environ.get("GITHUB_ACTIONS"):
        app.add_css_file(
            "https://assets.readthedocs.org/static/css/readthedocs-doc-embed.css"
        )
        app.add_css_file("https://assets.readthedocs.org/static/css/badge_only.css")

        # Create the dummy data file so we can link it
        # ref: https://github.com/readthedocs/readthedocs.org/blob/bc3e147770e5740314a8e8c33fec5d111c850498/readthedocs/core/static-src/core/js/doc-embed/footer.js  # noqa: E501
        app.add_js_file("rtd-data.js")
        app.add_js_file(
            "https://assets.readthedocs.org/static/javascript/readthedocs-doc-embed.js",
            priority=501,
        )
