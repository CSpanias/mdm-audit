"""
Markdown reporting functionality.

This exporter generates a consultant-facing assessment
report containing an executive summary, commentary,
and remediation guidance.
"""

from pathlib import Path

from mdm_audit.constants import REFERENCES, COMMENTARY_ORDER
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

    theme_names = [
        theme.lower()
        for theme in themes
    ]

    theme_text = _format_list(theme_names)

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
    if posture == "strong":
        lines.append(
            "The review identified that security "
            "controls were generally well implemented across "
            "the assessed mobile device estate. While several "
            f"opportunities for improvement relating to {theme_text} "
            "were identified, the majority of assessed controls "
            "were operating as intended."
        )

    elif posture == "moderate":
        lines.append(
            "The review identified a mixture of effective "
            "controls and opportunities for improvement across the "
            "mobile device estate. Areas requiring attention related "
            f"to {theme_text}."
        )

    else:
        if theme_text:
            lines.append(
                "The review identified several weaknesses "
                "affecting the implementation and enforcement of "
                "mobile device security controls. Opportunities for "
                f"improvement were identified relating to {theme_text}."
            )

        else:
            lines.append(
                "The review identified several weaknesses "
                "affecting the implementation and enforcement of "
                "mobile device security controls."
            )

    lines.append("")

    #---------------------------------------------------------------------------
    # Third Paragraph
    #---------------------------------------------------------------------------
    impact_areas = []

    if (
        "Patch and Lifecycle Management" in themes
        or "Device Hardening" in themes
    ):
        impact_areas.append(
            "maintaining secure and compliant device configurations"
        )

    if "Access Control" in themes:
        impact_areas.append(
            "enforcing appropriate authentication and access controls"
        )

    if "Data Protection" in themes:
        impact_areas.append(
            "protecting corporate information stored on managed devices"
        )

    if "Application Control" in themes:
        impact_areas.append(
            "governing the use of applications and device functionality"
        )

    if not impact_areas:
        impact_text = ("maintaining secure and compliant device configurations")
    else:
        impact_text = _format_list(impact_areas)

    if results.findings:

        lines.append(
            "The issues identified may reduce assurance that security "
            "requirements are applied consistently across the mobile "
            "estate. Several observations related to controls "
            f"responsible for {impact_text}. "
            "Where such controls are not consistently enforced, the "
            "likelihood of unauthorised access, information disclosure, "
            "or device misuse may increase."
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
            "Overall, the MDM platform provides a foundation for "
            "the management of corporate mobile devices; however, "
            "further work is required to ensure that security "
            "controls are applied consistently across the mobile "
            "estate."
        )

    else:
        lines.append(
            "Overall, significant opportunities exist to strengthen "
            "the security posture of the mobile device estate. "
            "Priority should be given to improving security control "
            "coverage, strengthening device protections, and "
            "ensuring that security requirements are enforced "
            "consistently across managed devices."
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

    print("\n=== COMMENTARY DEBUG ===")
    print("iOS findings:", len(ios_findings))
    print("Android findings:", len(android_findings))

    if ios_findings:
        print("First iOS finding:")
        print(ios_findings[0])

    print("iOS groups:", ios_groups.keys())
    print("Android groups:", android_groups.keys())

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
        lines.append(f"- [{title}]({url})")

    vendor = results.context.mdm_vendor

    if vendor in REFERENCES:
        for title, url in REFERENCES[vendor].items():
            lines.append(f"- [{title}]({url})")



    return lines


def export_markdown(
    results: AssessmentResults,
    output_file: str,
) -> None:
    """
    Export assessment report as Markdown.
    """

    path = Path(output_file)

    lines = [
        f"# {results.context.client_name} - MDM Assessment",
        "",
    ]

    lines.extend(
        _generate_executive_summary(results)
    )

    lines.extend(
        _generate_commentary(results)
    )

    lines.extend(
        _generate_remediation(results)
    )

    path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )