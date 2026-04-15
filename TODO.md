# TODO

## [x] Fix "Conversion produced no content" error for >30 channels
- [x] 4.1 Implement graceful truncation (df.head(30)) in `src/converter/logic.py`
- [x] 4.2 Update `tests/unit/test_converter.py` with working truncation test
- [x] 4.3 Verify fix with custom verification scripts
- [x] 4.4 Commit changes

## [ ] Refactor converter logic to parser/generator architecture
- [ ] 1.1 Implement BaseParser and BaseGenerator classes
- [ ] 1.2 Implement ChirpParser and ChirpGenerator
- [ ] 1.3 Implement BtechParser and BtechGenerator
- [x] 1.4 Implement ClipboardParser (JSON/CSV)
- [ ] 1.5 Refactor `src/converter/logic.py` to use new architecture with backward compatibility

## [ ] Implement CLI tool
- [ ] 2.1 Set up argparse with subcommands for all conversion directions
- [ ] 2.2 Implement stdin/stdout and file I/O support
- [ ] 2.3 Implement error handling and status reporting to stderr

## [ ] Testing and Verification
- [ ] 3.1 Update unit tests in `tests/unit/test_converter.py`
- [ ] 3.2 Create integration tests in `tests/cli/test_cli.py`
- [ ] 3.3 Verify Web API compatibility and run all tests
