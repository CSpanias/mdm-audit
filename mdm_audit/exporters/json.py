"""
JSON export functionality.

This exporter generates machine-readable output intended
for consumption by downstream tooling such as XML
converters and reporting pipelines.
"""

import json
from pathlib import Path

from mdm_audit.models import AssessmentResults


def export_findings_json(
    results: AssessmentResults,
    output_file: str,
) -> None:
    """
    Export findings in the standard findings format.
    """

    assessment_platforms = []
    
    if results.context.ios_policy_count is not None:
        assessment_platforms.append("ios")

    if results.context.android_policy_count is not None:
        assessment_platforms.append("android")

    findings = [
        {
            "id": "mdm-audit",
            "title": "MDM Policy Review",
            "description": (
                "A review of the organisation's mobile "
                "device management configuration was performed."
            ),
            "platforms": assessment_platforms,
        }
    ]

    grouped_findings = {}

    for finding in results.findings:
        if finding.finding_id not in grouped_findings:
            grouped_findings[finding.finding_id] = {
                "id": finding.finding_id,
                "title": finding.title,
                "description": finding.description,
                "platforms": [],
            }

        grouped_findings[finding.finding_id][
            "platforms"
        ].append(
            finding.platform.value
        )

    for finding in grouped_findings.values():
        finding["platforms"] = sorted(
            set(finding["platforms"])
        )

    findings.extend(
            grouped_findings.values()
        )

    path = Path(output_file)

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            {"findings": findings},
            file,
            indent=4,
        )