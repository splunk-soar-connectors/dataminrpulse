# File: dataminrpulse_view.py
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


def _get_alerts_result(result):

    ctx_result = {}
    param = result.get_param()
    data = result.get_data()
    status = result.get_status()

    ctx_result['status'] = status
    ctx_result['param'] = param
    if (data):
        ctx_result['data'] = data

    return ctx_result


def display_alerts(provides, all_app_runs, context):

    context['results'] = results = []

    for summary, action_results in all_app_runs:
        for result in action_results:
            get_alerts_result = _get_alerts_result(result)
            if not get_alerts_result:
                continue
            results.append(get_alerts_result)

    if provides == 'get alerts':
        return 'dataminrpulse_get_alerts.html'

    if provides == 'get lists':
        return 'dataminrpulse_get_lists.html'

    if provides == 'get related alerts':
        return 'dataminrpulse_get_related_alerts.html'
