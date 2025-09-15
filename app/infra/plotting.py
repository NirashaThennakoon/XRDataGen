import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def line_png(times, values, title: str):
    plt.figure(figsize=(10, 4))
    plt.plot(times, values, marker="o")
    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel("CO₂ (ppm)")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    return buf
