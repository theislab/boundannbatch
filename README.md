# boundannbatch

[![Tests][badge-tests]][tests]
[![Documentation][badge-docs]][documentation]

[badge-tests]: https://img.shields.io/github/actions/workflow/status/theislab/boundannbatch/test.yaml?branch=main
[badge-docs]: https://app.readthedocs.org/projects/boundannbatch/badge/

Declarative multi-source streaming over annbatch: matched batches across AnnData sources, keyed by `anndata.acc` references.

boundannbatch is meant to stay thin. Whatever annbatch (or anndata) can take over upstream should move there, and what
remains should be small hooks on top of annbatch's `Loader` and samplers. Ideally this package goes away.

## Getting started

Please refer to the [documentation][],
in particular, the [API documentation][].

## Installation

You need to have Python 3.12 or newer installed on your system.
If you don't have Python installed, we recommend installing [uv][].

We recommend managing dependencies in project-specific virtual environments to avoid dependency conflicts.
This is most convenient using package managers such as [uv][].
Choose from the options below to install boundannbatch:

<!--
1. Add the latest release of `boundannbatch` from [PyPI][] to your `uv` project:

   ```bash
   uv add boundannbatch
   ```

1. Install the latest release into a [standard virtual environment][venv]:

   ```bash
   (after activating your venv)
   pip install boundannbatch
   ```

-->

1. Install the latest development version:

   ```bash
   pip install git+https://github.com/theislab/boundannbatch.git  # (or `uv add`)
   ```

## Release notes

See the [changelog][].

## Contact

For questions and help requests, you can reach out in the [scverse discourse][].
If you found a bug, please use the [issue tracker][].

## Citation

> t.b.a

[uv]: https://github.com/astral-sh/uv
[scverse discourse]: https://discourse.scverse.org/
[issue tracker]: https://github.com/theislab/boundannbatch/issues
[tests]: https://github.com/theislab/boundannbatch/actions/workflows/test.yaml
[documentation]: https://boundannbatch.readthedocs.io
[changelog]: https://boundannbatch.readthedocs.io/page/changelog.html
[api documentation]: https://boundannbatch.readthedocs.io/page/api.html
[pypi]: https://pypi.org/project/boundannbatch
[venv]: https://docs.python.org/3/tutorial/venv.html
