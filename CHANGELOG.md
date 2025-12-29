# Changelog

All notable changes to this project will be documented in this file.

## [1.0.1] - 2025-12-29

### Added
- `--min-score-ratio` option in `kofamscan_parser.py` for quality filtering (skip hits where score/threshold ratio is below the specified value)
- `--gene` option in `kofamscan_parser.py` for outputting KO numbers with gene details (threshold, score, E-value, mark)


## [1.0.0] - 2025-08/20

### Added
- Initial release
- `kofamscan_parser.py`: Parse KofamScan results and extract KO numbers
- `predict_pathways.py`: Predict pathways from KO list
