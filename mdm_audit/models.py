
"""
Core data models used throughout the MDM Audit application.

This module defines the strongly-typed data structures that represent:

- Assessment questions
- Review context collected from the client
- Assessor responses
- Audit findings
- Positive observations
- Final assessment results

The models are implemented using Pydantic and provide validation for
data loaded from YAML files and generated during the audit workflow.

These models form the contract between the review engine and all
exporters, ensuring a consistent and predictable data structure
throughout the application.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Platform(str, Enum):
    """
    Supported device platforms.

    Used to determine which questions, context fields, findings,
    and reports apply to a given assessment.

    Values:
        IOS: Apple iOS devices.
        ANDROID: Android devices.
        BOTH: Shared controls applicable to both platforms.
    """

    IOS = "ios"
    ANDROID = "android"
    BOTH = "both"


class Vendor(str, Enum):
    """
    Supported Mobile Device Management (MDM) vendors.

    Used for displaying vendor-specific navigation hints
    and generating platform-specific preparation guides.

    The values correspond to the normalised vendor names
    used throughout the application.
    """
    INTUNE = "Microsoft Intune"
    OTHER = "Other"


class AuditAnswer(str, Enum):
    """
    Possible assessment outcomes recorded by the assessor.

    COMPLIANT:
        The control is implemented as expected.

    NON_COMPLIANT:
        The control is missing, disabled, or implemented
        incorrectly.

    NOT_APPLICABLE:
        The control does not apply to the assessed
        environment.

    UNKNOWN:
        The assessor was unable to determine the status
        of the control during the review.
    """
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


class ContextField(BaseModel):
    """
    Defines a contextual information field collected before
    the assessment begins.

    Context fields describe metadata about the client
    environment such as:

    - Client name
    - MDM platform
    - MDM version
    - Device counts
    - Policy counts
    - Minimum supported operating system versions

    Fields are loaded dynamically from context_fields.yaml.
    """
    id: str

    label: str
    type: str

    required: bool = True

    platforms: list[Platform]

    options: list[str] | None = None

    hints: dict[str, str] | None = None


class ReviewContext(BaseModel):
    """
    Stores environment information gathered during the
    assessment context collection phase.

    This information is used within exported reports,
    preparation guides, and XML outputs to provide
    background information about the reviewed environment.

    A single ReviewContext exists for each assessment.
    """

    platforms: str
    client_name: str

    mdm_vendor: Vendor
    mdm_version: str

    ios_policy_count: Optional[int] = None
    android_policy_count: Optional[int] = None

    minimum_ios_version: Optional[str] = None
    minimum_android_version: Optional[str] = None

    ios_device_count: Optional[int] = None
    android_device_count: Optional[int] = None


class QuestionResponse(BaseModel):
    """
    Represents the assessor's response to a single question.

    Responses are recorded regardless of whether the
    control is compliant or non-compliant and provide
    a complete audit trail of the assessment.

    These records form the basis for generating findings,
    positive observations, reports, and future analytics.
    """

    finding_id: str

    platform: Platform

    answer: AuditAnswer

    notes: str | None = None


class VendorHints(BaseModel):
    """
    Vendor-specific navigation hints used to guide
    the assessor to the relevant configuration within
    each supported MDM platform.
    """

    common: str | None = None
    ios: str | None = None
    android: str | None = None
    intune: str | None = None


class Question(BaseModel):
    """
    Represents a single audit question loaded from questions.yaml.

    Each question contains:
    - The review question presented to the assessor
    - Expected compliance state
    - Vulnerability mapping
    - Positive observation text
    - Remediation guidance
    - Vendor-specific navigation hints

    Questions are data-driven and should be maintained
    exclusively within the YAML configuration rather than
    hard-coded within the application.
    """
    
    applies_to: Platform

    finding_id: str
    finding_title: str
    section: str

    expected_answer: AuditAnswer

    question: str

    description: str
    commentary: str
    solution: str
    positive: str

    good_value: str
    bad_value: str

    hints: VendorHints


class Finding(BaseModel):
    """
    Represents a non-compliant control identified during
    the assessment.

    Findings are created when the assessor's response does
    not match the expected compliant state defined by the
    question.

    Each finding contains:
    - Vulnerability identifier
    - Platform
    - Description of the issue
    - Recommended remediation
    """
    
    finding_id: str
    platform: Platform
    title: str
    description: str
    commentary: str
    solution: str


class PositiveObservation(BaseModel):
    """
    Represents a successfully implemented security control.

    Positive observations are generated when a control
    meets the expected compliance requirements and can
    be included within reports and executive summaries.

    These observations help demonstrate security strengths
    alongside identified findings.
    """
    finding_id: str

    platform: Platform

    text: str


class AssessmentResults(BaseModel):
    """
    Represents the complete outcome of an MDM assessment.

    This model acts as the central object exchanged between
    the review engine and exporters.

    It contains:

    - Review context
    - Recorded responses
    - Findings
    - Positive observations

    Exporters should consume this model instead of directly
    accessing the review engine or raw YAML data.
    """
    context: ReviewContext

    findings: list[Finding] = Field(default_factory=list)

    positives: list[PositiveObservation] = Field(default_factory=list)

    responses: list[QuestionResponse] = Field(default_factory=list)