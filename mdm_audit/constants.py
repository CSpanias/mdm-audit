"""
Reporting and categorisation constants.
"""

FINDING_THEMES = {
    "Patch and Lifecycle Management": {
        "mdm-unsupported-os-version",
        "mdm-inactive-device-compliance-policy",
    },

    "Device Hardening": {
        "mdm-jailbroken-rooted-devices",
        "mdm-developer-mode-enabled",
        "mdm-usb-debugging-enabled",
        "mdm-unencrypted-android-devices",
        "mdm-unencrypted-sd-cards",
    },

    "Access Control": {
        "mdm-biometric-authentication-disabled",
        "mdm-numeric-only-passwords-allowed",
        "mdm-android-swipe-pattern-passwords-allowed",
        "mdm-weak-minimum-password-length",
        "mdm-unsafe-failed-login-wipe-threshold",
    },

    "Data Protection": {
        "mdm-unrestricted-ios-data-sharing",
        "mdm-remote-wipe-disabled",
    },

    "Application Control": {
        "mdm-untrusted-app-installation-allowed",
        "mdm-unrestricted-app-store-access",
        "mdm-default-system-apps-not-controlled",
    },
}

COMMENTARY_GROUPS = {
    "Device Lifecycle and Compliance": {
        "mdm-unsupported-os-version",
        "mdm-inactive-device-compliance-policy",
        "mdm-remote-wipe-disabled",
        "mdm-unsafe-failed-login-wipe-threshold",
    },

    "Authentication and Access Control": {
        "mdm-biometric-authentication-disabled",
        "mdm-numeric-only-passwords-allowed",
        "mdm-android-swipe-pattern-passwords-allowed",
        "mdm-weak-minimum-password-length",
    },

    "Data Protection": {
        "mdm-unrestricted-ios-data-sharing",
        "mdm-unencrypted-android-devices",
        "mdm-unencrypted-sd-cards",
    },

    "Device Security and Hardening": {
        "mdm-jailbroken-rooted-devices",
        "mdm-developer-mode-enabled",
        "mdm-usb-debugging-enabled",
        "mdm-usb-accessories-allowed-while-locked",
        "mdm-ios-host-pairing-allowed",
    },

    "Application Governance": {
        "mdm-untrusted-app-installation-allowed",
        "mdm-unrestricted-app-store-access",
        "mdm-default-system-apps-not-controlled",
    },
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