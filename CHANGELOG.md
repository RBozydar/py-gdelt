# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.6](https://github.com/RBozydar/py-gdelt/compare/gdelt-py-v0.1.5...gdelt-py-v0.1.6) (2026-01-25)


### Features

* add file-based dataset endpoints (VGKG, TV-GKG, TV NGrams, Radio NGrams) ([#61](https://github.com/RBozydar/py-gdelt/issues/61)) ([162de20](https://github.com/RBozydar/py-gdelt/commit/162de20340c2ea7cdcba2720136a59bc0304b9c7))
* **endpoints:** add LowerThird, TVV, and GKG GeoJSON API endpoints ([#65](https://github.com/RBozydar/py-gdelt/issues/65)) ([d2d529a](https://github.com/RBozydar/py-gdelt/commit/d2d529adbd64f6448ae82812c21fe274701c1ed6))
* **graphs:** add GDELT Graph Datasets support (GQG, GEG, GFG, GGG, GEMG, GAL) ([#66](https://github.com/RBozydar/py-gdelt/issues/66)) ([c6398f0](https://github.com/RBozydar/py-gdelt/commit/c6398f06df19de06f9fadce016a9689383d9d334))
* **lookups:** add 4 new lookup tables + expand GKG themes to 59K entries ([#62](https://github.com/RBozydar/py-gdelt/issues/62)) ([2bbe3c8](https://github.com/RBozydar/py-gdelt/commit/2bbe3c8e8ebee851fe2184f97a1251eb8193058c))
* **lookups:** enrich CAMEO codes with examples and usage notes ([#70](https://github.com/RBozydar/py-gdelt/issues/70)) ([09289ff](https://github.com/RBozydar/py-gdelt/commit/09289ff5ccbe42c2914b57cd0f641ea0f0552bd1))
* **mcp:** add MCP server with streaming aggregation for geopolitical research ([#50](https://github.com/RBozydar/py-gdelt/issues/50)) ([b8d5a31](https://github.com/RBozydar/py-gdelt/commit/b8d5a3156daccd369c4907555df5ce0d3f7b50b9))


### Bug Fixes

* Claude workflow max-turns and continue-on-error ([#56](https://github.com/RBozydar/py-gdelt/issues/56)) ([27f4199](https://github.com/RBozydar/py-gdelt/commit/27f41993424ea95a5dcba270c8f4bb7bf96cdba4))
* **filters:** remove arbitrary date range limits for file-based datasets ([519a320](https://github.com/RBozydar/py-gdelt/commit/519a3200b3f93e78819ca79e4f11b12c4e8a3ed3))
* resolve weekly integration test failures ([#69](https://github.com/RBozydar/py-gdelt/issues/69)) ([02b3a23](https://github.com/RBozydar/py-gdelt/commit/02b3a2387b387ec942f454c297e2c14c569c8ec9))

## [0.1.5](https://github.com/RBozydar/py-gdelt/compare/gdelt-py-v0.1.4...gdelt-py-v0.1.5) (2026-01-12)


### Features

* add BigQuery integration tests ([ad7c100](https://github.com/RBozydar/py-gdelt/commit/ad7c100473c7e13d9dbf0512361b6b1af26bbee0))
* add py-gdelt core library with GDELT API support ([020018d](https://github.com/RBozydar/py-gdelt/commit/020018d84a76b0e85e9349249f8ca598a240e7c6))
* add py-gdelt core library with GDELT API support ([ee5cc66](https://github.com/RBozydar/py-gdelt/commit/ee5cc66d4ece78866a9d23b5a6d38816e170f4be))
* add schema drift detection integration tests ([1411cd2](https://github.com/RBozydar/py-gdelt/commit/1411cd2fa5d3e9f9a9ef366aeb4e2755054be395))
* comprehensive integration tests and API bug fixes ([945ab11](https://github.com/RBozydar/py-gdelt/commit/945ab117b8ad7af4206dbc2eae125065a343f4c6))
* enforce conventional commits with full automation ([b7a87e7](https://github.com/RBozydar/py-gdelt/commit/b7a87e7f905664ce95e4a3f72f882b1556348ebe))
* enforce conventional commits with full automation ([d4597f0](https://github.com/RBozydar/py-gdelt/commit/d4597f085bd17a7c5fb5a38bf73ecff85a494944))
* merge v1-core with tests, CI, and docs into main ([b8c2125](https://github.com/RBozydar/py-gdelt/commit/b8c2125f84f6b52df6e12b2a664484a07ea12faf))
* setup CI/CD with PyPI publishing and documentation coverage ([1aaf18c](https://github.com/RBozydar/py-gdelt/commit/1aaf18c8a1d8bf6b89f7844ebec839a7c6e8aef5))
* setup CI/CD with PyPI publishing and documentation coverage ([02e6c05](https://github.com/RBozydar/py-gdelt/commit/02e6c05a9e446055a901d8f63b1943f187f4db77))


### Bug Fixes

* add pyright support and fix type compatibility issues ([8a0f26b](https://github.com/RBozydar/py-gdelt/commit/8a0f26b9177fcae918db960d202306876748670d))
* add pyright support and fix type compatibility issues ([ef7fb44](https://github.com/RBozydar/py-gdelt/commit/ef7fb44dcaf2d3026fd467ebbe8e70a432856e31))
* add workflow exit step and timeline parsing logging ([c9fbd36](https://github.com/RBozydar/py-gdelt/commit/c9fbd36abe6f18ea12855bfbc33a2d5b07f5087e))
* address PR review comments for bug fixes and example corrections ([#27](https://github.com/RBozydar/py-gdelt/issues/27)) ([0e94124](https://github.com/RBozydar/py-gdelt/commit/0e9412460472725a739a1612d35220dab39aaefb))
* configure uv build-backend module-name for gdelt-py ([3b05a9b](https://github.com/RBozydar/py-gdelt/commit/3b05a9b04199a554964c44cb0d9b93235de3ff97))
* correct API parameters and types for GEO, Context, TV, and BigQuery ([2a7fe0b](https://github.com/RBozydar/py-gdelt/commit/2a7fe0b9bf2da3f7077718e38be80b87b2e7e7a8))
* correct DOC API timeline mode to use 'timelinevol' ([76cb844](https://github.com/RBozydar/py-gdelt/commit/76cb84417e6ff7f20e69422f5404fc4ea9b735ca))
* correct integration test assertions and skip broken API tests ([9a8511f](https://github.com/RBozydar/py-gdelt/commit/9a8511f9e43d64bea94ae3aa907881cc4958660b))
* extract version from pyproject.toml for release notes ([877225a](https://github.com/RBozydar/py-gdelt/commit/877225ad48fb1c4bc9a55eee9430d4e0e0e7951f))
* install docs dependencies from pyproject.toml extras ([edc77f6](https://github.com/RBozydar/py-gdelt/commit/edc77f6bfcdad28fa5db9470af34dbedfc58af56))
* remove non-existent docstr-coverage GitHub Action ([2e3ffcc](https://github.com/RBozydar/py-gdelt/commit/2e3ffccb3795c66be5a1725a0d3096412bfcc35b))
* remove non-existent docstr-coverage GitHub Action ([8563262](https://github.com/RBozydar/py-gdelt/commit/85632625a5194acfb80463048110091089c4079a))
* remove unused type ignore for pandas import ([3437d53](https://github.com/RBozydar/py-gdelt/commit/3437d53ac7a73e40b75d6d92e8294977019e0974))
* rename package to gdelt-py for PyPI and bump to 0.1.1 ([#28](https://github.com/RBozydar/py-gdelt/issues/28)) ([1cb654d](https://github.com/RBozydar/py-gdelt/commit/1cb654d29397a9119eb608e1b26f277812b8f466))
* update publish workflow, README, and docs for gdelt-py ([#29](https://github.com/RBozydar/py-gdelt/issues/29)) ([00062cd](https://github.com/RBozydar/py-gdelt/commit/00062cdfd6dd0eae046ba4ef4a270980dd48dacf))
* update urllib3 to 2.6.3 to fix CVE-2026-21441 ([2c5736d](https://github.com/RBozydar/py-gdelt/commit/2c5736d5fd30e2a979c276deac25a3f3a49163cd))
* use HTTP for data.gdeltproject.org (SSL cert mismatch) ([9c7c0d8](https://github.com/RBozydar/py-gdelt/commit/9c7c0d8b29fd35680a2a3466babec38e77086301))


### Documentation

* add data sources matrix and architecture documentation ([0186185](https://github.com/RBozydar/py-gdelt/commit/01861850741e125188f5e1afdc6c992c5f4fc7d8))
* add data sources matrix and architecture documentation ([#33](https://github.com/RBozydar/py-gdelt/issues/33)) ([d8b91b5](https://github.com/RBozydar/py-gdelt/commit/d8b91b596014dfec87cb35c93f08e207041dcaae))
* add data sources matrix and architecture documentation ([#37](https://github.com/RBozydar/py-gdelt/issues/37)) ([6cb731c](https://github.com/RBozydar/py-gdelt/commit/6cb731cbc8c1b4b8056ff8789cce9b46feb6c227))
* add GDELT reference documentation (CAMEO, GKG themes) ([8c76e49](https://github.com/RBozydar/py-gdelt/commit/8c76e4926cdc3152a87b4a8c17eaf8aa3ef30c3b))
* add GDELT reference documentation (CAMEO, GKG themes) ([a134e4b](https://github.com/RBozydar/py-gdelt/commit/a134e4baff46c9b3d0ec590ba4abc956ed28db13))
* add llms.txt plugin and fix API documentation coverage ([#32](https://github.com/RBozydar/py-gdelt/issues/32)) ([10e6e72](https://github.com/RBozydar/py-gdelt/commit/10e6e720b2ad9b6342ca562c1ea4a945e39e7d17))
* add plan for schema drift detection integration tests ([cec7b1d](https://github.com/RBozydar/py-gdelt/commit/cec7b1dc563f89c132d9a4bfa8e00e5156bde846))
* add user documentation, examples, and Jupyter notebooks ([84c81a8](https://github.com/RBozydar/py-gdelt/commit/84c81a861ca8602782f1397978d87c52f65981f2))
* add user documentation, examples, and notebooks ([de89814](https://github.com/RBozydar/py-gdelt/commit/de89814fec77996f810692a784d68e9dcf766a0b))
* fix models.md to reference actual exported classes ([#24](https://github.com/RBozydar/py-gdelt/issues/24)) ([8f55592](https://github.com/RBozydar/py-gdelt/commit/8f555925d6f60cbff30ff0f8658ad77456078c08))
* move plan file to dev branch ([b330c0f](https://github.com/RBozydar/py-gdelt/commit/b330c0f257ab58953fc3f018a13cd2f071dd78d0))

## [0.1.4](https://github.com/RBozydar/py-gdelt/compare/gdelt-py-v0.1.3...gdelt-py-v0.1.4) (2026-01-08)


### Features

* add BigQuery integration tests ([ad7c100](https://github.com/RBozydar/py-gdelt/commit/ad7c100473c7e13d9dbf0512361b6b1af26bbee0))
* add py-gdelt core library with GDELT API support ([020018d](https://github.com/RBozydar/py-gdelt/commit/020018d84a76b0e85e9349249f8ca598a240e7c6))
* add py-gdelt core library with GDELT API support ([ee5cc66](https://github.com/RBozydar/py-gdelt/commit/ee5cc66d4ece78866a9d23b5a6d38816e170f4be))
* add schema drift detection integration tests ([1411cd2](https://github.com/RBozydar/py-gdelt/commit/1411cd2fa5d3e9f9a9ef366aeb4e2755054be395))
* comprehensive integration tests and API bug fixes ([945ab11](https://github.com/RBozydar/py-gdelt/commit/945ab117b8ad7af4206dbc2eae125065a343f4c6))
* enforce conventional commits with full automation ([b7a87e7](https://github.com/RBozydar/py-gdelt/commit/b7a87e7f905664ce95e4a3f72f882b1556348ebe))
* enforce conventional commits with full automation ([d4597f0](https://github.com/RBozydar/py-gdelt/commit/d4597f085bd17a7c5fb5a38bf73ecff85a494944))
* merge v1-core with tests, CI, and docs into main ([b8c2125](https://github.com/RBozydar/py-gdelt/commit/b8c2125f84f6b52df6e12b2a664484a07ea12faf))
* setup CI/CD with PyPI publishing and documentation coverage ([1aaf18c](https://github.com/RBozydar/py-gdelt/commit/1aaf18c8a1d8bf6b89f7844ebec839a7c6e8aef5))
* setup CI/CD with PyPI publishing and documentation coverage ([02e6c05](https://github.com/RBozydar/py-gdelt/commit/02e6c05a9e446055a901d8f63b1943f187f4db77))


### Bug Fixes

* add workflow exit step and timeline parsing logging ([c9fbd36](https://github.com/RBozydar/py-gdelt/commit/c9fbd36abe6f18ea12855bfbc33a2d5b07f5087e))
* address PR review comments for bug fixes and example corrections ([#27](https://github.com/RBozydar/py-gdelt/issues/27)) ([0e94124](https://github.com/RBozydar/py-gdelt/commit/0e9412460472725a739a1612d35220dab39aaefb))
* configure uv build-backend module-name for gdelt-py ([3b05a9b](https://github.com/RBozydar/py-gdelt/commit/3b05a9b04199a554964c44cb0d9b93235de3ff97))
* correct API parameters and types for GEO, Context, TV, and BigQuery ([2a7fe0b](https://github.com/RBozydar/py-gdelt/commit/2a7fe0b9bf2da3f7077718e38be80b87b2e7e7a8))
* correct DOC API timeline mode to use 'timelinevol' ([76cb844](https://github.com/RBozydar/py-gdelt/commit/76cb84417e6ff7f20e69422f5404fc4ea9b735ca))
* correct integration test assertions and skip broken API tests ([9a8511f](https://github.com/RBozydar/py-gdelt/commit/9a8511f9e43d64bea94ae3aa907881cc4958660b))
* extract version from pyproject.toml for release notes ([877225a](https://github.com/RBozydar/py-gdelt/commit/877225ad48fb1c4bc9a55eee9430d4e0e0e7951f))
* remove non-existent docstr-coverage GitHub Action ([2e3ffcc](https://github.com/RBozydar/py-gdelt/commit/2e3ffccb3795c66be5a1725a0d3096412bfcc35b))
* remove non-existent docstr-coverage GitHub Action ([8563262](https://github.com/RBozydar/py-gdelt/commit/85632625a5194acfb80463048110091089c4079a))
* remove unused type ignore for pandas import ([3437d53](https://github.com/RBozydar/py-gdelt/commit/3437d53ac7a73e40b75d6d92e8294977019e0974))
* rename package to gdelt-py for PyPI and bump to 0.1.1 ([#28](https://github.com/RBozydar/py-gdelt/issues/28)) ([1cb654d](https://github.com/RBozydar/py-gdelt/commit/1cb654d29397a9119eb608e1b26f277812b8f466))
* update publish workflow, README, and docs for gdelt-py ([#29](https://github.com/RBozydar/py-gdelt/issues/29)) ([00062cd](https://github.com/RBozydar/py-gdelt/commit/00062cdfd6dd0eae046ba4ef4a270980dd48dacf))
* update urllib3 to 2.6.3 to fix CVE-2026-21441 ([2c5736d](https://github.com/RBozydar/py-gdelt/commit/2c5736d5fd30e2a979c276deac25a3f3a49163cd))
* use HTTP for data.gdeltproject.org (SSL cert mismatch) ([9c7c0d8](https://github.com/RBozydar/py-gdelt/commit/9c7c0d8b29fd35680a2a3466babec38e77086301))


### Documentation

* add data sources matrix and architecture documentation ([#33](https://github.com/RBozydar/py-gdelt/issues/33)) ([d8b91b5](https://github.com/RBozydar/py-gdelt/commit/d8b91b596014dfec87cb35c93f08e207041dcaae))
* add data sources matrix and architecture documentation ([#37](https://github.com/RBozydar/py-gdelt/issues/37)) ([6cb731c](https://github.com/RBozydar/py-gdelt/commit/6cb731cbc8c1b4b8056ff8789cce9b46feb6c227))
* add GDELT reference documentation (CAMEO, GKG themes) ([8c76e49](https://github.com/RBozydar/py-gdelt/commit/8c76e4926cdc3152a87b4a8c17eaf8aa3ef30c3b))
* add GDELT reference documentation (CAMEO, GKG themes) ([a134e4b](https://github.com/RBozydar/py-gdelt/commit/a134e4baff46c9b3d0ec590ba4abc956ed28db13))
* add llms.txt plugin and fix API documentation coverage ([#32](https://github.com/RBozydar/py-gdelt/issues/32)) ([10e6e72](https://github.com/RBozydar/py-gdelt/commit/10e6e720b2ad9b6342ca562c1ea4a945e39e7d17))
* add plan for schema drift detection integration tests ([cec7b1d](https://github.com/RBozydar/py-gdelt/commit/cec7b1dc563f89c132d9a4bfa8e00e5156bde846))
* add user documentation, examples, and Jupyter notebooks ([84c81a8](https://github.com/RBozydar/py-gdelt/commit/84c81a861ca8602782f1397978d87c52f65981f2))
* add user documentation, examples, and notebooks ([de89814](https://github.com/RBozydar/py-gdelt/commit/de89814fec77996f810692a784d68e9dcf766a0b))
* fix models.md to reference actual exported classes ([#24](https://github.com/RBozydar/py-gdelt/issues/24)) ([8f55592](https://github.com/RBozydar/py-gdelt/commit/8f555925d6f60cbff30ff0f8658ad77456078c08))
* move plan file to dev branch ([b330c0f](https://github.com/RBozydar/py-gdelt/commit/b330c0f257ab58953fc3f018a13cd2f071dd78d0))

## [0.1.3](https://github.com/RBozydar/py-gdelt/releases/tag/0.1.3) (2026-01-07)

### Bug Fixes

* configure uv build-backend module-name for gdelt-py
* rename package to gdelt-py for PyPI

## [0.1.0](https://github.com/RBozydar/py-gdelt/releases/tag/0.1.0) (2026-01-06)

### Features

* Initial release of gdelt-py
* Unified interface for GDELT APIs
* Async-first design with Pydantic models
* Support for Events, Mentions, GKG, and NGrams
* REST API clients for DOC, GEO, Context, TV, and TVAI
* Comprehensive lookup tables (CAMEO, Themes, Countries)
