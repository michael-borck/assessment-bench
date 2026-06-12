"""Capability manifest — family-consistent identity for the bench's HTTP face."""

from lens_contract import make_manifest

MANIFEST = make_manifest(
    name="assessment-bench",
    accepts=["experiment"],
    produces="ExperimentResult",
    extensions=[],
    auto_routable=False,  # a bench is invoked deliberately, never routed to by file type
    role="bench",
)
