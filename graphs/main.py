import matplotlib.pyplot as plt

# # Data for the chart
# categories = ['Human Receptionist', 'Lumi']
# costs = [26520, 2000]

# # Create a bar chart
# plt.figure(figsize=(8, 6))
# bars = plt.bar(categories, costs, color=['skyblue', 'lightgreen'])

# # Annotate each bar with the corresponding cost
# for bar, cost in zip(bars, costs):
#     plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() - 1500,
#              f'SGD {cost:,}', ha='center', va='bottom', color='black', fontsize=12, fontweight='bold')

# # Add title and labels
# plt.title('Annual Cost Comparison: Human Receptionist vs. Lumi', fontsize=14)
# plt.ylabel('Annual Cost (SGD)', fontsize=12)
# plt.xlabel('Cost Categories', fontsize=12)

# # Display the chart
# plt.show()


# # Data for multilingual language support
# languages = ['English', 'Mandarin', 'Malay', 'Tamil', 'Japanese', 'Other Languages']
# usage_percentages = [40, 25, 15, 10, 5, 5]

# # Create a bar chart
# plt.figure(figsize=(10, 6))
# bars = plt.bar(languages, usage_percentages, color=['dodgerblue', 'orange', 'green', 'purple', 'red', 'gray'])

# # Annotate each bar with the percentage
# for bar, usage in zip(bars, usage_percentages):
#     plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
#              f'{usage}%', ha='center', va='bottom', color='black', fontsize=12, fontweight='bold')

# # Add title and labels
# plt.title('Estimated Language Usage at Lyf Funan Singapore', fontsize=14)
# plt.ylabel('Estimated Usage (%)', fontsize=12)
# plt.xlabel('Languages', fontsize=12)

# # Display the chart
# plt.show()

# # Data for response time reduction
# months = ['Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5', 'Month 6']
# human_response_time = [15, 15, 15, 15, 15, 15]  # constant response time for human support
# bot_response_time = [5, 4.5, 4, 3.5, 3, 2.5]    # projected improvement in bot response time

# # Create a line graph
# plt.figure(figsize=(10, 6))
# plt.plot(months, human_response_time, label='Human Response Time', color='red', linestyle='--', marker='o')
# plt.plot(months, bot_response_time, label='Bot Response Time', color='blue', marker='o')

# # Annotate each point with the corresponding response time
# for i, (human, bot) in enumerate(zip(human_response_time, bot_response_time)):
#     plt.text(months[i], human + 0.3, f'{human} mins', ha='center', color='red')
#     plt.text(months[i], bot - 0.5, f'{bot} mins', ha='center', color='blue')

# # Add title and labels
# plt.title('Projected Response Time Reduction: AI Bot vs. Human Support', fontsize=14)
# plt.xlabel('Months', fontsize=12)
# plt.ylabel('Average Response Time (minutes)', fontsize=12)
# plt.legend()

# # Display the chart
# plt.show()

import matplotlib.pyplot as plt

# # Data for the chart
# interaction_types = ['Feedback Conversation', 'Complaint Resolution', 'Follow-up Calls', 'Suggestions']
# conversion_rates = [40, 50, 30, 20]
# colors = ['#4CAF50', '#FF9800', '#03A9F4', '#9C27B0']

# # Set up the figure and axis
# fig, ax = plt.subplots(figsize=(10, 6))
# bars = plt.bar(interaction_types, conversion_rates, color=colors)

# # Add percentage labels on top of each bar
# for bar, rate in zip(bars, conversion_rates):
#     yval = bar.get_height()
#     ax.text(bar.get_x() + bar.get_width() / 2, yval + 2, f"{rate}%", ha='center', va='bottom', fontsize=12, fontweight='bold')

# # Title and labels
# plt.title("Projected Conversion Rate of Customer Interactions to Lyf Loyalty Points")
# plt.xlabel("Interaction Type")
# plt.ylabel("Conversion Rate (%)")
# plt.ylim(0, 60)  # Extend y-axis slightly above the max rate for clarity

# # Display the chart
# plt.show()

# # Data for the pie chart
# platforms = ['Lyf Room Displays', 'Phone Calls', 'WhatsApp', 'Hotel App']
# distribution = [35, 25, 30, 10]
# colors = ['#4CAF50', '#FF9800', '#03A9F4', '#9C27B0']

# # Create the pie chart
# fig, ax = plt.subplots(figsize=(8, 8))
# wedges, texts, autotexts = ax.pie(distribution, labels=platforms, autopct='%1.1f%%', startangle=140, colors=colors, textprops=dict(color="black"))

# # Set title and customize font size
# plt.setp(autotexts, size=12, weight="bold")
# plt.title("Customer Distribution Across Platforms")

# # Display the chart
# plt.show()

import numpy as np

# Data for the line chart
months = np.arange(1, 13)  # Months 1 through 12
initial_satisfaction = 65
improvement_rate = 2  # Percentage points per month
projected_satisfaction = initial_satisfaction + improvement_rate * (months - 1)
industry_average = 75  # Industry benchmark

# Plot the data
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(months, projected_satisfaction, label="Projected Satisfaction", marker='o', color='#4CAF50', linewidth=2)
ax.axhline(industry_average, color='#FF9800', linestyle='--', label="Industry Average")

# Labels and title
plt.title("Projected Customer Satisfaction Growth Over 12 Months")
plt.xlabel("Months")
plt.ylabel("Satisfaction Percentage (%)")
plt.xticks(months)
plt.ylim(60, 90)
plt.legend()

# Display the chart
plt.show()


