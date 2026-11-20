import pandas as pd
from tabulate import tabulate

df = pd.read_csv("students.csv")

print(tabulate(df, headers="keys", tablefmt="grid",
               showindex= False , colalign=("right", "left","right","left","right","right","right")))