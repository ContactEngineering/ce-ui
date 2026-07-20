pytest_plugins = ["topobank.testing.fixtures"]

# Register topobank's test workflow implementations so the analysis tests can
# resolve them from the registry. register_implementation is idempotent (keyed
# by name), so registering here in addition to anywhere else is harmless.
from topobank.analysis.registry import register_implementation  # noqa: E402
from topobank.testing.workflows import (  # noqa: E402
    SecondTestImplementation, TestImplementation, TestImplementationWithError,
    TestImplementationWithErrorInDependency, TopographyOnlyTestImplementation)

for _implementation in (
    TestImplementation,
    SecondTestImplementation,
    TestImplementationWithError,
    TestImplementationWithErrorInDependency,
    TopographyOnlyTestImplementation,
):
    register_implementation(_implementation)
