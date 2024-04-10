[comment]: # " File: README.md"
[comment]: # ""
[comment]: # "    Copyright (c) 2023-2024 Dataminr"
[comment]: # ""
[comment]: # "    This unpublished material is proprietary to Dataminr."
[comment]: # "    All rights reserved. The methods and"
[comment]: # "    techniques described herein are considered trade secrets"
[comment]: # "    and/or confidential. Reproduction or distribution, in whole"
[comment]: # "    or in part, is forbidden except by express written permission"
[comment]: # "    of Dataminr."
[comment]: # ""
[comment]: # "    Licensed under the Apache License, Version 2.0 (the 'License');"
[comment]: # "    you may not use this file except in compliance with the License."
[comment]: # "    You may obtain a copy of the License at"
[comment]: # ""
[comment]: # "        http://www.apache.org/licenses/LICENSE-2.0"
[comment]: # ""
[comment]: # "    Unless required by applicable law or agreed to in writing, software distributed under"
[comment]: # "    the License is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,"
[comment]: # "    either express or implied. See the License for the specific language governing permissions"
[comment]: # "    and limitations under the License."
[comment]: # ""
## Explanation of the Asset Configuration Parameters

The asset configuration parameters affect 'test connectivity' and some other actions of the
application. The parameters related to test connectivity action are Client ID and Client Secret.

-   **Client ID:** Client ID.
-   **Client Secret:** Client Secret.

## Explanation of the Actions' Parameters

-   ### Test Connectivity

    This action will check the status of the Dataminr Pulse API endpoint and test connectivity of
    Splunk SOAR to the Dataminr Pulse instance. It can be used to generate a new token.  
    The action validates the provided asset configuration parameters. Based on the response from the
    API call, the appropriate success and failure message will be displayed when the action gets
    executed.

-   ### On Poll

    This polling is to ingest the dynamic alerts of a particular watchlist that is configured on
    this asset. The user can provide the watchlist names to ingest the alerts from, or provide the
    query and set the pagesize for polling. The user can also filter the results of the alert
    response, based on alert type.  

    -   **Manual Polling (POLL NOW)**

          

        -   It will fetch the data when initiated, as per the corresponding asset configuration
            parameters. It does not store the last run context of the fetched data.

    -   **Schedule/Interval Polling**

          

        -   **Schedule Polling:** The ingestion action can be triggered at every specified time
            interval.
        -   **Interval Polling:** The ingestion action can be triggered at every time range
            interval.
        -   It will fetch the data every time, based on the stored context from the previous
            ingestion run. It stores the last run context of the fetched data. It starts fetching
            data based on the combination of the values of stored context for the previous ingestion
            run.
        -   **NOTE:** If the user changes the configuration related to 'list names' or 'query'
            parameter while the schedule/interval polling is running, then the next polling cycle
            will start fetching the latest data according to the updated configured parameters.

    <!-- -->

    -   **Action Parameter: List names**

          

        -   This parameter accepts comma-seperated names of the watchlist and it is required if the
            user does not use this query parameter. Example: Company Cyber Alerts, Supply Chain
            Partner Cyber Alerts
        -   If any one of the list names is invalid in the comma-separated string, the action will
            skip that list name and continue with the valid ones.  
        -   **NOTE:** The list names asset parameter is case-sensitive and the user must provide the
            exact case match of the watchlist

    -   **Action Parameter: Query**

          

        -   This parameter accepts the search value for all the watchlists and it is required if we
            do not use the list names parameter. Example: ("Test" AND "Application") OR ("text" AND
            "json")
        -   The query parameter is case-insensitive.
        -   **Note:** If the user provides a list name and query both, then the action will return
            queried alerts from that particular watchlist only.

        **NOTE:** For polling, either 'list names' or 'query' must be provided to ingest alerts.

    -   **Action Parameter: Page size for polling**

          

        -   This parameter allows the user to limit the number of alerts in the response. It expects
            a numeric value as an input.
        -   The default value is 40 for this parameter.

    -   **Action Parameter: Alert type**

          

        -   This parameter allows additional filtering above list names and query. When any of
            "Alert, Urgent, Flash" is selected, it just ingests the alerts with specific alert type
            from the alerts fetched by the API with configured pagesize. If "All" is selected, all
            the types of alerts will be ingested.
        -   **NOTE:** The severity of containers, Alert artifacts, and it's cyber artifacts is
            according to the alert type of the first ingested alert. If the alert type is not
            present in the API response of any alert, then by default the severity is set to
            'Alert'. If related alert artifacts are ingested in the same container and have
            different severity, then the higher severity level will be set for the respective
            container and the new Alert artifacts and its cyber artifacts will have the severity of
            it's alert only. Thus, the severity of already ingested container would update only when
            an alert of higher severity than the existing one is ingested in the same container.
        -   The priority order of severity levels (high to low): Flash \> Urgent \> Alert

    -   **Examples:**

        -   List the alert details with the list names 'Test alert 1,Test alert 2' and the query
            ("Test" AND "Application") OR ("text" AND "json") with page size for polling as 10:
            -   List names = Test alert 1,Test alert 2
            -   Query = ("Test" AND "Application") OR ("text" AND "json")
            -   Page Size for Polling = 10

          

        ### Addition of Custom Severities on Ingested Data

        -   This app needs to add custom severity levels based on alert type. Adding the severity in
            the Splunk SOAR platform is handled by the Dataminr Pulse app on running the Test
            Connectivity.

        -   This app requires the proper app-level permissions to do so. Please note, for the
            Dataminr Pulse app to apply these custom severities to the Artifacts ingested via API
            queries using On Poll, you must make sure that the automation user you use has the
            correct permissions.

        -   By default, the automation user is selected to run the Dataminr Pulse for Splunk SOAR
            ingestion action. (See **Asset Configuration** \> **Asset Settings** \> **Advanced** )
            The automation user does **NOT** have access to view or edit **System Settings** , which
            includes the permission to view the custom severities on your instance. This will cause
            your On Poll action to fail since your user cannot add the custom severities (Flash,
            Urgent, and Alert) on your instance.

        -   In order to solve this problem, you must create a user of type **Automation** and assign
            this user a Role that has permissions to view or edit **System Settings** (
            **Administration** \> **User Management** \> **Users** **\> + User** button on the top
            right corner). Then, choose this user in your Dataminr Pulse for Splunk SOAR **Asset
            Settings** under **Advanced** and you will be able to successfully apply custom
            severities to your ingested data.  
              
            **Administration** \> **User Management** \> **Users** **\> + User**
            [![](/app_resource/dataminrpulseforsplunksoar_8630b723-b317-4765-b923-5be5229c71d1/img/create_user.png)](/app_resource/dataminrpulseforsplunksoar_8630b723-b317-4765-b923-5be5229c71d1/img/create_user.png)  
              
              
            **Administration** \> **User Management** \> **Roles & Permissions** **\> + Role**
            [![](/app_resource/dataminrpulseforsplunksoar_8630b723-b317-4765-b923-5be5229c71d1/img/create_role.png)](/app_resource/dataminrpulseforsplunksoar_8630b723-b317-4765-b923-5be5229c71d1/img/create_role.png)  
              
              
            **Asset Settings** \> **Advanced**
            [![](/app_resource/dataminrpulseforsplunksoar_8630b723-b317-4765-b923-5be5229c71d1/img/asset_settings.png)](/app_resource/dataminrpulseforsplunksoar_8630b723-b317-4765-b923-5be5229c71d1/img/asset_settings.png)  
              
              

              
            **NOTE:** If an error perists related to severity addition, it would be visible in logs
            while data ingestion. In this case, the user is advised to add the severity manually
            using these steps:

            -   On the SOAR platform, navigate to **Administration->Event Settings->Severity**

            -   Click on **ADD ITEM** and add severity type 'Flash' and select color as 'Red'. Click
                on **Done** .

            -   Click on **ADD ITEM** and add severity type 'Urgent' and select color as 'Orange'.
                Click on **Done** .

            -   Click on **ADD ITEM** and add severity type 'Alert' and select color as 'Yellow'.
                Click on **Done** .

            -   **NOTE:** The severity types are case-sensitive hence, user is advised to add
                severity in **same case and same order** as mentioned above and as shown in below
                image.

                  
                [![](img/add_severity.png)](img/add_severity.png)

-   ### Get Lists

    Retrieves all the watchlists of user's account.  
    The action has no parameters.

-   ### Get Alerts

    Fetch the details of the alerts from the Dataminr platform for the given List ID or query.

    -   **Action Parameter: List ID**

          

        -   This parameter accepts comma-seperated ids of the watchlist and it is required if we do
            not use the query parameter. Example: 1234567,1234568
        -   If any one of the List IDs is invalid in the comma-separated string, the action will
            skip that List ID and continue with the valid ones.  
        -   Users can get the list ID by executing the "get lists" action.

    -   **Action Parameter: Use asset configured lists**

          

        -   This parameter is the optional boolean parameter. On marking it as true, the list id
            will be considered the one which is configured in the asset parameter.
        -   If the user provides a list id and marks this boolean parameter as true, then priority
            will be given to list ids.

    -   **Action Parameter: Query**

          

        -   This parameter accepts the search value for all the watchlists and it is required if we
            do not use the query parameter. Example: ("Test" AND "Application") OR ("text" AND
            "json")
        -   The query parameter is case-insensitive.
        -   **Note:** If the user provides a list id and query both, then the action will return
            queried alerts from that particular watchlist only.

        **Note:** User need to provide either 'list id' in action parameter or valid 'list names' in
        asset configuration parameter or 'query' to fetch alerts.

    -   **Action Parameter: Max Alerts**

          

        -   This parameter allows the user to limit the number of alerts in the response. It expects
            a numeric value as an input.
        -   The default value is 40 for this parameter.

    -   **Action Parameter: From**

          

        -   This parameter points to a cursor that you want any alerts after.

    -   **Action Parameter: To**

          

        -   This parameter points to a cursor that you want any alerts before.

        **Note:** Only one of "from" or "to" parameter can be included at a time.

    -   **Examples:**
        -   List the alert details with the List ID '1234567,1234568' and the query ("Test" AND
            "Application") OR ("text" AND "json") with max alerts as 10:
            -   List ID = 1234567,1234568
            -   Query = ("Test" AND "Application") OR ("text" AND "json")
            -   Max Alerts = 10

-   ### Get Related Alerts

    Fetch the details of the asset from the Dataminr platform for the given Alert ID.

    -   **Action Parameter: Alert ID**

          

        -   This parameter is the unique key for any particular alert and it is a required
            parameter.  
        -   If the Alert ID provided is invalid, the action will return an empty response.
        -   Users can get the alert ID by executing the "get alerts" action.

    -   **Action Parameter: Include Root**

          

        -   This parameter accepts a boolean value and it is optional.
        -   This parameter is used if the user wants the root alert (provided alert) in the get
            related alerts response.

    -   **Examples:**
        -   List the alerts detail with the Alert ID '01234567-1672385801826-3' with includeRoot as
            True.

              

            -   Alert ID = 01234567-1672385801826-3
            -   includeRoot = True
