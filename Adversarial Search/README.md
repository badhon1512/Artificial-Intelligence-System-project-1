# WS2324 Assignment 1.2: Play FAUhalma - Team698 Repository

Welcome to the repository for Team698's solution for the WS2324 Assignment 1.2: Play FAUhalma. In this assignment, we have implemented an intelligent agent using Python to play the game of FAUhalma. Our agent uses a combination of heuristic strategies for optimal moves.

## Getting Started

### Prerequisites

Ensure you have a recent version of Python installed on your system. If Python is not installed, you can download and install it from the official Python website:

```bash
https://www.python.org/downloads/
```

### Running the Script

To run the script, open the command prompt (cmd) in your project's root directory and execute the following command (all json files are stored inside agent-configs folder) :
```bash
python client_simple.py path/to/your/config.json
```
To run the script for hardcore-3-players, open the command prompt (cmd) in your project's root directory and execute the following command:
```bash
python client_simple.py agent-configs/ws2324.1.2.8.json
```

### Agent Behaviour

The agent employs heuristic strategies to determine the best moves in the FAUhalma Game. It considers various factors, including peg positions, neighbors, and potential hops, to make informed decisions.

### Code Overview
#### Agent Class
The Agent class initializes the agent with a request dictionary containing peg positions. It then calculates the best moves based on a combination of heuristics.

### Heuristic Strategies
- The agent identifies active pegs and evaluates potential moves based on their positions.
- It prioritizes hop moves and simple moves, considering rewards associated with each.

### Output

Our agent competed by playing on the server: https://aisysproj.kwarc.info.
The following summarizes the output and performance of our FAUhalma agent in most difficult environment:
Best Rating: 1.4
Finished runs: 8150
Current rating: 1.08 



## Insights about the Approach

We have used Manhatan distance to calculate the base heurestic value for a specific position then by analyzing the game playing we have rewarded/penalized each position with a certain number based on number of simple hopes it is possible to made from that position, number of chain hops possible from that position and how that position help in blocking the opponent moves. 

### Challenges and Solutions

- **Calculating Heurestic:** 
  - To make sure for our agent to always win we initially tried to use simple eucledian distance but with that approach our agent was performing well on simple environments but on more complicated enviroments rating was low. Then we employeed Manhatan distance to calculate the heurestic of each position, with Manhatan distance our rating was improved a little bit but it was not performing well on the hard environment. So, in the end we tried to use combination of Manhatan distance and game playing condition to determine the heurestic value of each position and with differnt trials and runs we reached to values where our agent was performing well on the most difficult environment.

### Conclusion

This project showcases an intelligent agent for the FAUHalma, utilizing heuristic strategies for decision-making. The agent's approach involves evaluating potential moves and selecting the most rewarding ones.

---

For any queries or further assistance, please feel free to reach out to our team(badhon.miah@fau.de, aleem.ud.din@fau.de).

