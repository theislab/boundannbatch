from datetime import datetime
from importlib.metadata import metadata

info = metadata("boundannbatch")
project = info["Name"]
author = info["Author"]
copyright = f"{datetime.now():%Y}, {author}."
version = release = info["Version"]
repository_url = dict(pu.split(", ") for pu in info.get_all("Project-URL"))["Source"]

nitpicky = True
html_context = {
    "display_github": True,
    "github_user": "theislab",
    "github_repo": project,
    "github_version": "main",
    "conf_py_path": "/docs/",
}

extensions = [
    "myst_parser",
    "sphinx_copybutton",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "scverse_misc.sphinx_ext",
]

autodoc_member_order = "groupwise"
default_role = "literal"
napoleon_google_docstring = False
napoleon_include_init_with_doc = False
napoleon_use_rtype = True
napoleon_use_param = True
myst_heading_anchors = 6
myst_enable_extensions = ["colon_fence", "deflist"]
typehints_defaults = "braces"
always_use_bars_union = True

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "anndata": ("https://anndata.scverse.org/en/latest/", None),
    "annbatch": ("https://annbatch.readthedocs.io/en/latest/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "torch": ("https://docs.pytorch.org/docs/stable/", None),
    "zarr": ("https://zarr.readthedocs.io/en/stable/", None),
}
exclude_patterns = ["_build", ".DS_Store"]

html_theme = "sphinx_book_theme"
html_title = project
html_theme_options = {
    "repository_url": repository_url,
    "use_repository_button": True,
    "path_to_docs": "docs/",
    "navigation_with_keys": False,
}
