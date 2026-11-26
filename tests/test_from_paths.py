"""Path sources — ``Loader.from_paths`` opens zarr ``{source_key: path | [paths]}`` backed.

Covers the source-value shapes (single path / list of paths / already-constructed AnnData), the "load only
the reps the streams use" contract (via ``open_source``), that an annbatch collection root is
rejected (unsupported), and that a path-sourced loader streams matched batches end-to-end.
"""

from __future__ import annotations

import warnings

import anndata as ad
import numpy as np
import pandas as pd
import pytest
import scipy.sparse as sp
from annbatch import DatasetCollection
from anndata.acc import A
from scheme_helpers import KEY, perturbation_obs, uniform, write_zarr

from boundannbatch import Loader, Stream, obs_columns

LINES = ("A", "B")
DRUGS = ("control", "d1", "d2")
COLS = ("cell_line", "drug")
READ = {"sampler": {"batch_size": 16, "chunk_size": 16, "preload_nchunks": 1}, "to": None}


def _adata(n_per_combo: int = 16, seed: int = 0) -> ad.AnnData:
    """Sparse X + an obsm rep + a layer + an unreferenced obs column (open must load only what's used)."""
    rng = np.random.default_rng(seed)
    obs = perturbation_obs(LINES, DRUGS, n_per_combo)
    obs["extra"] = "unused"  # an obs column no stream references — must not be required
    a = ad.AnnData(X=sp.csr_matrix(rng.random((len(obs), 5), dtype="float32")), obs=obs)
    a.obsm["emb"] = rng.random((len(obs), 3), dtype="float32")
    a.layers["log1p"] = sp.csr_matrix(rng.random((len(obs), 5), dtype="float32"))
    return a


def _streams():
    combos = {(cl, dr) for cl in LINES for dr in DRUGS}
    pert = uniform([c for c in combos if c[1] != "control"])
    ctrl = uniform([c for c in combos if c[1] == "control"])
    return (
        Stream(KEY, group_by=COLS, reps=A.X, weights=pert),
        {"ctrl": Stream(KEY, group_by=COLS, reps=(A.X, A.obsm["emb"]), match_on=("cell_line",), weights=ctrl)},
    )


def _loader(path_value):
    primary, links = _streams()
    return Loader.from_paths({KEY: path_value}, primary=primary, links=links, seed=0, **READ)


# ── open_source on a zarr path: only the requested reps/cols are materialized ───────────────────
def test_obs_columns_stacks_files_with_the_union_of_categories():
    a = ad.AnnData(obs=pd.DataFrame({"c": pd.Categorical(["x", "x"])}, index=["0", "1"]))
    b = ad.AnnData(obs=pd.DataFrame({"c": pd.Categorical(["y"])}, index=["0"]))
    obs = obs_columns([a, b], ["c"])
    assert list(obs.index) == [0, 1, 2] and list(obs["c"]) == ["x", "x", "y"]
    assert set(obs["c"].cat.categories) == {"x", "y"}
    assert list(a.obs["c"].cat.categories) == ["x"]  # the caller's obs is untouched


# ── Loader.from_paths: source-value shapes ─────────────────────────────────────────────────────
def test_single_path_source_opened_backed_and_streams(tmp_path):
    p = write_zarr(_adata(), tmp_path / "a.zarr")
    loader = _loader(p)
    a = loader._sources[KEY].adatas[0]
    assert isinstance(a.X, ad.abc.CSRDataset)  # backed, not in-memory
    assert list(a.obsm) == ["emb"]  # only the reps the streams use (union: A.X + A.obsm["emb"])
    assert "log1p" not in a.layers
    b = next(iter(loader))
    assert b["primary"][A.X].shape == (16, 5)
    assert b["ctrl"][A.X].shape == (16, 5)  # matched control rows
    assert b["ctrl"][A.obsm["emb"]].shape == (16, 3)  # aligned obsm rep of the same cells


def test_list_of_paths_source_streams(tmp_path):
    paths = [write_zarr(_adata(seed=i), tmp_path / f"a{i}.zarr") for i in range(2)]
    loader = _loader(paths)
    adatas = loader._sources[KEY].adatas
    assert len(adatas) == 2 and all(isinstance(a, ad.AnnData) for a in adatas)
    assert next(iter(loader))["primary"][A.X].shape == (16, 5)


def test_in_memory_source_passes_through():
    # an already-constructed container is returned unchanged (not re-opened)
    from boundannbatch._io import open_source

    adata = _adata()
    assert open_source(adata, A.X, *(A.obs[c] for c in COLS)) is adata


def test_layers_rep_streams_the_layer(tmp_path):
    adata = _adata()
    p = write_zarr(adata, tmp_path / "a.zarr")
    stream = Stream(KEY, group_by=COLS, reps=A.layers["log1p"])
    loader = Loader.from_paths({KEY: p}, primary=stream, seed=0, **READ)
    b = next(iter(loader))
    assert list(b["primary"]) == [A.layers["log1p"]]  # keyed by the reference
    np.testing.assert_allclose(
        b["primary"][A.layers["log1p"]].toarray(), adata.layers["log1p"][b["rows"]["primary"]].toarray()
    )


def test_collection_root_is_unsupported(tmp_path):
    ap = write_zarr(_adata(), tmp_path / "a.zarr")
    cp = str(tmp_path / "coll.zarr")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        DatasetCollection(cp, mode="a").add_adatas([ap], groupby=list(COLS), shuffle=False)
    with pytest.raises(NotImplementedError, match="DatasetCollection"):
        _loader(cp)
    with pytest.raises(NotImplementedError, match="DatasetCollection"):  # also inside a list of paths
        _loader([ap, cp])


def test_h5ad_source_streams_sparse_x_in_memory(tmp_path):
    adata = _adata()
    p = tmp_path / "a.h5ad"
    adata.write_h5ad(p)
    loader = _loader(p)
    a = loader._sources[KEY].adatas[0]
    assert sp.issparse(a.X) and not isinstance(a.X, ad.abc.CSRDataset)  # in memory: h5ad is never backed
    b = next(iter(loader))
    rows = b["rows"]["primary"]
    np.testing.assert_allclose(b["primary"][A.X].toarray(), adata.X[rows].toarray())
    assert b["ctrl"][A.obsm["emb"]].shape == (16, 3)


def test_a_source_mixing_zarr_and_h5ad_is_refused(tmp_path):
    zarr_path = write_zarr(_adata(seed=0), tmp_path / "a.zarr")
    h5ad_path = tmp_path / "b.h5ad"
    _adata(seed=1).write_h5ad(h5ad_path)
    with pytest.raises(ValueError, match="on disk in some of this source's files"):
        next(iter(_loader([zarr_path, h5ad_path])))
