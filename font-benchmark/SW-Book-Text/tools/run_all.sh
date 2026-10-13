#!/usr/bin/env bash
# Full pipeline: build -> specimen -> reports -> tests -> validators.  Logs to reports/test_results.txt
set -u
cd "$(dirname "$0")/.."
LOG=reports/test_results.txt
START=$(date +%s)
{
echo "# SW Book Text benchmark prototype - full validation log"
echo "# started: $(date -u +%FT%TZ)   host: $(uname -srm)   python: $(python3 --version 2>&1)"
run() { echo; echo "\$ $*"; "$@" 2>&1; echo "[exit code: $?]"; }
run bash -c 'cd src && python3 -m swbook.build'
run python3 specimen/build_specimen.py
run python3 tools/make_reports.py
run sha256sum fonts/SWBookText-Regular.ttf fonts/SWBookText-Bold.ttf specimen/SWBookText-Specimen.pdf
run python3 -m pytest tests -v -p no:cacheprovider
run fontbakery check-universal --skip-network --succinct -n fonts/SWBookText-Regular.ttf fonts/SWBookText-Bold.ttf
run fontbakery check-opentype --skip-network --succinct -n fonts/SWBookText-Regular.ttf fonts/SWBookText-Bold.ttf
run python3 -m ots fonts/SWBookText-Regular.ttf
run python3 -m ots fonts/SWBookText-Bold.ttf
run pdfinfo specimen/SWBookText-Specimen.pdf
run pdffonts specimen/SWBookText-Specimen.pdf
run python3 tools/shaping_demo.py
echo; echo "# finished in $(( $(date +%s) - START )) s"
} 2>&1 | tee "$LOG"
