"""
Markdown reporting functionality.

This exporter generates a consultant-facing assessment
report containing an executive summary, commentary,
and remediation guidance.
"""

from pathlib import Path

from mdm_audit.constants import (
    REFERENCES, COMMENTARY_ORDER, THEME_DISPLAY, NUMBER_WORDS
)
from mdm_audit.models import AssessmentResults, Platform


def _get_review_scope(
    results: AssessmentResults,
) -> str:

    platforms = {
        response.platform
        for response in results.responses
    }

    if (
        Platform.IOS in platforms
        and Platform.ANDROID in platforms
    ):
        return "both Android and iOS devices"

    if Platform.IOS in platforms:
        return "iOS devices"

    return "Android devices"


def _format_count(
    count: int,
    singular: str,
    plural: str,
) -> str:
    """
    Convert counts into report-friendly text.

    Examples:
        0 -> "no findings"
        1 -> "one finding"
        2 -> "two findings"
        10 -> "10 findings"
    """

    value = NUMBER_WORDS.get(count, str(count))

    if count == 1:
        return f"{value} {singular}"

    return f"{value} {plural}"

#-------------------------------------------------------------------------------
# Executive Summary
#-------------------------------------------------------------------------------

def _get_identified_themes(
    results: AssessmentResults,
) -> list[str]:
    """
    Return the themes affected by identified findings.
    """

    themes = {
        finding.theme
        for finding in results.findings
        if getattr(finding, "theme", None)
    }

    return sorted(themes)


def _get_security_posture(
    results: AssessmentResults,
) -> str:
    """
    Determine the overall security posture based on the
    ratio of positive observations to findings.
    """

    total = (
        len(results.findings)
        + len(results.positives)
    )

    if total == 0:
        return "unknown"

    ratio = len(results.positives) / total

    if ratio >= 0.8:
        return "strong"

    if ratio >= 0.5:
        return "moderate"

    return "weak"


def _format_list(items: list[str]) -> str:

    if not items:
        return ""

    if len(items) == 1:
        return items[0]

    if len(items) == 2:
        return f"{items[0]} and {items[1]}"

    return (
        ", ".join(items[:-1])
        + f", and {items[-1]}"
    )


def _generate_executive_summary(
    results: AssessmentResults,
) -> list[str]:
    """
    Generate the executive summary section.
    """

    lines = []

    posture = _get_security_posture(results)

    scope = _get_review_scope(results)

    themes = _get_identified_themes(results)

    lines.append("## Executive Summary")
    lines.append("")

    #---------------------------------------------------------------------------
    # Introductory Paragraph
    #---------------------------------------------------------------------------
    lines.append(
        "A Mobile Device Management (MDM) review was conducted "
        f"for the {results.context.client_name} environment "
        f"covering {scope}. The assessment considered device "
        "compliance requirements, authentication controls, "
        "application governance, device hardening measures, "
        "and platform-specific security restrictions."
    )

    lines.append("")

    #---------------------------------------------------------------------------
    # Second Paragraph
    #---------------------------------------------------------------------------
    finding_count = len(results.findings)
    positive_count = len(results.positives)

    finding_text = _format_count(finding_count, "finding", "findings")

    positive_text = _format_count(
        positive_count, "positive observation", "positive observations"
    )

    if posture == "strong":
        lines.append(
            f"The assessment identified {finding_text} "
            f"and {positive_text}. Security "
            "controls were generally well implemented across the "
            "assessed mobile device estate and the majority of "
            "controls were operating as intended."
        )

    elif posture == "moderate":
        lines.append(
            f"The assessment identified {finding_text} "
            f"and {positive_text}. A mixture "
            "of effective controls and opportunities for improvement "
            "was observed across the mobile device estate."
        )

    else:
        lines.append(
            f"The assessment identified {finding_text} "
            f"and {positive_text}. "
            "Weaknesses were observed across multiple areas of the "
            "mobile device management implementation, indicating "
            "that expected security controls were not consistently "
            "implemented or enforced across the assessed device estate."
        )

    lines.append("")

    #---------------------------------------------------------------------------
    # Third Paragraph
    #---------------------------------------------------------------------------
        
    theme_text = _format_list(
        [
            THEME_DISPLAY.get(theme, theme.lower())
            for theme in themes
        ]
    )

    if results.findings:

        lines.append(
            f"The most significant observations related to {theme_text}. "
            "The assessment identified weaknesses affecting both "
            "the enforcement of security controls through device "
            "configuration policies and the validation of those "
            "controls through compliance policies. Where such "
            "controls are not consistently enforced and monitored, "
            "the likelihood of unauthorised access, information "
            "disclosure, device compromise, or policy non-compliance "
            "may increase."
        )

    else:

        lines.append(
            "No significant weaknesses were identified during the review. "
            "The assessed controls were operating as intended and "
            "contributed towards the secure management of mobile devices "
            "and corporate information."
        )

    lines.append("")

    #---------------------------------------------------------------------------
    # Conclusion
    #---------------------------------------------------------------------------
    if posture == "strong":
        lines.append(
            "Overall, the assessed configuration provided a "
            "generally effective foundation for the management "
            "and security of corporate mobile devices. Addressing "
            "the identified opportunities would further improve "
            "the consistency and effectiveness of existing controls."
        )

    elif posture == "moderate":
        lines.append(
            "Overall, the assessed configuration provides a reasonable "
            "foundation for the secure management of mobile devices; "
            "however, several control weaknesses should be addressed to "
            "improve the consistency and effectiveness of security "
            "enforcement across the estate."
        )

    else:
        lines.append(
            "Overall, significant opportunities exist to strengthen "
            "the security posture of the mobile device estate. "
            "Priority should be given to improving both the "
            "enforcement of security requirements through device "
            "configuration policies and the validation of those "
            "requirements through compliance monitoring controls."
        )

    lines.append("")

    return lines

#-------------------------------------------------------------------------------
# Technical Commentary
#-------------------------------------------------------------------------------

def _get_group_intro(
    group_name: str,
) -> str:

    intros = {
        "Device Lifecycle and Compliance": (
            "The review identified a number of weaknesses relating "
            "to device lifecycle management and compliance monitoring "
            "controls. These controls are intended to ensure that "
            "managed devices remain visible, compliant, and subject "
            "to ongoing organisational oversight."
        ),

        "Authentication and Access Control": (
            "Opportunities for improvement were identified within "
            "the controls used to authenticate users and restrict "
            "access to managed devices and corporate resources. "
            "Effective implementation of these controls helps ensure "
            "that access is limited to authorised users."
        ),

        "Data Protection": (
            "The assessment highlighted several areas where controls "
            "designed to protect corporate information could be "
            "further strengthened. These controls play an important "
            "role in preventing the unauthorised disclosure, transfer, "
            "or loss of sensitive information."
        ),

        "Device Security and Hardening": (
            "Further observations related to device hardening measures "
            "intended to reduce the attack surface of managed devices. "
            "Weaknesses in this area may increase exposure to insecure "
            "configurations, unnecessary functionality, or potential "
            "abuse of device capabilities."
        ),

        "Application Governance": (
            "The review also identified opportunities to strengthen "
            "application governance and software management controls. "
            "These controls help ensure that software installed on "
            "managed devices remains appropriate for organisational "
            "use and aligned with security requirements."
        ),
    }

    return intros.get(group_name, "")


def _group_findings(
    findings,
) -> dict[str, list]:
    """
    Group findings by commentary group.
    """

    grouped = {}

    for finding in findings:

        group = getattr(
            finding,
            "commentary_group",
            None,
        )

        if not group:
            continue

        grouped.setdefault(
            group,
            []
        ).append(finding)

    ordered = {}

    for group in COMMENTARY_ORDER:
        if group in grouped:
            ordered[group] = grouped[group]

    return ordered


def _generate_commentary(
    results: AssessmentResults,
) -> list[str]:
    """
    Generate the assessment commentary section.
    """

    lines = []

    ios_findings = [
        finding
        for finding in results.findings
        if finding.platform == Platform.IOS
    ]

    android_findings = [
        finding
        for finding in results.findings
        if finding.platform == Platform.ANDROID
    ]

    ios_groups = _group_findings(ios_findings)
    android_groups = _group_findings(android_findings)

    lines.append("## Commentary")
    lines.append("")

    lines.append(
        "A Mobile Device Management (MDM) review was conducted "
        f"for the {results.context.client_name} environment. "
        "The assessment reviewed the effectiveness of controls "
        "implemented to secure managed mobile devices and protect "
        "corporate information."
    )

    lines.append("")

    lines.append("### iOS Devices")
    lines.append("")

    if ios_findings:

        for group_name, findings in ios_groups.items():

            lines.append(_get_group_intro(group_name))
            lines.append("")

            for finding in findings:
                lines.append(finding.commentary.strip())
                lines.append("")

    else:
        lines.append(
            "No issues were identified affecting managed iOS devices."
        )

    lines.append("")

    lines.append("### Android Devices")
    lines.append("")

    if android_findings:

        for group_name, findings in android_groups.items():

            lines.append(_get_group_intro(group_name))
            lines.append("")

            for finding in findings:
                lines.append(finding.commentary.strip())
                lines.append("")

    else:
        lines.append(
            "No issues were identified affecting managed Android devices."
        )

    lines.append("")

    lines.append("### Conclusion")
    lines.append("")

    if results.findings:
        lines.append(
            "The review identified several opportunities to "
            "further strengthen the security posture of managed "
            "mobile devices. Addressing the observations "
            "identified throughout the assessment would improve "
            "assurance that security requirements are applied "
            "consistently and that corporate information remains "
            "appropriately protected."
        )
    else:
        lines.append(
            "No security weaknesses were identified during the "
            "review. The assessed controls appeared to provide "
            "an appropriate baseline for the secure management "
            "of corporate mobile devices."
        )

    lines.append("")

    return lines

#-------------------------------------------------------------------------------
# Remediation
#-------------------------------------------------------------------------------
def _generate_remediation(
    results: AssessmentResults,
) -> list[str]:
    """
    Generate the remediation section.
    """

    lines = []

    lines.append("## Remediation")
    lines.append("")

    if not results.findings:
        lines.append("No remediation actions are currently required.")
        lines.append("")

        return lines

    lines.append("The following remediation actions are recommended:")
    lines.append("")

    recommendations = set()

    for finding in results.findings:
        recommendations.add(finding.solution.strip())

    for recommendation in sorted(recommendations):
        lines.append(f"- {recommendation}")

    lines.append("")

    lines.append("### References")
    lines.append("")

    for title, url in REFERENCES["Generic"].items():
        lines.append(f"- [{url}]({url})")

    vendor = results.context.mdm_vendor

    if vendor in REFERENCES:
        for title, url in REFERENCES[vendor].items():
            lines.append(f"- [{url}]({url})")



    return lines


def export_markdown(
    results: AssessmentResults,
    output_file: str,
) -> None:
    """
    Export assessment report as Markdown.
    """

    path = Path(output_file)

    lines = [f"# {results.context.client_name} - MDM Assessment", ""]

    lines.extend(_generate_executive_summary(results))

    lines.extend(_generate_commentary(results))

    lines.extend(_generate_remediation(results))

    path.write_text("\n".join(lines), encoding="utf-8")