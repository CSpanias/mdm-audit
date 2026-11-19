import json
import os
import tempfile
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

from mdm_audit import cli
from mdm_audit.exporters.sureformat import export_sureformat
from mdm_audit.models import AssessmentResults, Finding, Platform, ReviewContext, Vendor


def finding(finding_id, platform, description):
    return Finding(
        finding_id=finding_id, platform=platform, title=finding_id,
        theme="Security", commentary_group="Controls", section="configuration",
        description=description, commentary="", solution="",
    )


def sample_results():
    return AssessmentResults(
        context=ReviewContext(
            platforms="iOS and Android", client_name="Example",
            mdm_vendor=Vendor.INTUNE, mdm_version="1",
            ios_policy_count=0, android_policy_count=1,
        ),
        findings=[
            finding("intune-unsupported-os-version", Platform.IOS, "Old <OS> & devices"),
            finding("intune-unsupported-os-version", Platform.ANDROID, "Old <OS> & devices"),
            finding("intune-unrestricted-data-sharing", Platform.IOS, "Sharing"),
            finding("intune-unrestricted-data-sharing", Platform.ANDROID, "Sharing"),
            finding("intune-developer-mode-enabled", Platform.ANDROID, "Developer mode"),
            finding("intune-inactive-device-clean-up-rule", Platform.IOS, "Cleanup"),
        ],
    )


class SureFormatTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=os.environ["TEMP"])
        self.old_cwd = os.getcwd()
        os.chdir(self.directory.name)
        self.addCleanup(self.directory.cleanup)
        self.addCleanup(os.chdir, self.old_cwd)

    def test_cli_writes_separate_platform_exports(self):
        with patch("sys.argv", ["mdm-audit", "--csacyber"]), \
             patch.object(cli, "run_assessment", return_value=sample_results()), \
             patch("builtins.input", side_effect=["", "ios_2026", "android_2026"]) as prompt, \
             patch.object(cli, "export_markdown") as markdown, \
             patch("mdm_audit.exporters.sureformat.console.print") as warning:
            cli.main()
        self.assertEqual(prompt.call_count, 3)
        expected = {
            "ios": ("ios_2026", ["SC-2142", "SC-9545", "SC-9551"]),
            "android": ("android_2026", ["SC-2142", "SC-9545", "SC-9550"]),
        }
        for platform, (hostname, ids) in expected.items():
            root = ET.parse(f"mdm-findings-{platform}.xml").getroot()
            item = root.find("item")
            service = item.find("./services/service")
            findings = service.findall("./vulnerabilities/vulnerability")
            self.assertEqual(root.attrib, {"source": "SureFormat", "version": "1.0.0"})
            self.assertEqual(item.attrib, {"ipaddress": "", "hostname": hostname})
            self.assertEqual(service.attrib, {"name": "", "port": "", "protocol": "tcp"})
            self.assertEqual([f.attrib["id"] for f in findings], ids)
            self.assertEqual(findings[1].findtext("information"), "Old <OS> & devices")
        warnings = " ".join(str(call) for call in warning.call_args_list)
        self.assertIn("intune-inactive-device-clean-up-rule", warnings)
        self.assertIn("android finding: intune-unrestricted-data-sharing", warnings)
        self.assertFalse(os.path.exists("mdm-findings.json"))
        with open("mdm-notes.json", encoding="utf-8") as file:
            self.assertEqual(json.load(file), {"responses": []})
        markdown.assert_called_once()

    def test_default_cli_keeps_generic_json_and_does_not_prompt(self):
        with patch("sys.argv", ["mdm-audit"]), \
             patch.object(cli, "run_assessment", return_value=sample_results()), \
             patch.object(cli, "export_markdown"), patch("builtins.input") as prompt:
            cli.main()
        prompt.assert_not_called()
        with open("mdm-findings.json", encoding="utf-8") as file:
            findings = json.load(file)["findings"]
        self.assertEqual(findings[0]["platforms"], ["ios", "android"])
        self.assertEqual(findings[1]["platforms"], ["android", "ios"])
        self.assertFalse(os.path.exists("mdm-findings-ios.xml"))

    def test_single_platform_prompts_once(self):
        results = sample_results()
        results.context.platforms = "Android only"
        results.context.ios_policy_count = None
        results.findings = [f for f in results.findings if f.platform == Platform.ANDROID]
        with patch("sys.argv", ["mdm-audit", "--csacyber"]), \
             patch.object(cli, "run_assessment", return_value=results), \
             patch("builtins.input", return_value="android") as prompt, \
             patch.object(cli, "export_markdown"):
            cli.main()
        prompt.assert_called_once()
        self.assertFalse(os.path.exists("mdm-findings-ios.xml"))
        self.assertTrue(os.path.exists("mdm-findings-android.xml"))

    def test_interrupted_hostname_prompt_preserves_assessment_notes(self):
        with patch("sys.argv", ["mdm-audit", "--csacyber"]), \
             patch.object(cli, "run_assessment", return_value=sample_results()), \
             patch("builtins.input", side_effect=EOFError), \
             patch.object(cli, "export_markdown") as markdown:
            with self.assertRaises(EOFError):
                cli.main()
        markdown.assert_called_once()
        with open("mdm-notes.json", encoding="utf-8") as file:
            self.assertEqual(json.load(file), {"responses": []})
        self.assertFalse(os.path.exists("mdm-findings-ios.xml"))

    def test_separate_configuration_and_compliance_findings_are_preserved(self):
        findings = [
            {"id": "intune-weak-minimum-password-length-configuration",
             "description": "Configuration", "platforms": ["ios"]},
            {"id": "intune-weak-minimum-password-length-compliance",
             "description": "Compliance", "platforms": ["ios"]},
        ]
        export_sureformat(findings, "ios", "ios_2026", "test.xml")
        vulnerabilities = ET.parse("test.xml").getroot().findall(".//vulnerability")
        self.assertEqual([v.attrib["id"] for v in vulnerabilities], ["SC-9560", "SC-9560"])
        self.assertEqual(
            [v.findtext("information") for v in vulnerabilities],
            ["Configuration", "Compliance"],
        )


if __name__ == "__main__":
    unittest.main()
