# File: dataminrpulse_get_alerts.py
#
# Copyright (c) 2023-2024 Dataminr
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


import phantom.app as phantom

import dataminrpulse_consts as consts
from actions import BaseAction


class GetAlertsAction(BaseAction):
    """Class to handle get alerts action."""

    def execute(self):
        """Execute the get alerts action."""
        list_id = self._param.get("list_id", None)
        use_asset_configured_lists = self._param.get("use_asset_configured_lists", False)
        query = self._param.get("query", None)

        # Accepts comma-seperated list only
        if list_id:
            list_id = list_id.strip(",")
            list_id = str(list_id).replace(" ", "")

            if not list_id and use_asset_configured_lists:
                list_id = self._connector.util._get_list_id(self._action_result)
                if not (list_id or query):
                    return self._action_result.set_status(
                        phantom.APP_ERROR,
                        "Please provide either valid 'list names' in asset configuration parameter or 'query' in action parameter"
                    )

        elif use_asset_configured_lists:
            list_id = self._connector.util._get_list_id(self._action_result)
            if not (list_id or query):
                return self._action_result.set_status(
                    phantom.APP_ERROR,
                    "Please provide either valid 'list names' in asset configuration parameter or 'query' in action parameter"
                )

        from_value = self._param.get("from", None)
        to_value = self._param.get("to", None)

        if not (list_id or query):
            return self._action_result.set_status(phantom.APP_ERROR, "Please provide either 'list id' or 'query' action parameter")

        num = self._param.get("max_alerts", 40)
        ret_val, num = self._connector.util._validate_integer(self._action_result, num, "num", True)
        if phantom.is_fail(ret_val):
            return self._action_result.get_status()

        # Prepare query parameters
        params = {
            "lists": list_id,
            "query": query,
            "from": from_value,
            "to": to_value,
            "num": num,
            "application": "splunk_soar",
            "application_version": f"{self._connector.get_product_version()}",
            "integration_version": f"{self._connector.get_app_json().get('app_version')}"
        }

        # Make rest call to fetch the alerts
        ret_val, response = self._connector.util._make_rest_call_helper(
            consts.DATAMINRPULSE_GET_ALERTS, self._action_result, params=params
        )

        if phantom.is_fail(ret_val):
            return self._action_result.get_status()

        data = response.get("data", {})
        self._action_result.add_data(data)

        # Add summary
        self._action_result.update_summary({"total_alerts": len(data.get("alerts", []))})

        return self._action_result.set_status(phantom.APP_SUCCESS)
