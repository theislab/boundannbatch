# boundannbatch

[![Tests][badge-tests]][tests]
[![Documentation][badge-docs]][documentation]

[badge-tests]: https://img.shields.io/github/actions/workflow/status/theislab/boundannbatch/test.yaml?branch=main
[badge-docs]: https://app.readthedocs.org/projects/boundannbatch/badge/

Declarative multi-source streaming over annbatch: matched batches across AnnData sources, keyed by `anndata.acc` references.

boundannbatch is meant to stay thin. Whatever annbatch (or anndata) can take over upstream should move there, and what
remains should be small hooks on top of annbatch's `Loader` and samplers. Ideally this package goes away.

```bash
pip install boundannbatch
```

See the [API documentation][] and the [changelog][]. Bugs go to the [issue tracker][].

[issue tracker]: https://github.com/theislab/boundannbatch/issues
[tests]: https://github.com/theislab/boundannbatch/actions/workflows/test.yaml
[documentation]: https://boundannbatch.readthedocs.io
[changelog]: https://boundannbatch.readthedocs.io/page/changelog.html
[api documentation]: https://boundannbatch.readthedocs.io/page/api.html
