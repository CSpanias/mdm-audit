"""
Reporting and categorisation constants.
"""

NUMBER_WORDS = {
    0: "no",
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
}


COMMENTARY_ORDER = [
    "Device Lifecycle and Compliance",
    "Authentication and Access Control",
    "Data Protection",
    "Device Security and Hardening",
    "Application Governance",
]


COMMENTARY_INTROS = {
    "Device Lifecycle and Compliance":
        "The assessment identified that ",

    "Authentication and Access Control":
        "Specific observations included that ",

    "Data Protection":
        "The review noted that ",

    "Device Security and Hardening":
        "Further observations identified that ",

    "Application Governance":
        "The assessment observed that ",
}


COMMENTARY_SUMMARIES = {
    "Device Lifecycle and Compliance": (
        "Weaknesses were identified affecting device "
        "lifecycle management, compliance monitoring, "
        "and the organisation's ability to maintain "
        "visibility over managed devices."
    ),

    "Authentication and Access Control": (
        "Opportunities for improvement were identified "
        "within the controls used to authenticate users "
        "and restrict access to managed devices and "
        "corporate resources."
    ),

    "Data Protection": (
        "Several observations related to the protection "
        "of corporate information stored and accessed "
        "on managed devices."
    ),

    "Device Security and Hardening": (
        "The review highlighted weaknesses in a number "
        "of device hardening controls intended to reduce "
        "the attack surface of managed devices."
    ),

    "Application Governance": (
        "Further observations related to application "
        "governance controls intended to restrict the "
        "installation and use of unapproved software."
    ),
}


COVERAGE_TEXT = {
    "Device Lifecycle and Compliance": {
        "both": (
            "Together, these observations reduce assurance that "
            "managed devices remain visible, compliant, and subject "
            "to ongoing organisational oversight."
        ),
        "configuration": (
            "The findings suggest that lifecycle requirements were "
            "not being consistently enforced across the managed "
            "device estate."
        ),
        "compliance": (
            "The assessment highlighted gaps in the processes used "
            "to monitor device compliance and security status."
        ),
    },

    "Authentication and Access Control": {
        "both": (
            "Collectively, these observations indicate that device "
            "authentication requirements were not consistently "
            "enforced or validated across managed devices."
        ),
        "configuration": (
            "The review identified gaps in the controls used to "
            "enforce authentication and access restrictions on "
            "managed devices."
        ),
        "compliance": (
            "The observed weaknesses suggest that devices may not "
            "have been effectively validated against authentication "
            "requirements before access was granted."
        ),
    },

    "Data Protection": {
        "both": (
            "Taken together, the identified issues reduce assurance "
            "that corporate information remains appropriately "
            "protected throughout its lifecycle."
        ),
        "configuration": (
            "Several safeguards intended to prevent the unauthorised "
            "disclosure or transfer of corporate information were "
            "not fully enforced."
        ),
        "compliance": (
            "The control gaps identified during the review suggest "
            "that data protection requirements were not being "
            "consistently validated."
        ),
    },

    "Device Security and Hardening": {
        "both": (
            "Overall, the observations increase the likelihood that "
            "insecure devices or configurations could operate within "
            "the managed environment."
        ),
        "configuration": (
            "The assessment highlighted opportunities to strengthen "
            "the controls intended to reduce the attack surface of "
            "managed devices."
        ),
        "compliance": (
            "Current validation mechanisms may not provide sufficient "
            "assurance that insecure devices are identified and "
            "restricted."
        ),
    },

    "Application Governance": {
        "both": (
            "From a governance perspective, the observations reduce "
            "assurance that installed software aligns with "
            "organisational security requirements."
        ),
        "configuration": (
            "The review found that application governance "
            "requirements were not being consistently enforced "
            "through device policy."
        ),
        "compliance": (
            "The findings indicate that application governance "
            "requirements were not being consistently assessed "
            "through compliance controls."
        ),
    },
}


THEME_DISPLAY = {
    "Access Control":
        "authentication and access control",

    "Application Control":
        "application governance",

    "Data Protection":
        "data protection",

    "Device Hardening":
        "device hardening",

    "Patch and Lifecycle Management":
        "device lifecycle management",
}


REMEDIATIONS = {
    "inactive_devices": (
        "Establish inactivity thresholds to automatically mark devices "
        "as non-compliant and revoke access until they reconnect."
    ),

    "screen_lock_timeout": (
        "Reduce screen lock timeouts to ensure unattended devices are "
        "automatically secured after an appropriate period of inactivity."
    ),

    "screen_lock_reauthentication": (
        "Strengthen device access controls by requiring re-authentication "
        "shortly after screen lock events and periods of inactivity."
    ),

    "password_history": (
        "Implement password history controls to prevent the reuse of "
        "previously used credentials."
    ),

    "developer_mode": (
        "Remove access to Developer Mode on managed devices unless a "
        "documented business requirement exists."
    ),

    "host_pairing": (
        "Prevent managed devices from establishing trust relationships "
        "with unauthorised host computers."
    ),

    "usb_restricted_mode": (
        "Apply USB Restricted Mode to limit communication with external "
        "accessories while devices remain locked."
    ),

    "failed_login_wipe": (
        "Introduce automatic device wipe protections following a defined "
        "number of failed authentication attempts."
    ),

    "jailbreak_root_detection": (
        "Detect and block jailbroken or rooted devices from accessing "
        "organisational resources."
    ),

    "minimum_password_length": (
        "Increase minimum password length requirements in line with "
        "organisational security standards."
    ),

    "password_required": (
        "Mandate device authentication through passcodes, PINs, or "
        "passwords before access to corporate resources is permitted."
    ),

    "remote_wipe": (
        "Maintain remote wipe functionality and supporting operational "
        "procedures for lost, stolen, or retired devices."
    ),

    "managed_data_sharing": (
        "Apply Managed Open-In and data-sharing restrictions to prevent "
        "corporate information being transferred to unmanaged applications."
    ),

    "device_encryption": (
        "Protect corporate data through mandatory device encryption and "
        "deny access from non-compliant devices."
    ),

    "biometrics": (
        "Allow approved biometric authentication methods to improve "
        "usability while maintaining strong authentication controls."
    ),

    "simple_passwords": (
        "Strengthen password complexity requirements by prohibiting "
        "simple or easily guessed passwords."
    ),

    "alphanumeric_passwords": (
        "Adopt alphanumeric password requirements to improve resistance "
        "to guessing and brute-force attacks."
    ),

    "app_store_access": (
        "Limit software installation to approved applications and "
        "managed application catalogues."
    ),

    "external_storage": (
        "Control the use of removable and external storage through "
        "appropriate technical restrictions and security safeguards."
    ),

    "screen_capture": (
        "Restrict screenshot and screen recording functionality where "
        "sensitive information may be exposed."
    ),

    "supported_os_version": (
        "Require devices to run operating system versions that remain "
        "supported and continue to receive vendor security updates."
    ),
}


REFERENCES = {
    "Generic": {
        "NCSC Device Security Guidance":
            "https://www.ncsc.gov.uk/collection/device-security-guidance/getting-ready/mobile-device-management",
    },

    "Microsoft Intune": {
        "Microsoft Intune Best Practices":
            "https://techcommunity.microsoft.com/blog/intunecustomersuccess/best-practices-for-securing-microsoft-intune/4502117",
    },

    "Jamf Pro": {
        "Jamf Security Foundation":
            "https://www.jamf.com/blog/mobile-device-management-security-foundation/",
    },

    "Omnissa Workspace ONE": {
        "Workspace ONE Configuration Guidance":
            "https://techzone.omnissa.com/mobile-management#overview",
    },

    "Google Endpoint Management": {
        "Google Device Management Security Checklist":
            "https://knowledge.workspace.google.com/admin/devices/device-management-security-checklist",
    },
}