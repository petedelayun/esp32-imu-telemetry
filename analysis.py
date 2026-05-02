from matplotlib.animation import FuncAnimation
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

fig, axes = plt.subplots(3, 1, figsize=(12, 8))
fig.suptitle("ESP32 IMU Telemetry Analysis", fontsize=14, fontweight="bold")
df = pd.DataFrame()

def read_last_n(filepath, n=100):
    """
    0.017127 -> 0.008775
    1.96x faster than pandas read_csv
    """
    
    with open(filepath, "rb") as f:
        # Read header
        f.seek(0)
        header = f.readline().decode().strip().split(",")
        
        # Read last n lines efficiently
        f.seek(0, 2)  # seek to end
        file_size = f.tell()
        
        chunk = min(file_size, n * 100)  # estimate bytes needed
        f.seek(-chunk, 2)
        lines = f.read().decode().split("\n")
        lines = [l for l in lines if l.strip()][-n:]
        
    rows = [l.split(",") for l in lines[1:]]
    df = pd.DataFrame(rows, columns=header)
    df[["ax", "ay", "az", "gx", "gy", "gz"]] = df[["ax", "ay", "az", "gx", "gy", "gz"]].astype(float)
    
    return df

def animate(i):
    # Read n_rows from csv
    n_rows = 250
    df = read_last_n("telemetry.csv", n_rows)

    # Accelerometer magnitude
    df["accel_magnitude"] = np.sqrt(df["ax"]**2 + df["ay"]**2 + df["az"]**2)

    # Rolling z-score anomaly detection
    window = 50
    df["rolling_mean"] = df["accel_magnitude"].rolling(window).mean()
    df["rolling_std"]  = df["accel_magnitude"].rolling(window).std()
    df["z_score"]      = (df["accel_magnitude"] - df["rolling_mean"]) / df["rolling_std"]
    df["anomaly"]      = df["z_score"].abs() > 3.0

    # Clear only the axes we use, not the whole figure
    for ax in axes:
        ax.cla()

    # Accelerometer magnitude
    axes[0].plot(df["accel_magnitude"], color="steelblue")
    axes[0].set_title("Accelerometer Magnitude (g)")
    axes[0].set_ylabel("g-force")

    # Gyroscope
    axes[1].plot(df["gx"], label="Gyro X", alpha=0.7)
    axes[1].plot(df["gy"], label="Gyro Y", alpha=0.7)
    axes[1].plot(df["gz"], label="Gyro Z", alpha=0.7)
    axes[1].legend()
    axes[1].set_title("Gyroscope (degrees/sec)")
    axes[1].set_ylabel("°/s")

    # Anomaly detection
    axes[2].plot(df["accel_magnitude"], alpha=0.5, color="steelblue")
    axes[2].scatter(
        df[df["anomaly"]].index,
        df[df["anomaly"]]["accel_magnitude"],
        color="red", label="Anomaly", zorder=5, s=20
    )
    axes[2].legend()
    axes[2].set_title("Anomaly Detection (Z-score > 3)")
    axes[2].set_ylabel("g-force")

    fig.tight_layout()

ani = FuncAnimation(fig, animate, interval=1000, cache_frame_data=False)

plt.show()
