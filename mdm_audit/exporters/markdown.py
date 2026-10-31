"""
Markdown reporting functionality.

This exporter generates a consultant-facing assessment
report containing an executive summary, commentary,
and remediation guidance.
"""

from pathlib import Path

from mdm_audit.constants import (
    REFERENCES,
    REMEDIATIONS,
    COMMENTARY_ORDER,
    COMMENTARY_INTROS,
    COMMENTARY_SUMMARIES,
    COVERAGE_TEXT,
    THEME_DISPLAY,
    NUMBER_WORDS
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

def _generate_assessment_context(
    results: AssessmentResults,
) -> list[str]:
    """
    Generate the assessment context section.
    """

    context = results.context

    lines = []

    lines.append(
        "The assessed mobile device management environment is summarised below:"
    )
    lines.append("")

    lines.extend([
        "| Property | Value |",
        "|----------|-------|",
        f"| Organisation | {context.client_name} |",
        f"| Platforms Reviewed | {context.platforms} |",
        f"| MDM Solution | {context.mdm_vendor.value} |",
        f"| MDM Version | {context.mdm_version} |",
    ])

    if context.ios_device_count is not None:
        lines.append(
            f"| Enrolled iOS Devices | {context.ios_device_count} |"
        )

    if context.android_device_count is not None:
        lines.append(
            f"| Enrolled Android Devices | {context.android_device_count} |"
        )

    if context.ios_policy_count is not None:
        lines.append(
            f"| iOS Compliance Policies | {context.ios_policy_count} |"
        )

    if context.android_policy_count is not None:
        lines.append(
            f"| Android Compliance Policies | {context.android_policy_count} |"
        )

    if context.minimum_ios_version:
        lines.append(
            f"| Minimum Supported iOS Version | {context.minimum_ios_version} |"
        )

    if context.minimum_android_version:
        lines.append(
            f"| Minimum Supported Android Version | {context.minimum_android_version} |"
        )

    lines.append("")

    return lines


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


def _get_observation_summary(
    findings: list,
) -> str:
    """
    Build a concise summary of the observations
    identified within a finding group.
    """

    observations = []

    for finding in findings:

        sentence = (
            finding.commentary
            .strip()
            .split(".")[0]
            .strip()
        )

        sentence = (
            sentence[0].lower()
            + sentence[1:]
        )

        observations.append(sentence)

    observations = sorted(set(observations))

    return _format_list(observations)



def _build_group_commentary(
    group_name: str,
    findings: list,
) -> str:
    """
    Generate narrative commentary for a group of findings.
    """

    summary = COMMENTARY_SUMMARIES[group_name]

    intro = COMMENTARY_INTROS[group_name]

    observations = _get_observation_summary(findings)

    sections = {finding.section for finding in findings}

    if (
        "configuration" in sections
        and "compliance" in sections
    ):
        coverage = COVERAGE_TEXT[group_name]["both"]

    elif "configuration" in sections:

        coverage = COVERAGE_TEXT[group_name]["configuration"]

    elif "compliance" in sections:

        coverage = COVERAGE_TEXT[group_name]["compliance"]

    else:

        coverage = (
            "The identified weaknesses affected controls within this area of "
            "the MDM platform."
        )

    return (
        f"{summary} "
        f"{intro}{observations}. "
        f"{coverage}"
    )


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

    lines.extend(_generate_assessment_context(results))

    if ios_findings:

        lines.append("### iOS Devices")
        lines.append("")

        for group_name, findings in ios_groups.items():

            lines.append(f"#### {group_name}")
            lines.append("")

            lines.append(_build_group_commentary(group_name, findings))

    lines.append("")

    if android_findings:

        lines.append("### Android Devices")
        lines.append("")

        for group_name, findings in android_groups.items():

            lines.append(f"#### {group_name}")
            lines.append("")
            lines.append(_build_group_commentary(group_name, findings))

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

    recommendations = {}

    for finding in results.findings:

        remediation_id = getattr(finding, "remediation_id", None)

        if remediation_id:

            recommendations.setdefault(
                remediation_id,
                REMEDIATIONS[remediation_id],
            )

        else:

            recommendations.setdefault(
                finding.solution.strip(),
                finding.solution.strip(),
            )

    for recommendation in sorted(recommendations.values()):
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