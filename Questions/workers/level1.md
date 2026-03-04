Instructions
============

Your task is to implement a simplified version of a program registering the working hours of contract workers at a facility. All operations that should be supported by this program are described below.

Solving this task consists of several levels. Subsequent levels are opened when the current level is correctly solved. You always have access to the data for the current and all previous levels.

Requirements
------------

Your task is to implement a simplified version of a program registering the working hours of contract workers at a facility. Plan your design according to the level specifications below:

*   **Level 1**: The working hours register program should support adding workers to the system, registering the time when workers enter or leave the office and retrieving information about the time spent in the office.
*   **Level 2**: The working hours register program should support retrieving statistics about the amount of time that workers spent in the office.
*   **Level 3**: The working hours register program should support promoting workers, assigning them new positions and new compensation. The program should also support calculating a worker's salary for a given period.
*   **Level 4**: The working hours register program should support setting time periods to be double-paid.

To move to the next level, you need to pass all the tests at this level.

Level 1
=======

Introduce operations for adding workers, registering their entering or leaving the office and retrieving information about the amount of time that they have worked.

*   `ADD_WORKER <workerId> <position> <compensation>` — should add the workerId to the system and save additional information about them: their position and compensation. If the workerId already exists, nothing happens and this operation should return "false". If the workerId was successfully added, return "true". workerId and position are guaranteed to contain only English letters and spaces.
*   `REGISTER <workerId> <timestamp>` — should register the time when the workerId entered or left the office. The time is represented by the timestamp. Note that REGISTER operation calls are given in the increasing order of the timestamp parameter. If the workerId doesn't exist within the system, nothing happens and this operation should return "invalid\_request". If the workerId is not in the office, this operation registers the time when the workerId entered the office. If the workerId is already in the office, this operation registers the time when the workerId left the office. If the workerId's entering or leaving time was successfully registered, return "registered".
*   `GET <workerId>` — should return a string representing the total calculated amount of time that the workerId spent in the office. The amount of time is calculated using finished working sessions only. It means that if the worker has entered the office but hasn't left yet, this visit is not considered in the calculation. If the workerId doesn't exist within the system, return an empty string.

Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `["ADD_WORKER", "Ashley", "Middle Developer", "150"]` | returns "true" |
| `["ADD_WORKER", "Ashley", "Junior Developer", "100"]` | returns "false"; the same workerId already exists within the system |
| `["REGISTER", "Ashley", "10"]` | returns "registered"; "Ashley" entered the office at timestamp 10 |
| `["REGISTER", "Ashley", "25"]` | returns "registered"; "Ashley" left the office at timestamp 25 |
| `["GET", "Ashley"]` | returns "15"; "Ashley" spent 25 - 10 = 15 time units in the office |
| `["REGISTER", "Ashley", "40"]` | returns "registered" |
| `["REGISTER", "Ashley", "67"]` | returns "registered" |
| `["REGISTER", "Ashley", "100"]` | returns "42"; "Ashley" spent (25 - 10) + (67 - 40) = 42 time units in the office |
| `["GET", "Ashley"]` | returns "42" |
| `["GET", "Walter"]` | returns ""; id "Walter" was never added to the system |
| `["REGISTER", "Walter", "120"]` | returns "invalid_request"; "Walter" was never added to the system |

the output should be `["true", "false", "registered", "registered", "15", "registered", "registered", "registered", "42", "", "invalid_request"]`.

Input/Output
------------

*   **\[execution time limit\]** 4 seconds (py3)
*   **\[memory limit\]** 1 GB
*   **\[input\]** array.array.string queriesAn array of queries to the system. It is guaranteed that all the queries parameters are valid: each query calls one of the operations described in the description, all operation parameters are given in the correct format, and all conditions required for each operation are satisfied.Guaranteed constraints:1 ≤ queries.length ≤ 500.
*   **\[output\]** array.stringAn array of strings representing the returned values of queries.