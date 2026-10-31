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
    export_findings_json, export_assessment_responses_json
)
from mdm_audit.exporters.markdown import export_markdown
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

    parser.parse_args()

    results = run_assessment()

    console.print()
    console.print(Panel.fit("[bold green]Assessment Complete[/bold green]"))
    console.print(f"[cyan]Responses:[/cyan] {len(results.responses)}")
    console.print(f"[red]Findings:[/red] {len(results.findings)}")
    console.print(f"[green]Positive Observations:[/green] {len(results.positives)}")

    export_findings_json(results, "mdm-findings.json")
    export_markdown(results, "mdm-report.md")
    export_assessment_responses_json(results, "mdm-notes.json")


if __name__ == "__main__":
    main()