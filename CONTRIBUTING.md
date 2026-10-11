# Contributing

Open an issue describing the problem and expected result before a substantial behavior change. Include plugin version, exact OrcaSlicer build, operating system, and a minimal reproduction. Use the included 10 mm cube when possible; remove private models, paths, and credentials from reports.

Follow the [development commands](README.md#development). Build the wheel before running the full test suite. Numerical changes need independent expected values; UI changes need browser coverage. Fake-host and browser tests do not establish native Orca compatibility. Record which native checks were actually performed in [testing.md](docs/testing.md).

Bath-reference changes must cite the manufacturer's product-specific documentation, preserve its original units, and distinguish operating examples from limits or startup recommendations. Do not infer a generic voltage from mesh area. Keep unavailable references blank rather than guessing.

Submit a focused pull request with the reason, changed behavior, verification results, and remaining limitations. Contributions are provided under GPL-3.0-or-later, the project's license. Do not include third-party code without compatible licensing and attribution.
