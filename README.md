# MDM-Audit

A Python-based tool designed to streamline Mobile Device Management (MDM) security reviews.

Developed as an educational tool to accompany [Mobile Device Management Security Explained: Microsoft Intune](https://mollysec.com/posts/mdm-security-explained/). 

The generated outputs are intended to support formal security reviews and can be used as inputs into downstream reporting and governance tools.

```text
Configuration Review
        ↓
Structured Assessment
        ↓
Markdown Report + JSON Export
```

## Installation

### [UV](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer) (Method 1 - Recommended)

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install mdm-audit via UV
uv tool install git+https://github.com/CSpanias/mdm-audit

# Verify installation
mdm-audit -h

# Update
uv tool upgrade mdm-audit
```

### Development Installation

> Recommended for contributors and anyone modifying the source code.
>
> The editable installation (`-e`) allows local code changes to take effect immediately without reinstalling the package.

```bash
# Clone repository
git clone https://github.com/CSpanias/mdm-audit /opt/mdm-audit

# Move into the directory
cd /opt/mdm-audit

# Create virtual environment
uv venv

# Install editable package
uv pip install -e .

# Verify installation
python -m mdm_audit.cli
```

## Features

- Guided MDM assessment workflow
- Support for Intune-based iOS / iPadOS and Android reviews
- Markdown-formatted report generation
- JSON findings export
- JSON assessment response export
- YAML-driven assessment content

## Usage

Just launch the tool!

```bash
mdm-audit
```

## Requirements

- Python 3.11+
- UV (recommended)