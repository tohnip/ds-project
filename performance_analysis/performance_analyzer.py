import os
import re
import matplotlib.pyplot as plt
import random

performance_measurement_folder = "performance_measurements"

measurement_parsing_regex = r"'forwarding_data_duration_seconds': ([0-9]+\.[0-9]+), 'data_size': ([0-9]+)"
filename_parsing_regex = r"([0-9]+)percent_cpu_([0-9]+)_stream"


file_results = {}

files = list(os.listdir(performance_measurement_folder))
files = sorted(files)

for file in files:
    filepath = os.path.join(performance_measurement_folder, file)
    if not os.path.isfile(filepath):
        continue
    
    parsing_matches = re.search(filename_parsing_regex, file)

    file_results[file] = {
        "times": [],
        "sizes": [],
        "cpu_percentage": int(parsing_matches.group(1)),
        "num_streams": int(parsing_matches.group(2))
    }

    with open(filepath, "r") as f:
        line = f.readline()
        while line:
            if "performance_metrics" in line:
                parsing_matches = re.search(measurement_parsing_regex, line)
                time = parsing_matches.group(1)
                size = parsing_matches.group(2)
                file_results[file]["times"].append(float(time))
                file_results[file]["sizes"].append(int(size))

            line = f.readline()

plottable_results = {}
plottable_results["average_speed"] = {}
plottable_results["fastest_speed"] = {}
plottable_results["slowest_speed"] = {}
plottable_results["num_streams"] = {}

result_items = list(file_results.items())
shuffled_result_items = random.shuffle(result_items)


for filepath, results in result_items:
    num_samples = len(results["times"])

    time_sum = sum(results["times"])
    size_sum = sum(results["sizes"])
    average_forwarding_speed = size_sum/time_sum/1000
    max_forward_time = max(results["times"])

    forward_speeds = [size/time/1000 for size, time in zip(results["sizes"], results["times"])]
    slowest_forward = min(forward_speeds)
    fastest_forward = max(forward_speeds)

    cpu_percentage = results["cpu_percentage"]
    num_streams = results["num_streams"]

    result_string = f"""
measurement:            {filepath}
sample count:           {num_samples}
cpu availability:       {cpu_percentage} %
stream count:           {num_streams}
max forwarding time:    {max_forward_time} seconds
slowest forward speed:  {slowest_forward:.1f} KB/s
fastest forward speed:  {fastest_forward:.1f} KB/s
average forwards speed: {average_forwarding_speed:.1f} KB/s
"""

    print(result_string)

    for statname, stat in zip(
        ["average_speed", "fastest_speed", "slowest_speed", "num_streams", "max_forward_time"],
        [average_forwarding_speed, fastest_forward, slowest_forward, num_streams, max_forward_time]
    ):
        if statname not in plottable_results:
            plottable_results[statname] = {}
        if str(cpu_percentage) not in plottable_results[statname]:
            plottable_results[statname][str(cpu_percentage)] = []
        plottable_results[statname][str(cpu_percentage)].append(stat)


for stat in plottable_results:
    plot_samples = {}
    for cpu in plottable_results[stat]:
        plottable_results[stat][cpu] = [value for _, value in sorted(zip(plottable_results["num_streams"][cpu], plottable_results[stat][cpu]), key=lambda pair: pair[0])]
        plot_samples[str(cpu)] = {"data": plottable_results[stat][cpu], "streams": sorted(plottable_results["num_streams"][cpu])}
        
    
    plot_arguments = [[plot_samples[cpu_key]["streams"], plot_samples[cpu_key]["data"], line] for cpu_key, line in zip(plot_samples.keys(), ['r--', 'b--', 'g--'][:len(plot_samples.keys())]) ]
    plot_arguments = [item for items in plot_arguments for item in items]

    plt.plot(*plot_arguments)
    plt.xlabel("number of streams")
    plt.ylabel(stat)
    plt.legend([f"cpu available {value}%" for value in plot_samples.keys()])
    plt.savefig(f"figures/fig_{stat}.png")
    plt.close()

