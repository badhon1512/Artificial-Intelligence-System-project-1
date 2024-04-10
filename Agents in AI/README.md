# Repository for ws2324.1.0.a/um48ozus-1

# WS2324 Assignment 0 (Warm-Up, Variant A): Clean the Wumpus Cave

Welcome to the repository for the solution of Assignment 0 (Warm-Up, Variant A): Clean the Wumpus Cave. In this assignment, I have implemented a simple agent using Python to Clean the
Wumpus Cave. Depth-first search(DFS) has been used to implement this agent.

## Getting Started

### Prerequisites

Ensure you have a recent version of Python installed on your system. If Python is not installed, you can download and install it from the official Python website:

```bash
https://www.python.org/downloads/
```
Additionally, Install numpy on your system using following command if you don't have.

```bash
pip install numpy
```
### Running the Script

To run the script, open the command prompt (cmd) in your project's root directory and execute the following command:
```bash
python wumpus_cave_solver.py
```

### Output

After successful execution, the script will generate solution file for each problems inside the solutions directory.

## Insights about the Approach

My approach primarily revolves around adapting DFS algorithm, which is a well-known algorithm for graph searching. For this assignment, special attention was given to the direction of explore to make sure agent clean as much as possible dirt before backtracking.

### Challenges and Solutions

- **Handling FIND PLAN for unknown starting position(problem-f):**

  - Start with a List: Create a list 'L' of all empty squares to identify potential starting positions.
  - Develop Initial Plan: Use the first position in 'L' to develop a cleaning plan using simple cleaning approach that was implemented for problem-d, then apply and adjust it for subsequent positions in 'L'.
  - Extend with DFS: If some areas remain uncleaned, use DFS and heuristics to extend the plan, ensuring it remains effective for previous starting positions.
  - Iteratively Optimize: Apply and refine this plan for each position in 'L', ensuring the extended plan is efficient and not excessively long.
  
### Conclusion

This project showcases a practical implementation of the Depth-First Search (DFS) algorithm, tailored for a simple agent. It underscores the importance of customizing algorithms to meet specific requirements. The innovative strategies employed in this assignment effectively address the unique challenges of the task, resulting in a solution that is both robust and efficient.

---

For any queries or further assistance, please feel free to reach out to me(badhon.miah@fau.de).


