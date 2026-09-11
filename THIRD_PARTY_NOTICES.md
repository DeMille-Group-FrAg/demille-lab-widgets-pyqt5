# Third-party notices

This package depends on PyQt5, pyqtgraph, and NumPy. Those projects are not
bundled into this source distribution and remain subject to their respective
licenses.

## Implementation provenance

An earlier internal widget collection cited several external examples and
snippets. Before this package's first public release, the affected components
were replaced with new package-local implementations based on the required
observable behavior and the public Qt APIs:

- cursor-position-aware integer and decimal stepping;
- scientific-notation validation, formatting, and stepping;
- a sparse flexible grid layout; and
- synchronized table overlays for frozen leading rows and columns.

The current source files do not incorporate the previously cited snippet or
example implementations. This record is retained to explain the review and
rewrite; it is not an attribution claim for code contained in the release.
