---
task: Write zero-mock tests for data_visualization engines module
slug: 20260307-120000_data-visualization-tests
effort: Advanced
phase: complete
progress: 28/28
mode: ALGORITHM
started: 2026-03-07T12:00:00
updated: 2026-03-07T12:15:00
---

## Context

The data_visualization module has 20+ test files already. Existing tests cover most files at 90%+.
The task is to write comprehensive zero-mock tests for advanced_plotter.py and related engines files.

After analysis:
- `engines/advanced_plotter.py`: 97-98% covered by existing test_advanced_plotter.py (142 tests, all pass)
- Missing: line 152 (save_path param via finalize_plot), import error path (intentionally untestable)
- `engines/plotter.py` (the simpler Plotter wrapper): was 39% covered, then improved to 100%
- `_compat.py`: 26% — fallback stubs only reachable if codomyrmex.performance is not installed
- Most engines subfiles are 92-96% (TYPE_CHECKING guards are intentionally uncoverable)

Real gaps to target:
1. Plotter wrapper class (plotter.py) — all 6 chart methods
2. finalize_plot with save_path parameter
3. _compat fallback behavior (performance_context no-op context manager)
4. apply_scatter standalone function in _scatter.py
5. Edge cases: save_plot failure path (no figure), clear_figures resets state

### Risks

- matplotlib show() triggers warnings on Agg backend — tests must set show_plot=False in config
- Coverage numbers run against full codebase when --cov is used — only per-module view is meaningful
- TYPE_CHECKING import guards (lines 10-14 in mixins) are never reachable at runtime — not a real gap

## Criteria

- [ ] ISC-1: TestPlotterWrapper tests bar_chart method returns Figure
- [ ] ISC-2: TestPlotterWrapper tests line_plot method returns Figure
- [ ] ISC-3: TestPlotterWrapper tests scatter_plot method returns Figure
- [ ] ISC-4: TestPlotterWrapper tests histogram method returns Figure
- [ ] ISC-5: TestPlotterWrapper tests pie_chart method returns Figure
- [ ] ISC-6: TestPlotterWrapper tests heatmap method returns Figure
- [ ] ISC-7: TestPlotterWrapper tests custom figure_size passed through
- [ ] ISC-8: TestFinalizePlotWithSavePath tests save_path param saves file to disk
- [ ] ISC-9: TestFinalizePlotWithSavePath asserts file exists at save_path
- [ ] ISC-10: TestFinalizePlotWithSavePath cleanup removes temp file after test
- [ ] ISC-11: TestSavePlotNoFigure tests save_plot returns False with no current figure
- [ ] ISC-12: TestClearFigures tests current_figure is None after clear
- [ ] ISC-13: TestClearFigures tests current_axes is None after clear
- [ ] ISC-14: TestClearFigures tests figures list is empty after clear
- [ ] ISC-15: TestApplyScatter tests standalone apply_scatter function returns PathCollection
- [ ] ISC-16: TestCompatFallback tests monitor_performance no-op decorator passes through return value
- [ ] ISC-17: TestCompatFallback tests performance_context no-op enters and exits cleanly
- [ ] ISC-18: TestCompatFallback tests PERFORMANCE_MONITORING_AVAILABLE is boolean
- [ ] ISC-19: TestPlotDatasetDispatch tests LINE type dispatches to ax.plot
- [ ] ISC-20: TestPlotDatasetDispatch tests SCATTER type dispatches to ax.scatter
- [ ] ISC-21: TestPlotDatasetDispatch tests BAR type dispatches to ax.bar
- [ ] ISC-22: TestPlotDatasetDispatch tests HISTOGRAM type dispatches to ax.hist
- [ ] ISC-23: TestIterAxes tests single axes yields one item
- [ ] ISC-24: TestIterAxes tests multi-subplot axes yields all items via flat
- [ ] ISC-25: All 28+ tests pass with zero failures
- [ ] ISC-26: Zero use of unittest.mock, MagicMock, or monkeypatch
- [ ] ISC-27: Module-level skipif guard for missing matplotlib/seaborn/numpy/pandas
- [ ] ISC-28: engines coverage reaches 98%+ per-file across all engines subfiles

## Decisions

- Use PlotConfig(show_plot=False) everywhere to avoid Agg backend plt.show() warnings
- Use tmp_path pytest fixture for save_path tests (real file I/O, zero mocks)
- _compat.py fallback stubs can only be tested if performance module absent; test the real path instead
- apply_scatter in _scatter.py is a standalone function — call directly with a real axes object

## Verification

Tests written and run — see EXECUTE phase results.
