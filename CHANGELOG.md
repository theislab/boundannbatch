# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog][],
and this project adheres to [Semantic Versioning][].

[keep a changelog]: https://keepachangelog.com/
[semantic versioning]: https://semver.org/

## [Unreleased]

## [0.2.0] - 2026-11-26

### Changed

- `SamplerParams` is a frozen dataclass instead of a pydantic model; a bad value raises `ValueError`, an unknown key `TypeError`
- `EvalLoader(subsample=...)` takes `"head"` or `"random"`; the callable form is removed
- An annbatch `DatasetCollection` is no longer accepted as a source value (it never streamed)
- Dependencies: `zarrs` comes through `annbatch[zarrs]`; `scipy` is test-only

## [0.1.0] - 2026-11-25

### Changed

- Split out of `scfit.data` (scfit 0.0.14) into its own package: `from scfit.data import Loader` is now `from boundannbatch import Loader`. Earlier history is in [scfit's changelog](https://github.com/theislab/modelbinder/blob/v0.0.14/CHANGELOG.md)
- torch is optional (`pip install boundannbatch[torch]`), needed only for `EvalLoader(to="torch")`
