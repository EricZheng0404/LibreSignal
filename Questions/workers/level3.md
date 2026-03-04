Level 3
=======

Introduce operations for worker promotion and salary calculation.

*   `PROMOTE <workerId> <newPosition> <newCompensation> <startTimestamp>` — should register a new position and new compensation for the workerId. newPosition is guaranteed to be different from the current worker's position. New position and new compensation are active from the moment of the first entering the office after or at startTimestamp. In other words, the first time period of being in office for the newPosition is the first time period that starts after or at startTimestamp. startTimestamp is guaranteed to be greater than timestamp parameter of the last REGISTER call for any worker. If the PROMOTE operation is called repeatedly for the same workerId before they entered the office with the newPosition, nothing happens, and this operation should return "invalid\_request". If workerId doesn't exist within the system, nothing happens, and this operation should return "invalid\_request". If the worker's promotion was successfully registered, return "success". Note: TOP\_N\_WORKERS operation should take only the worker's current position into account. GET operation should return the total amount of time across all the worker's past and current positions.
*   `CALC_SALARY <workerId> <startTimestamp> <endTimestamp>` — should calculate net salary that workerId has earned for the time period between startTimestamp and endTimestamp. No restrictions are applied to startTimestamp and endTimestamp, except that it is guaranteed that endTimestamp > startTimestamp >= 0. Note that workers are only paid for the time they were present in the office. The amount of time is calculated using finished working sessions only. For any finished working session "sessionStartTimestamp, sessionEndTimestamp" salary is calculated as salary = (sessionEndTimestamp - sessionStartTimestamp) \* compensationDuringPeriod. Note, that compensationDuringPeriod may differ for different periods, because workers may be promoted. If workerId doesn't exist within the system, nothing happens and this operation should return an empty string.

Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `["ADD_WORKER", "John", "Middle Developer", "200"]` | returns "true" |
| `["REGISTER", "John", "100"]` | returns "registered" |
| `["REGISTER", "John", "125"]` | returns "registered"; now "John" has 25 time units spent in the office |
| `["PROMOTE", "John", "Senior Developer", "500", "200"]` | returns "success"; at timestamp 200, new position and compensation granted to "John" |
| `["REGISTER", "John", "150"]` | returns "registered"; "John" enters the office |
| `["PROMOTE", "John", "Senior Developer", "350", "250"]` | returns "invalid_request"; "John" has an active new position registered, not applied yet |
| `["REGISTER", "John", "300"]` | returns "registered"; "John" leaves the office; total 175 time units spent (25 + (300-150)) |
| `["REGISTER", "John", "325"]` | returns "registered"; "John" enters the office at timestamp 325 (new position starts from timestamp 200) |
| `["CALC_SALARY", "John", "0", "500"]` | returns "35000"; salary calculated for two periods under "Middle Developer" with compensation = 200 |
| `["TOP_N_WORKERS", "3", "Senior Developer"]` | John(0) |
| `["REGISTER", "John", "400"]` | registered |
| `["GET", "John"]` | 250 |
| `["TOP_N_WORKERS", "10", "Senior Developer"]` | returns "John(75)" |
| `["TOP_N_WORKERS", "10", "Middle Developer"]` | returns "" |
| `["CALC_SALARY", "John", "110", "350"]` | returns "45500"; salary calculated across periods and positions with compensations 200 and 500 |
| `["CALC_SALARY", "John", "900", "1400"]` | returns "0" |


the output should be `["true", "registered", "registered", "success", "registered", "invalid_request", "registered", "registered", "35000", "John(0)", "registered", "250", "John(75)", "", "45500", "0"]`.

Input/Output
------------

*   **\[execution time limit\]** 4 seconds (py3)
*   **\[memory limit\]** 1 GB
*   **\[input\]** array.array.string queriesAn array of queries to the system. It is guaranteed that all the queries parameters are valid: each query calls one of the operations described in the description, all operation parameters are given in the correct format, and all conditions required for each operation are satisfied.Guaranteed constraints:1 ≤ queries.length ≤ 500.
*   **\[output\]** array.stringAn array of strings representing the returned values of queries.