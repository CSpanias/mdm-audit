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


def get_applicable_context_fields(
    fields: list[ContextField],
    platforms: list[Platform],
) -> list[ContextField]:
    """
    Return the context fields applicable to the selected platforms.

    Platform-specific fields are filtered according to the review
    scope and returned in display order for collection during the
    assessment setup phase.
    """

    applicable_fields = []

    for field in fields:
        if any(platform in field.platforms for platform in platforms):
            applicable_fields.append(field)

    return sorted(applicable_fields, key=lambda field: field.order)


def select_platforms() -> list[Platform]:
    """
    Prompt the assessor to define the assessment scope.

    The selected platforms determine which context fields and
    assessment questions will be included in the review.
    """


    console.print()
    console.print("[bold]Which mobile platforms are being reviewed?[/bold]")
    console.print("1. iOS and Android")
    console.print("2. iOS only")
    console.print("3. Android only")

    while True:
        choice = input("> ").strip()

        match choice:
            case "1":
                return [Platform.IOS, Platform.ANDROID]

            case "2":
                return [Platform.IOS]

            case "3":
                return [Platform.ANDROID]

            case _:
                console.print("[red]Invalid selection.[/red]")


def collect_context(
    fields: list[ContextField],
) -> ReviewContext:
    """
    Collect contextual information about the reviewed MDM
    environment.

    The collected information describes the environment under
    review and is used within generated reports, exports, and
    assessment summaries.
    """

    responses = {}

    for field in fields:

        console.print()

        if field.type == "choice" and field.options:
            console.print(f"\n[bold]{field.label}[/bold]")

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
            console.print(f"[bold]{field.label}[/bold]")

            vendor = responses.get("mdm_vendor")
                            
            if field.hints:
                console.print()
                common_hint = field.hints.get("common")

                if common_hint:
                    console.print(
                        f"[bold blue]Evidence[/bold blue]\n"
                        f"[italic]{common_hint}[/italic]"
                    )

                if vendor:

                    vendor_hint = field.hints.get(vendor)

                    if vendor_hint:
                        console.print(
                            f"[bold yellow]Location[/bold yellow]\n"
                            f"[italic]{vendor_hint}[/italic]"
                        )

            value = input("> ")

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
                    value = input(f"{field.label} (enter a number): ")

        responses[field.id] = value

    return ReviewContext(**responses)


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

    common_hint = None
    vendor_hint = None

    if vendor == Vendor.INTUNE and question.hints.intune:
        vendor_hint = question.hints.intune.strip()

    console.print()
    console.print(
        f"[bold cyan][{platform.value.upper()}] "
        f"Question {current}/{total}:[/bold cyan] "
        f"[bold]{question.question}[/bold]"
    )
    console.print()

    if common_hint:
        console.print(
            f"[bold blue]Evidence[/bold blue]\n"
            f"[italic]{common_hint.strip()}[/italic]"
        )

    if vendor_hint:
        console.print(
            f"[bold yellow]Location[/bold yellow]\n"
            f"[italic]{vendor_hint.strip()}[/italic]"
        )

    platform_hint = None

    if platform == Platform.IOS:
        platform_hint = question.hints.ios

    elif platform == Platform.ANDROID:
        platform_hint = question.hints.android

    if platform_hint:
        console.print()
        console.print(
            f"[bold cyan]Setting[/bold cyan]\n"
            f"[italic]{platform_hint.strip()}[/italic]"
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

    return QuestionResponse(
        finding_id=question.finding_id,
        platform=platform,
        answer=answer,
    )


def conduct_review(
    questions: list[Question],
    vendor: Vendor,
    platforms: list[Platform],
) -> list[QuestionResponse]:
    """
    Execute the assessment questionnaire.

    Questions are presented separately for each platform within
    the review scope, allowing Android and iOS controls to be
    assessed in dedicated sections. Shared controls are included
    within each platform review where applicable.

    Responses collected during the assessment are returned for
    subsequent finding generation and reporting.
    """

    responses = []

    for platform in platforms:

        console.print()
        console.print(
            f"[bold green]{platform.value.upper()} REVIEW[/bold green]"
        )

        platform_questions = [
            question
            for question in questions
            if (
                question.applies_to == Platform.BOTH
                or question.applies_to == platform
            )
        ]

        total = len(platform_questions)

        current_section = None

        for current, question in enumerate(platform_questions, start=1):

            if question.section != current_section:

                console.print()

                section_name = (question.section.replace("_", " ").title())
                console.print(f"[bold magenta]{section_name}[/bold magenta]")

                current_section = question.section

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
                    platform=response.platform,
                    title=question.finding_title,
                    description=question.description.strip(),
                    commentary=question.commentary.strip(),
                    solution=question.solution.strip(),
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

    The assessment workflow consists of scope selection, context
    collection, questionnaire execution, and results generation.
    The completed assessment results are returned for reporting
    and export.
    """

    platforms = select_platforms()

    context_fields = get_applicable_context_fields(
        load_context_fields(),
        platforms,
    )

    context = collect_context(context_fields)

    questions = get_applicable_questions(load_questions(), platforms)

    responses = conduct_review(
        questions,
        context.mdm_vendor,
        platforms,
    )

    return build_assessment_results(
        context=context,
        questions=questions,
        responses=responses,
    )