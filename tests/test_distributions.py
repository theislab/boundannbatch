"""A linked stream's label distribution is weight-controlled *within* the matched context
(``P(link extra cols | match_on)``). Fixed ``seed`` → reproducible, so ``atol`` is a safe band.
"""

from __future__ import annotations

from collections import Counter
from itertools import islice

from anndata.acc import A
from scheme_helpers import KEY, encoded_adata, only_leaf, rep, uniform

from boundannbatch import Loader, Stream

COLS = ("cell_line", "drug")
READ = {"sampler": {"batch_size": 8, "chunk_size": 1, "preload_nchunks": 8}}


def test_link_label_follows_weights_within_context():
    # the link matches on cell_line but partitions on (cell_line, drug): within line A the source drug must
    # be drawn 3:1 — i.e. P(drug | cell_line) is weight-controlled (the BoundClassSampler select + project).
    adata = encoded_adata(("A", "B"), ("d1", "d2"), n_per_combo=64)
    loader = Loader(
        {KEY: adata},
        primary=Stream(
            KEY, reps=A.X, group_by=COLS, weights=uniform([("A", "d1"), ("A", "d2"), ("B", "d1"), ("B", "d2")])
        ),
        links={
            "src": Stream(
                KEY,
                reps=A.X,
                group_by=COLS,
                match_on=("cell_line",),
                weights={("A", "d1"): 3, ("A", "d2"): 1, ("B", "d1"): 1, ("B", "d2"): 1},
            )
        },
        **READ,
        seed=0,
    )
    drug_when_a = Counter(
        only_leaf(rep(b, "src", A.X))[1]  # the source drug code...
        for b in islice(loader, 6000)
        if only_leaf(rep(b, "primary", A.X))[0] == 0  # ...on batches whose primary is line A (code 0)
    )
    total = sum(drug_when_a.values())
    assert total > 0, "no line-A batches drawn"
    assert abs(drug_when_a[0] / total - 0.75) < 0.03  # d1 ≈ 75% within line A
