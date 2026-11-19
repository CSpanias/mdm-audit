"""SureFormat XML export for MDM findings."""

import xml.etree.ElementTree as ET
from pathlib import Path

from mdm_audit.ui import console

FINDING_MAP = {
    "mdm-audit": "SC-2142",
    "mdm-unsupported-os-version": "SC-9545",
    "mdm-jailbroken-rooted-devices": "SC-9546",
    "mdm-inactive-device-compliance-policy": "SC-9547",
    "mdm-remote-wipe-disabled": "SC-9548",
    "mdm-unsafe-failed-login-wipe-threshold": "SC-9549",
    "mdm-developer-mode-enabled": "SC-9550",
    "mdm-unrestricted-ios-data-sharing": "SC-9551",
    "mdm-usb-accessories-allowed-while-locked": "SC-9552",
    "mdm-ios-host-pairing-allowed": "SC-9553",
    "mdm-unencrypted-android-devices": "SC-9554",
    "mdm-unencrypted-sd-cards": "SC-9555",
    "mdm-usb-debugging-enabled": "SC-9556",
    "mdm-biometric-authentication-disabled": "SC-9557",
    "mdm-numeric-only-passwords-allowed": "SC-9558",
    "mdm-android-swipe-pattern-passwords-allowed": "SC-9559",
    "mdm-weak-minimum-password-length": "SC-9560",
    "mdm-untrusted-app-installation-allowed": "SC-9561",
    "mdm-unrestricted-app-store-access": "SC-9562",
    "mdm-default-system-apps-not-controlled": "SC-9563",
    "intune-unsupported-os-version": "SC-9545",
    "intune-jailbroken-rooted-devices": "SC-9546",
    "intune-remote-wipe-disabled": "SC-9548",
    "intune-unsafe-failed-login-wipe-threshold": "SC-9549",
    "intune-developer-mode-enabled": "SC-9550",
    "intune-usb-accessories-allowed-while-locked": "SC-9552",
    "intune-ios-host-pairing-allowed": "SC-9553",
    "intune-unencrypted-android-devices": "SC-9554",
    "intune-biometric-authentication-disabled": "SC-9557",
    "intune-numeric-only-passwords-allowed-configuration": "SC-9558",
    "intune-numeric-only-passwords-allowed-compliance": "SC-9558",
    "intune-weak-minimum-password-length-configuration": "SC-9560",
    "intune-weak-minimum-password-length-compliance": "SC-9560",
    "intune-unrestricted-app-store-access": "SC-9562",
}


def export_sureformat(
    findings: list[dict], platform: str, hostname: str, output_file: str
) -> None:
    """Write mapped findings applicable to one mobile platform."""
    root = ET.Element("items", source="SureFormat", version="1.0.0")
    item = ET.SubElement(root, "item", ipaddress="", hostname=hostname)
    services = ET.SubElement(item, "services")
    service = ET.SubElement(services, "service", name="", port="", protocol="tcp")
    vulnerabilities = ET.SubElement(service, "vulnerabilities")

    for finding in findings:
        if platform not in finding.get("platforms", []):
            continue
        finding_id = finding["id"]
        if finding_id == "intune-unrestricted-data-sharing" and platform == "ios":
            vulnerability_id = "SC-9551"
        else:
            vulnerability_id = FINDING_MAP.get(finding_id)
        if not vulnerability_id:
            console.print(
                f"[yellow][!][/yellow] No SureFormat mapping found for {platform} finding: "
                f"{finding_id}"
            )
            continue
        vulnerability = ET.SubElement(vulnerabilities, "vulnerability", id=vulnerability_id)
        ET.SubElement(vulnerability, "information").text = finding["description"]

    tree = ET.ElementTree(root)
    ET.indent(tree, space="    ")
    tree.write(Path(output_file), encoding="utf-8", xml_declaration=False)
