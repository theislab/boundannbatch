# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog][],
and this project adheres to [Semantic Versioning][].

[keep a changelog]: https://keepachangelog.com/
[semantic versioning]: https://semver.org/

## [Unreleased]

### Changed

- Split out of `scfit.data` (scfit 0.0.14) into its own package: `from scfit.data import Loader` is now `from boundannbatch import Loader`. Earlier history is in [scfit's changelog](https://github.com/theislab/modelbinder/blob/v0.0.14/CHANGELOG.md)
- torch is optional (`pip install boundannbatch[torch]`), needed only for `EvalLoader(to="torch")`
