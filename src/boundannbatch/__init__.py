"""Declarative, index-free class-mapping data loading over annbatch.

Everything is a :class:`Stream` — one streamed population over a source. :class:`Loader` yields stochastic
matched batches for training and :class:`EvalLoader` a deterministic full-coverage pass; both key their
output by stream name, then by the stream's :mod:`anndata.acc` references (``A.X``, ``A.layers[k]``,
``A.obsm[k]``).
"""

from boundannbatch._eval import EvalLoader
from boundannbatch._io import obs_columns, open_adata, open_source
from boundannbatch._loader import Loader
from boundannbatch._schema import SamplerParams, Stream

__all__ = [
    "EvalLoader",
    "Loader",
    "SamplerParams",
    "Stream",
    "obs_columns",
    "open_adata",
    "open_source",
]
