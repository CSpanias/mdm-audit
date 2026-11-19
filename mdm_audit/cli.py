"""
Command-line interface for MDM-Audit.

MDM-Audit is a guided assessment tool that assists security
professionals in performing Mobile Device Management (MDM)
security reviews. The tool collects environment information,
conducts a structured control assessment, and generates
findings, remediation guidance, and report outputs.
"""

import argparse

from rich.panel import Panel
from textwrap import dedent

from mdm_audit.exporters.json import (
    build_findings, export_findings_json, export_assessment_responses_json
)
from mdm_audit.exporters.markdown import export_markdown
from mdm_audit.exporters.sureformat import export_sureformat
from mdm_audit.review import run_assessment
from mdm_audit.ui import console


def main() -> None:
    """
    Execute the MDM assessment workflow.
    """

    parser = argparse.ArgumentParser(
        description="Conduct Mobile Device Management (MDM) security reviews.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--csacyber",
        action="store_true",
        help="Export separate platform-specific SureFormat XML files instead of findings JSON",
    )
    args = parser.parse_args()

    results = run_assessment()

    console.print()
    console.print(Panel.fit("[bold green]Assessment Complete[/bold green]"))
    console.print(f"[cyan]Responses:[/cyan] {len(results.responses)}")
    console.print(f"[red]Findings:[/red] {len(results.findings)}")
    console.print(f"[green]Positive Observations:[/green] {len(results.positives)}")

    if not args.csacyber:
        export_findings_json(results, "mdm-findings.json")
    export_markdown(results, "mdm-report.md")
    export_assessment_responses_json(results, "mdm-notes.json")

    if args.csacyber:
        findings = build_findings(results)
        platforms = findings[0]["platforms"]
        if not platforms:
            raise ValueError("SureFormat export requires at least one assessed platform.")
        hostnames = {}
        for platform in platforms:
            hostname = input(f"SureCloud hostname for {platform}: ").strip()
            while not hostname:
                console.print("[red]Hostname is required.[/red]")
                hostname = input(f"SureCloud hostname for {platform}: ").strip()
            hostnames[platform] = hostname
        for platform, hostname in hostnames.items():
            export_sureformat(findings, platform, hostname, f"mdm-findings-{platform}.xml")


if __name__ == "__main__":
    main()