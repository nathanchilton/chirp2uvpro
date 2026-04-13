# TODO

## [x] Investigate E2E 500 error discrepancy
- [x] 1.1 Inspect `src/app/templates/partials/converter_ui.html` for HTHTMX request details
- [x] 1.2 Inspect `src/app/static/js/main.js` for client-side logic interference
- [x] 1.3 Implement Playwright network interception to verify E2E test payload (headers and/or body)
- [x] 1.4 Run E2E tests with enhanced logging to capture 500 error traceback

## [x] Fix identified issue
- [x] 2.1 Fix identified issue in API or UI

## [x] Verification
- [x] 3.1 Verify fix with reproduction scripts
- [x] 3.2 Run E2E tests to confirm fix
- [x] 3.3 Commit changes
