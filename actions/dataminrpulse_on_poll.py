# File: dataminrpulse_on_poll.py
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


class OnPollAction(BaseAction):
    """Class to handle on poll action."""

    def execute(self):
        """Execute the on poll action."""
        self._connector.save_progress("Executing Polling")

        list_id = self._connector.util._get_list_id(self._action_result)
        query = self._connector.config.get("query", None)

        if not (list_id or query):
            return self._action_result.set_status(
                phantom.APP_ERROR,
                "Please provide either valid 'list names' or 'query' in the asset configuration parameter"
            )

        list_id_in_state_file = self._connector.state.get(consts.DATAMINRPULSE_STATE_LIST_ID_VALUE, None)
        query_in_state_file = self._connector.state.get(consts.DATAMINRPULSE_STATE_QUERY_VALUE, None)

        if (list_id_in_state_file != list_id) or (query_in_state_file != query):
            self._connector.is_state_updated = True

            # Reset values of from and to on changing configuration
            self._connector.state.pop(consts.DATAMINRPULSE_STATE_FROM_VALUE, None)
            self._connector.state.pop(consts.DATAMINRPULSE_STATE_TO_VALUE, None)

            # Storing updated configured values in state file
            self._connector.state[consts.DATAMINRPULSE_STATE_LIST_ID_VALUE] = list_id
            self._connector.state[consts.DATAMINRPULSE_STATE_QUERY_VALUE] = query

        num = self._connector.config.get("page_size_for_polling", 40)
        ret_val, num = self._connector.util._validate_integer(self._action_result, num, "num", True)
        if phantom.is_fail(ret_val):
            return self._action_result.get_status()

        alert_type = self._connector.config.get("alert_type", "All")
        if alert_type not in consts.DATAMINRPULSE_ALERT_TYPE_VALUE:
            return self._action_result.set_status(phantom.APP_ERROR, consts.DATAMINRPULSE_ERROR_INVALID_PARAMETER_VALUE)

        # Prepare query parameters
        params = {
            "lists": list_id,
            "query": query,
            "num": num,
            "from": None,
            "to": None,
            "application": "splunk_soar",
            "application_version": f"{self._connector.get_product_version()}",
            "integration_version": f"{self._connector.get_app_json().get('app_version')}"
        }
        if not self._connector.is_poll_now() and self._connector.state.get(consts.DATAMINRPULSE_STATE_TO_VALUE, None):
            # To fetch new alerts, we assign to's value in from
            from_value = self._connector.state[consts.DATAMINRPULSE_STATE_TO_VALUE]
            params.update({"from": from_value})

        # Polling
        ret_val, response = self._connector.util._make_rest_call_helper(
            consts.DATAMINRPULSE_GET_ALERTS, self._action_result, params=params
        )
        if phantom.is_fail(ret_val):
            msg = self._action_result.get_message()
            if msg and (consts.DATAMINRPULSE_DECODE_FROM_ERROR in msg):
                self._connector.state.pop(consts.DATAMINRPULSE_STATE_TO_VALUE, None)
                self._connector.state.pop(consts.DATAMINRPULSE_STATE_FROM_VALUE, None)
                self._connector.debug_print("Error occurred with decoding 'from'. Reset 'from' and 'to' values from state file")
                self._connector.is_state_updated = True
            return self._action_result.get_status()

        alerts = []
        if alert_type != "All":
            for alert in response.get("data").get("alerts"):
                if alert_type == alert.get("alertType", {}).get("name", ""):
                    alerts.append(alert)
        else:
            alerts.extend(response.get("data").get("alerts", []))

        # Schedule Polling
        if not self._connector.is_poll_now():
            self._connector.is_state_updated = True
            to_value = response.get("data", {}).get("to", None)
            from_value = response.get("data", {}).get("from", None)

            if to_value:
                self._connector.state[consts.DATAMINRPULSE_STATE_TO_VALUE] = to_value

            if from_value:
                self._connector.state[consts.DATAMINRPULSE_STATE_FROM_VALUE] = from_value

        failed_alert_ids = 0
        total_alerts = len(alerts)

        self._connector.save_progress(f"Total alerts fetched: {total_alerts}")
        if not total_alerts:
            self._connector.debug_print("No alerts found")
            return self._action_result.set_status(phantom.APP_SUCCESS, consts.DATAMINRPULSE_ACTION_EMPTY_ALERTS)

        if self._connector.is_poll_now():
            self._connector.save_progress("Ingesting all possible artifacts (ignoring maximum artifacts value) for POLL NOW")

        for index, alert in enumerate(alerts):
            try:
                self._connector.send_progress("Processing alert # {} with Alert ID ending in: {}".format(index + 1, alert["alertId"][-10:]))
                ret_val = self._connector.util._process_alert_data(self._action_result, alert)
                if phantom.is_fail(ret_val):
                    failed_alert_ids += 1
                    self._connector.save_progress(
                        f"Error occurred while processing alert ID: {alert.get('alertId')}. {self._action_result.get_message()}")

            except Exception as e:
                failed_alert_ids += 1
                error_msg = self._connector.util._get_error_message_from_exception(e)
                self._connector.save_progress(f"Exception occurred while processing alert ID: {alert.get('alertId')}. {error_msg}")

        if failed_alert_ids == total_alerts:
            return self._action_result.set_status(phantom.APP_ERROR, "Error occurred while processing all the alert IDs")

        return self._action_result.set_status(phantom.APP_SUCCESS)
