import pandas as pd

# Sample DataFrame (same as above)
data = {'Name': ['Alice', 'Bob', 'Charlie'], 'Age': [25, 30, 28]}
df = pd.DataFrame(data)

# Create new row data as a dictionary
new_row = {'Name': 'David', 'Age': 35}

# Add the new row at the end using loc (by index)
a = len(df)
df.loc[a] = new_row