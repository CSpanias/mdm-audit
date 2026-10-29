"""
Assessment workflow engine for MDM reviews.

This module contains the core assessment workflow logic and is
responsible for:

- Selecting the appropriate context fields
- Selecting the appropriate audit questions
- Filtering controls by platform
- Coordinating the assessment workflow

The review engine is intentionally separated from reporting and
export functionality to ensure the assessment logic remains
independent from output formats.
"""

from rich.panel import Panel

from mdm_audit.models import (
    AssessmentResults,
    AuditAnswer,
    ContextField,
    Finding,
    Platform,
    PositiveObservation,
    Question,
    QuestionResponse,
    ReviewContext,
    Vendor
)
from mdm_audit.loader import (
    load_context_fields,
    load_questions,
)
from mdm_audit.ui import console



def get_applicable_questions(
    questions: list[Question],
    platforms: list[Platform],
) -> list[Question]:
    """
    Return the assessment questions applicable to the selected
    platforms.

    Shared controls are always included, while platform-specific
    controls are only included when the corresponding platform is
    within scope. Questions are returned in the order defined
    within the assessment configuration.
    """

    applicable_questions = []

    for question in questions:
        if question.applies_to == Platform.BOTH:
            applicable_questions.append(question)

        elif question.applies_to in platforms:
            applicable_questions.append(question)

    return applicable_questions


def get_fields_by_phase(
    fields: list[ContextField],
    phase: str,
) -> list[ContextField]:
    """
    Return context fields belonging to the specified phase.
    """

    return [
        field
        for field in fields
        if field.phase == phase
    ]


def collect_context(
    fields: list[ContextField],
    responses: dict | None = None,
    start: int = 1,
    overall_total: int | None = None,
) -> dict:
    """
    Collect contextual information about the reviewed MDM
    environment.

    Collected values are merged into the supplied response
    dictionary and returned to the caller.
    """

    responses = responses or {}

    overall_total = overall_total or len(fields)

    for current, field in enumerate(fields, start=start):

        progress = max(1, int((current / overall_total) * 20))

        bar = (
            f"[green]{'█' * progress}[/green]"
            f"[dim]{'░' * (20 - progress)}[/dim]"
        )

        console.print()
        console.print(
            f"[bold cyan][CONTEXT {current}/{overall_total}][/bold cyan] "
            f"{bar} "
            f"[bold]{field.label}[/bold]"
        )

        vendor = responses.get("mdm_vendor")

        if field.hints:

            common_hint = field.hints.get("common")

            if common_hint:
                console.print(
                    Panel.fit(
                        common_hint.strip(),
                        title="Evidence",
                        border_style="blue",
                    )
                )

            if vendor:

                vendor_hint = field.hints.get(vendor)

                if vendor_hint:
                    console.print()

                    console.print(
                        Panel.fit(
                            vendor_hint.strip(),
                            title="Location",
                            border_style="yellow",
                        )
                    )

                    console.print()

        if field.type == "choice" and field.options:

            console.print()

            for index, option in enumerate(field.options, start=1):
                console.print(f"[cyan]{index}.[/cyan] {option}")

            while True:
                choice = input("> ").strip()

                try:
                    value = field.options[int(choice) - 1]
                    break

                except (ValueError, IndexError):
                    console.print("[red]Invalid selection.[/red]")

        else:

            value = input("> ").strip()

            if field.required:

                while not value:
                    console.print("[red]This field is required.[/red]")
                    value = input("> ").strip()

        if field.type == "integer":

            while True:
                try:
                    value = int(value)

                    if value < 0:
                        raise ValueError

                    break

                except ValueError:
                    console.print(
                        "[red]Please enter a valid number.[/red]"
                    )
                    value = input("> ").strip()

        responses[field.id] = value

    return responses


def ask_question(
    question: Question,
    vendor: Vendor,
    platform: Platform,
    current: int,
    total: int,
) -> QuestionResponse:
    """
    Present an assessment question and record the assessor's
    response.

    Vendor-specific navigation guidance and evidence collection
    notes are displayed when available. Questions are presented
    within a platform-specific review and a single response is
    recorded for the selected platform.
    """

    common_hint = (
        question.hints.common.strip()
        if question.hints.common
        else None
    )

    vendor_hint = None

    if vendor == Vendor.INTUNE and question.hints.intune:
        vendor_hint = question.hints.intune.strip()

    console.print()

    progress = int((current / total) * 20)

    bar = (
        f"[green]{'█' * progress}[/green]"
        f"[dim]{'░' * (20 - progress)}[/dim]"
    )

    console.print(
        f"[bold cyan][{platform.value.upper()} {current}/{total}][/bold cyan] "
        f"{bar} "
        f"[bold]{question.question}[/bold]"
    )

    console.print()

    if common_hint:
        console.print(
            Panel.fit(common_hint, title="Evidence", border_style="blue")
        )

    platform_hint = None

    if platform == Platform.IOS:
        platform_hint = question.hints.ios

    elif platform == Platform.ANDROID:
        platform_hint = question.hints.android

    check_hints = []

    if vendor_hint:
        check_hints.append(vendor_hint)

    if platform_hint:
        check_hints.append(platform_hint.strip())

    if check_hints:
        console.print(
            Panel.fit(
                "\n\n".join(check_hints),
                title="Check",
                border_style="cyan",
            )
        )

    console.print()

    console.print("1. Compliant")
    console.print("2. Non-Compliant")
    console.print("3. Not Applicable")
    console.print("4. Unknown")

    while True:
        choice = input("> ").strip()

        match choice:
            case "1":
                answer = AuditAnswer.COMPLIANT
                break

            case "2":
                answer = AuditAnswer.NON_COMPLIANT
                break

            case "3":
                answer = AuditAnswer.NOT_APPLICABLE
                break

            case "4":
                answer = AuditAnswer.UNKNOWN
                break

            case _:
                console.print("[red]Invalid selection.[/red]")

    console.print()
    console.print("[dim]Notes (optional)[/dim]")

    notes = input("> ").strip() or None

    return QuestionResponse(
        finding_id=question.finding_id,
        platform=platform,
        answer=answer,
        notes=notes,
    )


def conduct_review(
    questions: list[Question],
    vendor: Vendor,
    platforms: list[Platform],
) -> list[QuestionResponse]:
    """
    Execute the assessment questionnaire.

    Questions are presented separately for each platform within the review 
    scope. Shared controls are included within each platform review where 
    applicable.

    Responses collected during the assessment are returned for subsequent 
    finding generation and reporting.
    """

    responses = []

    for platform in platforms:

        platform_questions = [
            question
            for question in questions
            if (
                question.applies_to == Platform.BOTH
                or question.applies_to == platform
            )
        ]

        total = len(platform_questions)

        for current, question in enumerate(platform_questions, start=1):

            response = ask_question(
                question,
                vendor,
                platform,
                current,
                total,
            )

            responses.append(response)

    return responses


def generate_findings(
    questions: list[Question],
    responses: list[QuestionResponse],
) -> list[Finding]:
    """
    Generate findings from assessment responses.

    A finding is created whenever a response does not match the
    expected secure configuration defined by the corresponding
    question.
    """

    findings = []

    questions_by_finding_id = {
        question.finding_id: question
        for question in questions
    }

    for response in responses:
        question = questions_by_finding_id[response.finding_id]

        if response.answer in (
            AuditAnswer.NOT_APPLICABLE,
            AuditAnswer.UNKNOWN,
        ):
            continue

        if response.answer != question.expected_answer:
            findings.append(
                Finding(
                    finding_id=question.finding_id,
                    theme=question.theme,
                    commentary_group=question.commentary_group,
                    section=question.section,
                    platform=response.platform,
                    title=question.finding_title,
                    description=question.description,
                    commentary=question.commentary,
                    solution=question.solution,
                )

            )

    return findings


def generate_positive_observations(
    questions: list[Question],
    responses: list[QuestionResponse],
) -> list[PositiveObservation]:
    """
    Generate positive observations from assessment responses.

    Positive observations are created for controls that were found
    to be configured in accordance with the expected secure state.
    """

    positives = []

    questions_by_finding_id = {
        question.finding_id: question
        for question in questions
    }

    for response in responses:
        question = questions_by_finding_id[response.finding_id]

        if response.answer in (
            AuditAnswer.NOT_APPLICABLE,
            AuditAnswer.UNKNOWN,
        ):
            continue

        if response.answer == question.expected_answer:
            positives.append(
                PositiveObservation(
                    finding_id=question.finding_id,
                    platform=response.platform,
                    text=question.positive,
                )
            )

    return positives


def build_assessment_results(
    context: ReviewContext,
    questions: list[Question],
    responses: list[QuestionResponse],
) -> AssessmentResults:
    """
    Build the final assessment results object.

    This combines the collected context, assessment responses,
    generated findings, and positive observations into a single
    structure used by reporting and export components.
    """

    findings = generate_findings(
        questions,
        responses,
    )

    positives = generate_positive_observations(
        questions,
        responses,
    )

    return AssessmentResults(
        context=context,
        findings=findings,
        positives=positives,
        responses=responses,
    )


def run_assessment() -> AssessmentResults:
    """
    Execute a complete MDM assessment.

    The assessment workflow consists of context collection,
    questionnaire execution, and results generation. The
    completed assessment results are returned for reporting
    and export.
    """

    all_fields = load_context_fields()

    setup_fields = get_fields_by_phase(all_fields, "setup")

    context_data = collect_context(setup_fields)

    match context_data["platforms"]:
        case "iOS and Android":
            platforms = [Platform.IOS, Platform.ANDROID]

        case "iOS only":
            platforms = [Platform.IOS]

        case "Android only":
            platforms = [Platform.ANDROID]

        case _:
            raise ValueError("Invalid platform selection")

    platform_fields = [
        field
        for field in get_fields_by_phase(
            all_fields,
            "context",
        )
        if any(
            platform in field.platforms
            for platform in platforms
        )
    ]

    total_context_fields = (len(setup_fields) + len(platform_fields))

    context_data = collect_context(
        platform_fields,
        context_data,
        start=len(setup_fields) + 1,
        overall_total=total_context_fields,
    )

    context = ReviewContext(**context_data)

    questions = get_applicable_questions(load_questions(), platforms)

    question_responses = conduct_review(
        questions,
        context.mdm_vendor,
        platforms,
    )

    return build_assessment_results(
        context=context,
        questions=questions,
        responses=question_responses,
    )