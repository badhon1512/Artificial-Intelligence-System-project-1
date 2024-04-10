# WS2324 Assignment 1.1: Find Train Connections - Team980 Repository

Welcome to the repository for Team980's solution for the WS2324 Assignment 1.1: Find Train Connections. Our approach utilizes Dijkstra's algorithm to determine the optimal train routes based on various cost functions.

## Getting Started

### Prerequisites

Ensure you have a recent version of Python installed on your system. If Python is not installed, you can download and install it from the official Python website:

```bash
https://www.python.org/downloads/
```

### Running the Script

To run the script, open the command prompt (cmd) in your project's root directory and execute the following command:
```bash
python connections.py
```

### Output

After successful execution, the script will generate a file named `solutions.csv` in the same root directory containing the optimal solutions for the train connections. The message 'Solutions have been written in solutions.csv file' will confirm the successful execution and creation of this file.

## Insights about the Approach

Our approach primarily revolves around adapting Dijkstra's algorithm, which is a well-known method for finding the shortest paths from a single source to all other nodes in a graph. For this assignment, special attention was given to the cost functions related to price and arrival time, as these posed unique challenges.

### Challenges and Solutions

- **Handling Arrival Time and Price Cost Functions:** 
  - To effectively manage these cost functions, we first mapped out all possible scenarios using pen and paper, inspired by the example solutions provided.
  - We identified that sometimes the optimal path for the 'price' cost function may not always be the shortest. To accommodate this, we modified the relaxation condition in Dijkstra's algorithm to consider paths with a cost less than or equal to the current cost. This change was crucial as it allowed the exploration of alternative paths that, while having the same cost, could offer more efficient solutions by avoiding additional train changes.

### Conclusion

This project demonstrates a practical application of Dijkstra's algorithm in a real-world scenario, highlighting the need for algorithm adaptation based on specific requirements. The team's innovative approach to tackling the unique challenges presented by the assignment led to a robust and effective solution.

---

For any queries or further assistance, please feel free to reach out to our team(badhon.miah@fau.de).

