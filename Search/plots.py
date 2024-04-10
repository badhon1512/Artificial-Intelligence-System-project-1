import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
df = pd.read_csv('summary.csv')

# Filter the dataset for 'schedule' problems more safely

# Filter the DataFrame for each problem type
df_type1 = df[df['file_name'] == 'schedule']
df_type2 = df[df['file_name'] == 'mini-schedule']

# Create a figure and a set of subplots
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(14, 6))

# First subplot for 'type1' problems
axes[0].scatter(df_type1['explored_neighbors'], df_type1['computation_time'], color='blue', alpha=0.5)
axes[0].set_title('Type 1 Problems', fontsize=14)
axes[0].set_xlabel('Number of Stations', fontsize=12)
axes[0].set_ylabel('Time in Seconds', fontsize=12)
axes[0].grid(True)

# Second subplot for 'type2' problems
axes[1].scatter(df_type2['explored_neighbors'], df_type2['computation_time'], color='green', alpha=0.5)
axes[1].set_title('Type 2 Problems', fontsize=14)
axes[1].set_xlabel('Number of Stations', fontsize=12)
axes[1].set_ylabel('Time in Seconds', fontsize=12)
axes[1].grid(True)

# Adjust layout
plt.tight_layout()

# Display the plot
plt.show()
