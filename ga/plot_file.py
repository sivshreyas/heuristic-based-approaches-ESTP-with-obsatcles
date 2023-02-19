import plotly.graph_objects as go
from plotly.subplots import make_subplots

import csv
import ast
titles = [
    "Weight: 1",
    "Weight: 1.25",
    "Weight: 1.5",
    "Weight: 1.75",
    "Weight: 5",
]
fig = make_subplots(rows=1, cols=5, subplot_titles=titles, shared_yaxes=True)
col = 0
row = 1

lowest_y = float('inf')
highest_y = -float('inf')
lowest_x = float('inf')
highest_x = -float('inf')


def run(file_path):
    print("parsing", file_path)
    global col
    global row
    global lowest_y
    global highest_y
    global lowest_x
    global highest_x
    col = col + 1
    with open(file_path, 'r') as file:
        data = []
        lines = file.readlines()
        csvreader = list(csv.reader(lines))
        # print(csvreader[1])
        terminals = ast.literal_eval(csvreader[1][1])
        x_vals = []
        y_vals = []
        for x,y in terminals:
            x_vals.append(x)
            y_vals.append(y)
        fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='markers', marker={'color':'crimson','size': 12}),  row=row, col=col)
        obstacles = ast.literal_eval(csvreader[0][1])
        for obstacle in obstacles:
            x_vals = []
            y_vals = []
            first_x = None
            first_y = None
            for x, y in obstacle:
                if not first_x:
                    first_x = x
                if not first_y:
                    first_y = y
                if lowest_y > y:
                    lowest_y = y
                if highest_y < y:
                    highest_y = y
                if lowest_x > x:
                    lowest_x = x
                if highest_x < x:
                    highest_x = x
                x_vals.append(x)
                y_vals.append(y)
            x_vals.append(first_x)
            y_vals.append(first_y)
            fig.add_trace(go.Scatter(x=x_vals, y=y_vals, fill="toself", line=dict(
                color="RoyalBlue",
                width=2,
            ), fillcolor="LightSkyBlue", mode='lines'), row=row, col=col)
            # break
            # print(obstacles)

        edges = ast.literal_eval(csvreader[-1][9])
        print(edges[0])
        for edge in edges:
            x_vals = []
            y_vals = []
            for x, y in edge:
                if lowest_y > y:
                    lowest_y = y
                if highest_y < y:
                    highest_y = y
                if lowest_x > x:
                    lowest_x = x
                if highest_x < x:
                    highest_x = x
                x_vals.append(x)
                y_vals.append(y)
                fig.add_trace(go.Scatter(x=x_vals, y=y_vals, line=dict(
                    color="Red", width=2), mode="lines"), row=row, col=col)


file_paths = [
    '/home/ubuntu/roads/soft/soft/1/data_dir/gen-1502-35717736123284-2.285881804955985.csv',
    '/home/ubuntu/roads/soft/soft/2/data_dir/gen-1502-34379985130444-2.369993945464816.csv',
    '/home/ubuntu/roads/soft/soft/3/data_dir/gen-1502-82545790061577-2.487352865052874.csv',
    '/home/ubuntu/roads/soft/soft/4/data_dir/gen-1495-20977203334175-2.602945744082756.csv',
    '/home/ubuntu/roads/soft/soft/5/data_dir/gen-1502-54153188958333-3.3313365907723433.csv'
]


for i, file_path in enumerate(file_paths):
    run(file_path)


# print([lowest_y - 0.3, highest_y + 0.3])
# # fig.update_layout(yaxis_range=[lowest_y - 0.3, highest_y + 0.3])
# # fig.update(layout_yaxis_range = [lowest_y - 0.3, highest_y + 0.3])
x_m = (highest_x - lowest_x) * 0.05
y_m = (highest_y - lowest_y) * 0.05
fig.update_layout(yaxis=dict(range=[lowest_y - y_m, highest_y + y_m]))
fig.update_layout(xaxis=dict(range=[lowest_x - x_m, highest_x + x_m]))
# fig.update_layout(h)

# # fig.update_layout(autosize=False)
# fig.update_yaxes(
#     scaleanchor = "x",
#     scaleratio = 1,
#   )

# fig.update_layout(autosize=False)
# fig.update_xaxes(
#     scaleanchor="y",
#     scaleratio=1,
#   )
fig.update_layout(autosize=True, height=1000, width=5000, showlegend=False)
# fig.update_layout(legend=dict(
#     yanchor="top",
#     y=0.99,
#     xanchor="left",
#     x=0.01
# ))

# fig.show()
fig.write_image("plots/weights-1-5.png")
