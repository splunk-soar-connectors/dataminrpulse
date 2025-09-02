# File: dataminrpulse_view.py
#
# Copyright (c) 2023-2025 Dataminr
#
# This unpublished material is proprietary to Dataminr.
# All rights reserved. The methods and
# techniques described herein are considered trade secrets
# and/or confidential. Reproduction or distribution, in whole
# or in part, is forbidden except by express written permission
# of Dataminr.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.

from datetime import datetime
import re


def _format_timestamp(timestamp_str):
    """
    Convert ISO timestamp to user-friendly format.
    
    Args:
        timestamp_str (str): ISO timestamp string like "2025-08-27T09:06:47.124Z"
        
    Returns:
        str: Formatted timestamp like "8:56 PM Sep 1, 2025" or original string if parsing fails
    """
    if not timestamp_str:
        return timestamp_str
    
    try:
        # Handle different ISO timestamp formats
        # Remove microseconds if present and handle Z timezone
        clean_timestamp = re.sub(r'\.\d+Z?$', '', timestamp_str.replace('Z', '+00:00'))
        
        # Parse the timestamp
        if '+' in clean_timestamp or clean_timestamp.endswith('Z'):
            # Handle timezone-aware timestamps
            dt = datetime.fromisoformat(clean_timestamp.replace('Z', '+00:00'))
        else:
            # Handle naive timestamps
            dt = datetime.fromisoformat(clean_timestamp)
        
        # Format to desired output: "8:56 PM Sep 1, 2025"
        return dt.strftime("%I:%M %p %b %d, %Y").lstrip('0')
    except (ValueError, TypeError):
        # Return original string if parsing fails
        return timestamp_str


def _enrich_alert_timestamps(alert_data):
    """
    Format timestamps in alert data to user-friendly format.
    
    Args:
        alert_data (dict): Alert data containing timestamps
        
    Returns:
        dict: Alert data with formatted timestamps
    """
    # Format main alert timestamp
    if alert_data.get("alertTimestamp"):
        alert_data["alertTimestamp"] = _format_timestamp(alert_data["alertTimestamp"])
    
    return alert_data

def _enrich_vulnerability_cvss_scores(alert_data):
    """
    Enrich vulnerability metadata with CVSS scores from discoveredEntities when missing.
    
    Args:
        alert_data (dict): Alert data containing metadata and intelAgents
        
    Returns:
        dict: Alert data with enriched vulnerability CVSS scores
    """
    # Check if we have the necessary data structures
    if not alert_data.get("metadata", []):
        return alert_data
    if not alert_data.get("metadata", {})[0].get("cyber", {}).get("vulnerabilities"):
        return alert_data
    
    vulnerabilities = alert_data["metadata"][0]["cyber"]["vulnerabilities"]
    discovered_entities = []
    
    # Extract all discovered entities from intel agents
    if alert_data.get("intelAgents"):
        for agent in alert_data["intelAgents"]:
            if agent.get("discoveredEntities"):
                discovered_entities.extend(agent["discoveredEntities"])
    
    # Create a lookup dictionary for discovered entities by name
    entity_lookup = {}
    for entity in discovered_entities:
        if entity.get("name") and entity.get("cvss"):
            entity_lookup[entity["name"]] = entity["cvss"]
    
    # Enrich vulnerabilities with CVSS scores from discovered entities
    for vuln in vulnerabilities:
        # If CVSS score is missing or empty in metadata
        if not vuln.get("cvss"):
            vuln_id = vuln.get("id")
            if vuln_id and vuln_id in entity_lookup:
                # Use CVSS score from discovered entities
                vuln["cvss"] = entity_lookup[vuln_id]
                vuln["cvss_source"] = "discoveredEntities"  # Track the source
            else:
                # Ensure we have a fallback value
                vuln["cvss"] = None
                vuln["cvss_source"] = "none"
        else:
            vuln["cvss_source"] = "metadata"
    
    return alert_data


def _get_alerts_result(provides, result):
    ctx_result = {}
    param = result.get_param()
    data = result.get_data()
    status = result.get_status()
    summary = result.get_summary()

    ctx_result["status"] = status
    ctx_result["param"] = param
    ctx_result["summary"] = summary
    if data:
        if provides == "get alert details":
            # Enrich each alert with CVSS score fallback logic
            enriched_data = []
            for alert_data in data:
                enriched_alert = _enrich_vulnerability_cvss_scores(alert_data)
                enriched_alert = _enrich_alert_timestamps(enriched_alert)
                enriched_data.append(enriched_alert)
            ctx_result["data"] = enriched_data
        else:
            ctx_result["data"] = data

    return ctx_result


def _get_api_version_from_results(all_app_runs):
    """Extract API version from action results or summary."""
    for summary, action_results in all_app_runs:
        for result in action_results:
            # Try to get API version from summary first
            result_summary = result.get_summary()
            if result_summary and "api_version_used" in result_summary:
                return result_summary["api_version_used"]
            
            # Try to get API version from data
            data = result.get_data()
            if data:
                for data_item in data:
                    if isinstance(data_item, dict) and "api_version" in data_item:
                        return data_item["api_version"]
    
    # Default to v3 if not found
    return "v3"


def _get_template_for_action(action_name, api_version):
    """Get the appropriate HTML template based on action and API version."""
    template_mapping = {
        "get alerts": {
            "v3": "dataminrpulse_get_alerts.html",
            "v4": "dataminrpulse_get_alerts_v4.html"
        },
        "get lists": {
            "v3": "dataminrpulse_get_lists.html",
            "v4": "dataminrpulse_get_lists_v4.html"
        },
        "get alert details": {
            "v3": "dataminrpulse_get_alert_details_v4.html",
            "v4": "dataminrpulse_get_alert_details_v4.html"
        }
    }
    
    # Get template for the specific version, fallback to v3 if not found
    action_templates = template_mapping.get(action_name, {})
    return action_templates.get(api_version, action_templates.get("v3"))


def display_alerts(provides, all_app_runs, context):
    context["results"] = results = []

    for summary, action_results in all_app_runs:
        for result in action_results:
            get_alerts_result = _get_alerts_result(provides, result)
            if not get_alerts_result:
                continue
            results.append(get_alerts_result)

    # Get API version from results
    api_version = _get_api_version_from_results(all_app_runs)
    
    # Add API version to context for use in templates
    context["api_version"] = api_version
    
    # Return appropriate template based on action and API version
    return _get_template_for_action(provides, api_version)
