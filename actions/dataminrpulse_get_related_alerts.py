# File: dataminrpulse_get_related_alerts.py
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


class GetRelatedAlertsAction(BaseAction):
    """Class to handle get related alerts action."""

    def execute(self):
        """Execute the get related alerts action."""
        params = {
            "id": self._param['alert_id'],
            "includeRoot": self._param.get('include_root', False)
        }

        status, response = self._connector.util._make_rest_call_helper(consts.DATAMINRPULSE_GET_RELATED_ALERTS, self._action_result, params=params)
        if phantom.is_fail(status):
            return self._action_result.get_status()

        for alerts in response:
            self._action_result.add_data(alerts)

        self._action_result.update_summary({'total_related_alerts': len(response)})

        return self._action_result.set_status(phantom.APP_SUCCESS)
