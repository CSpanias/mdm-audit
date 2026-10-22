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
    Return all questions applicable to the selected platforms.

    Shared controls are included once regardless of how many
    platforms are selected.

    Args:
        questions:
            Complete set of available audit questions.

        platforms:
            Platforms selected for review.

    Returns:
        Ordered list of questions to present to the assessor.
    """

    applicable_questions = []

    for question in questions:
        if question.applies_to == Platform.BOTH:
            applicable_questions.append(question)

        elif question.applies_to in platforms:
            applicable_questions.append(question)

    return sorted(applicable_questions, key=lambda q: q.id)


def get_applicable_context_fields(
    fields: list[ContextField],
    platforms: list[Platform],
) -> list[ContextField]:
    """
    Return all context fields applicable to the selected platforms.

    Args:
        fields:
            Complete set of context fields.

        platforms:
            Platforms selected for review.

    Returns:
        Ordered list of context fields to collect.
    """

    applicable_fields = []

    for field in fields:
        if any(platform in field.platforms for platform in platforms):
            applicable_fields.append(field)

    return sorted(applicable_fields, key=lambda field: field.order)


def select_platforms() -> list[Platform]:
    """
    Prompt the assessor to select the scope of the review.
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
    Collect assessment context information.
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
    platforms: list[Platform],
    current: int,
    total: int,
) -> list[QuestionResponse]:
    """
    Present a question to the assessor and record one or more
    responses.
    """

    common_hint = question.hints.common

    vendor_map = {
        Vendor.INTUNE: question.hints.intune,
        Vendor.JAMF: question.hints.jamf,
        Vendor.WORKSPACE_ONE: question.hints.workspace_one,
        Vendor.GOOGLE_ENDPOINT: question.hints.google_endpoint,
    }

    vendor_hint = vendor_map.get(vendor)

    if question.applies_to == Platform.BOTH:
        question_platforms = platforms
    else:
        question_platforms = [question.applies_to]

    console.print()
    console.print(
        f"[bold cyan]Question {current}/{total}:[/bold cyan] "
        f"[bold]{question.question}[/bold]"
    )
    console.print()

    if common_hint:
        console.print(
            f"[bold blue]Evidence[/bold blue]\n"
            f"[italic]{common_hint}[/italic]"
        )

    if vendor_hint:
        console.print(
            f"[bold yellow]Location[/bold yellow]\n"
            f"[italic]{vendor_hint}[/italic]"
        )

    responses = []

    for platform in question_platforms:
        console.print(f"[bold]{platform.value.upper()}[/bold]")

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
                    console.print(
                        "[red]Invalid selection.[/red]"
                    )

        responses.append(
            QuestionResponse(
                question_id=question.id,
                platform=platform,
                answer=answer,
            )
        )

    return responses


def conduct_review(
    questions: list[Question],
    vendor: Vendor,
    platforms: list[Platform],
) -> list[QuestionResponse]:
    """
    Execute the assessment question set.
    """

    responses = []

    total = len(questions)

    for current, question in enumerate(
        questions,
        start=1,
    ):
        question_responses = ask_question(
            question,
            vendor,
            platforms,
            current,
            total,
        )

        responses.extend(question_responses)

    return responses


def generate_findings(
    questions: list[Question],
    responses: list[QuestionResponse],
) -> list[Finding]:
    """
    Generate finding records for non-compliant controls.
    """

    findings = []

    questions_by_id = {
        question.id: question
        for question in questions
    }

    for response in responses:
        question = questions_by_id[response.question_id]

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
    Generate positive observations for compliant controls.
    """

    positives = []

    questions_by_id = {
        question.id: question
        for question in questions
    }

    for response in responses:
        question = questions_by_id[response.question_id]

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