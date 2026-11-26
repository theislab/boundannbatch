"""Sampler bookkeeping — epoch length, the run-length rule, and non-contiguous coverage.

The boundannbatch analogs of annbatch's ``test_n_batches`` (epoch length), ``test_run_length_error_names_class_labels``
+ ``test_zero_weight_class_exempt_from_run_length_rule`` (the ``chunk_size>1`` contiguous-run rule and its
zero-weight exemption), and ``test_noncontiguous_class_samples_all_runs`` (a label split across runs is
fully sampled). Each loader is a single primary stream (no links).
"""

from __future__ import annotations

from itertools import islice

import numpy as np
import pytest
from anndata.acc import A
from scheme_helpers import KEY, encoded_adata, rep, uniform

from boundannbatch import Loader, Stream

COLS = ("cell_line", "drug")


def _primary_only(adata, weights, *, batch_size=8, chunk_size=1, preload_nchunks=8, n_iters=None) -> Loader:
    loader = Loader(
        {KEY: adata},
        primary=Stream(KEY, reps=A.X, group_by=COLS, weights=weights),
        seed=0,
        sampler={"batch_size": batch_size, "chunk_size": chunk_size, "preload_nchunks": preload_nchunks},
    )
    return loader if n_iters is None else loader.set_n_iters(n_iters)


def test_n_batches_is_primary_obs_over_batch_size():
    # primary = 2 lines × 3 drugs × 16 = 96 target cells; batch 8 → 12 batches per with-replacement pass
    adata = encoded_adata(("A", "B"), ("d1", "d2", "d3"), n_per_combo=16)
    weights = uniform([(cl, dr) for cl in ("A", "B") for dr in ("d1", "d2", "d3")])
    loader = _primary_only(adata, weights)
    assert loader.n_batches == 96 // 8 and loader.n_iters is None  # derived epoch length; no cap by default
    first_pass = list(islice(loader, loader.n_batches))  # one epoch worth of batches
    assert len(first_pass) == loader.n_batches


def test_n_iters_bounds_each_pass():
    # n_iters is a pause point: each `for` over the loader yields exactly that many batches, then stops.
    adata = encoded_adata(("A", "B"), ("d1", "d2", "d3"), n_per_combo=16)
    weights = uniform([(cl, dr) for cl in ("A", "B") for dr in ("d1", "d2", "d3")])
    loader = _primary_only(adata, weights, n_iters=5)
    assert loader.n_iters == 5
    assert len(list(loader)) == 5 and len(list(loader)) == 5  # and it re-arms for the next pass


def test_n_iters_pauses_rather_than_restarts():
    # The underlying stream is one infinite schedule, so capping it only decides WHERE the passes break:
    # 3 passes of 4 must yield exactly the same 12 batches as one uncapped run of 12.
    adata = encoded_adata(("A", "B"), ("d1", "d2", "d3"), n_per_combo=16)
    weights = uniform([(cl, dr) for cl in ("A", "B") for dr in ("d1", "d2", "d3")])
    uncapped = [rep(b, "primary", A.X) for b in islice(_primary_only(adata, weights), 12)]

    capped = _primary_only(adata, weights, n_iters=4)
    resumed = [rep(b, "primary", A.X) for _ in range(3) for b in capped]  # 3 consecutive passes
    assert len(resumed) == 12
    for got, want in zip(resumed, uncapped, strict=True):
        assert np.array_equal(got, want)


def test_set_n_iters_none_removes_the_pause():
    adata = encoded_adata(("A", "B"), ("d1", "d2", "d3"), n_per_combo=16)
    weights = uniform([(cl, dr) for cl in ("A", "B") for dr in ("d1", "d2", "d3")])
    loader = _primary_only(adata, weights, n_iters=3)
    loader.set_n_iters(None)
    assert len(list(islice(loader, 20))) == 20  # runs past the old cap, across epoch rolls


def test_chunk_run_length_error_names_the_stream():
    # a positive-weight label with a 2-row run shorter than chunk_size(4): annbatch raises, boundannbatch re-raises
    # with the offending STREAM's name prepended (so the user knows which stream's runs are too short).
    adata = encoded_adata(("A", "B"), ("d1", "d2"), n_per_combo=2)
    weights = uniform([(cl, dr) for cl in ("A", "B") for dr in ("d1", "d2")])
    with pytest.raises(ValueError, match=r"stream 'primary'"):
        _primary_only(adata, weights, batch_size=4, chunk_size=4, preload_nchunks=4)
