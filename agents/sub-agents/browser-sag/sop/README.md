# BrowserSAG SOP

## Purpose
Standard operating procedure for BrowserSAG to handle web automation tasks, browser interactions, and web-based data collection across the Multi Agent Governance fleet.

## Prerequisites
- Active virtual environment (`python3 -m venv .venv && source .venv/bin/activate`).
- Updated dependencies (`pip install -r requirements.txt` or `uv sync`).
- Chrome DevTools MCP server configured and accessible.
- Playwright MCP server configured for browser automation.
- Valid target URLs and authentication credentials when required.

## Procedure — Execute Browser Task
1. **Triage**
   - Review the browser task request, confirm target URLs, authentication requirements, and expected outcomes.
   - Validate that target websites are accessible and comply with terms of service.
   - Notify OpsMAG and QAMAG of pending browser automation tasks.
2. **Prepare Environment**
   - Ensure Chrome DevTools MCP server is running and accessible.
   - Configure Playwright MCP server with appropriate browser settings (headless/headed mode).
   - Set up authentication tokens or credentials if required.
3. **Execute Browser Operations**
   - Navigate to target URLs using Playwright MCP server.
   - Perform required interactions (clicks, form fills, data extraction).
   - Capture screenshots or page content as needed.
   - Handle dynamic content and wait conditions appropriately.
4. **Data Collection & Processing**
   - Extract required data from web pages.
   - Validate data completeness and accuracy.
   - Store results in appropriate format for downstream processing.
5. **Cleanup & Reporting**
   - Close browser sessions and clean up resources.
   - Generate task completion report with results and any issues encountered.
   - Notify requesting agents of completion status.
6. **Monitor & Roll Back**
   - Track browser automation success rates and performance metrics.
   - If automation fails repeatedly, escalate to manual review and follow rollback procedures.

## Escalation Procedures
- For authentication failures: Contact OpsMAG for credential updates.
- For website access issues: Verify target availability and terms of service compliance.
- For automation failures: Review browser logs and consider alternative approaches.
- For data quality issues: Validate extraction logic and target page structure changes.
