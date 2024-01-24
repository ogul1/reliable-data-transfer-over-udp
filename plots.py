import seaborn as sb
import scipy.stats as stats
import matplotlib.pyplot as plt
import numpy as np

tcp_data = []
rdt_over_udp_data = []

sample_size = 30

for _ in range(sample_size):
    x = input()
    if "m" in x:
        x = x.split("m")
        x = 60 * float(x[0]) + float(x[1])
    tcp_data.append(float(x))

for _ in range(sample_size):
    x = input()
    if "m" in x:
        x = x.split("m")
        x = 60 * float(x[0]) + float(x[1])
    rdt_over_udp_data.append(float(x))

tcp_data = np.array(tcp_data)
rdt_over_udp_data = np.array(rdt_over_udp_data)

fig, ax = plt.subplots(figsize=(12, 6))

tcp_std_error = stats.sem(tcp_data)
tcp_confidence_interval = stats.t.interval(0.95, len(tcp_data) - 1, loc=np.mean(tcp_data), scale=tcp_std_error)

plt.axvline(x=tcp_confidence_interval[0], color='#482922', label='TCP 95% confidence lower bound')
plt.axvline(x=tcp_confidence_interval[1], color='#525252', label='TCP 95% confidence upper bound')

sb.histplot(tcp_data, label='TCP', kde=True)
plt.axvline(x=np.mean(tcp_data), color='#000000', label='Mean time of TCP')

rdt_over_udp_std_error = stats.sem(rdt_over_udp_data)
rdt_over_udp_confidence_interval = stats.t.interval(0.95, len(rdt_over_udp_data) - 1, loc=np.mean(rdt_over_udp_data), scale=rdt_over_udp_std_error)

plt.axvline(x=rdt_over_udp_confidence_interval[0], color='#FF4B25', label='RDT over UDP 95% confidence lower bound')
plt.axvline(x=rdt_over_udp_confidence_interval[1], color='#CC2400', label='RDT over UDP 95% confidence upper bound')

sb.histplot(rdt_over_udp_data, label='RDT over UDP', kde=True)
plt.axvline(x=np.mean(rdt_over_udp_data), color='#FF2D00', label='Mean time of RDT over UDP')

ax.legend()
plt.tight_layout()
plt.show()

# cat code/benchmark.txt | awk '$1 == "real" { gsub(/0m/,"",$2); gsub(/[s]/,"",$2); print $2 }' | python3 plots.py
