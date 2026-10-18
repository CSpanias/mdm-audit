"""
Command-line entry point for the MDM Audit application.

This module provides the interactive assessor experience
and is responsible for:

- Collecting assessment context
- Selecting platform scope
- Executing the review workflow
- Invoking exporters
- Displaying progress and status messages

The CLI should remain lightweight and delegate business
logic to the review engine.
"""