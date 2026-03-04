Level 2
=======

Introduce an operation to retrieve ordered statistics about the workers.

*   `TOP_N_WORKERS <n> <position>` — should return the string representing ids of the top n workers with the given position sorted in descending order by the total time spent in the office. The amount of time is calculated using finished working sessions only. In the case of a tie, workers must be sorted in alphabetical order of their ids. The returned string should be in the following format: "workerId1(timeSpentInOffice1), workerId2(timeSpentInOffice2), ..., workerIdN(timeSpentInOfficeN)". If less than n workers with the given position exist within the system, then return all ids in the described format. If there are no workers with the given position within the system, return an empty string. Note that if a worker exists within the system and doesn't have any finished periods of being in the office, their time spent in the office is considered to be 0.

Examples

The example below shows how this operation should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `["ADD_WORKER", "John", "Junior Developer", "120"]` | returns "true" |
| `["ADD_WORKER", "Jason", "Junior Developer", "120"]` | returns "true" |
| `["ADD_WORKER", "Ashley", "Junior Developer", "120"]` | returns "true" |
| `["REGISTER", "John", "100"]` | returns "registered" |
| `["REGISTER", "John", "150"]` | returns "registered"; now "John" has 50 time units spent in the office |
| `["REGISTER", "Jason", "200"]` | returns "registered" |
| `["REGISTER", "Jason", "250"]` | returns "registered"; now "Jason" has 50 time units spent in the office |
| `["REGISTER", "Jason", "275"]` | returns "registered"; "Jason" entered the office at timestamp 275 |
| `["TOP_N_WORKERS", "5", "Junior Developer"]` | returns "Jason(50), John(50), Ashley(0)"; "Jason" goes before "John" alphabetically |
| `["TOP_N_WORKERS", "1", "Junior Developer"]` | returns "Jason(50)" |
| `["REGISTER", "Ashley", "400"]` | returns "registered" |
| `["REGISTER", "Ashley", "500"]` | returns "registered"; now "Ashley" has 100 time units spent in the office |
| `["REGISTER", "Jason", "575"]` | returns "registered"; "Jason" left the office and now has 50 + (575 - 275) = 350 time units spent in the office |
| `["TOP_N_WORKERS", "3", "Junior Developer"]` | returns "Jason(350), Ashley(100), John(50)" |
| `["TOP_N_WORKERS", "3", "Middle Developer"]` | returns ""; there are no workers with position "Middle Developer" |


the output should be `["true", "true", "true", "registered", "registered", "registered", "registered", "registered", "Jason(50), John(50), Ashley(0)", "Jason(50)", "registered", "registered", "registered", "Jason(350), Ashley(100), John(50)", ""]`.

Input/Output
------------

*   **\[execution time limit\]** 4 seconds (py3)
*   **\[memory limit\]** 1 GB
*   **\[input\]** array.array.string queriesAn array of queries to the system. It is guaranteed that all the queries parameters are valid: each query calls one of the operations described in the description, all operation parameters are given in the correct format, and all conditions required for each operation are satisfied.Guaranteed constraints:1 ≤ queries.length ≤ 500.
*   **\[output\]** array.stringAn array of strings representing the returned values of queries.
