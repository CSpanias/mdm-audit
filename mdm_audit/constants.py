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