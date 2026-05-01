import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ----------------------------
# Page Setup
# ----------------------------
st.set_page_config(page_title="Coffee Pour Lab", layout="wide")
st.title("☕ Coffee Pour Lab")
st.markdown("Compare pour patterns on a circular coffee bed — like a brewing wind tunnel.")

# ----------------------------
# Grid + Circular Bed
# ----------------------------
GRID_SIZE = 140
RADIUS = GRID_SIZE // 2 - 6
cx, cy = GRID_SIZE // 2, GRID_SIZE // 2

x = np.arange(GRID_SIZE)
y = np.arange(GRID_SIZE)
X, Y = np.meshgrid(x, y)

mask = (X - cx)**2 + (Y - cy)**2 <= RADIUS**2

# ----------------------------
# Sidebar Controls
# ----------------------------
st.sidebar.header("⚙️ Controls")

flow_rate = st.sidebar.slider("Flow Rate", 0.1, 3.0, 1.0, 0.1)
sigma = st.sidebar.slider("Spread (Sigma / Pour Height)", 0.5, 6.0, 2.5, 0.1)
steps = st.sidebar.slider("Speed (Steps / Pour Duration)", 500, 5000, 2000, 100)
pitch = st.sidebar.slider("Spiral Pitch (Tight ↔ Loose)", 0.2, 2.0, 1.0, 0.1)
rows = st.sidebar.slider("Zigzag Rows (Density)", 4, 24, 12, 1)

# ----------------------------
# Pour Patterns
# ----------------------------
def spiral_path(t, total_steps, pitch):
    # theta increases steadily
    theta = 8 * np.pi * (t / total_steps)

    # radius grows based on pitch
    r = pitch * theta

    # normalize so it fits inside the coffee bed
    max_r = pitch * (8 * np.pi)
    r = (r / max_r) * RADIUS

    px = cx + r * np.cos(theta)
    py = cy + r * np.sin(theta)

    return px, py

def zigzag_path(t, total_steps, rows):
    row_height = (2 * RADIUS) / rows
    current_row = int((t / total_steps) * rows)

    y = cy - RADIUS + current_row * row_height + row_height / 2

    if current_row % 2 == 0:
        x = cx - RADIUS + (t % (total_steps // rows)) / (total_steps // rows) * (2 * RADIUS)
    else:
        x = cx + RADIUS - (t % (total_steps // rows)) / (total_steps // rows) * (2 * RADIUS)

    return x, y

# ----------------------------
# Simulation
# ----------------------------
@st.cache_data
def run_simulation(pattern, steps, flow_rate, sigma, rows):
    bed = np.zeros((GRID_SIZE, GRID_SIZE))

    for t in range(steps):
        if pattern == "Spiral":
            px, py = spiral_path(t, steps, pitch)
        else:
            px, py = zigzag_path(t, steps, rows)

        if (px - cx)**2 + (py - cy)**2 > RADIUS**2:
            continue

        deposit = flow_rate * np.exp(-((X - px)**2 + (Y - py)**2) / (2 * sigma**2))
        bed += deposit

    return np.where(mask, bed, np.nan)

def uniformity_score(bed):
    vals = bed[~np.isnan(bed)]
    return np.std(vals) / np.mean(vals)

# ----------------------------
# Run Both Simulations
# ----------------------------
spiral = run_simulation("Spiral", steps, flow_rate, sigma, rows)
zigzag = run_simulation("Zigzag", steps, flow_rate, sigma, rows)

score_spiral = uniformity_score(spiral)
score_zigzag = uniformity_score(zigzag)

difference = spiral - zigzag

# ----------------------------
# Layout
# ----------------------------
col1, col2 = st.columns(2)

# Spiral
with col1:
    st.subheader("🌀 Spiral")
    fig1, ax1 = plt.subplots()
    im1 = ax1.imshow(spiral, origin='lower')
    ax1.set_title(f"Uniformity: {score_spiral:.4f}")
    plt.colorbar(im1, ax=ax1)
    st.pyplot(fig1)

# Zigzag
with col2:
    st.subheader("↔️ Zigzag")
    fig2, ax2 = plt.subplots()
    im2 = ax2.imshow(zigzag, origin='lower')
    ax2.set_title(f"Uniformity: {score_zigzag:.4f}")
    plt.colorbar(im2, ax=ax2)
    st.pyplot(fig2)

# ----------------------------
# Difference Map
# ----------------------------
st.markdown("---")
st.subheader("🔍 Difference Map (Spiral − Zigzag)")

fig3, ax3 = plt.subplots()
im3 = ax3.imshow(difference, origin='lower', cmap='coolwarm')
ax3.set_title("Red = Spiral more water | Blue = Zigzag more water")
plt.colorbar(im3, ax=ax3)
st.pyplot(fig3)

# ----------------------------
# Metrics + Insight
# ----------------------------
st.markdown("---")

m1, m2, m3 = st.columns(3)

m1.metric("Spiral Uniformity", f"{score_spiral:.4f}")
m2.metric("Zigzag Uniformity", f"{score_zigzag:.4f}")
m3.metric("Winner", "Spiral" if score_spiral < score_zigzag else "Zigzag")

# ----------------------------
# Interpretation Panel
# ----------------------------
st.markdown("### 🧠 Interpretation")

if score_spiral < score_zigzag:
    st.success("Spiral is more uniform under current settings.")
else:
    st.warning("Zigzag is outperforming spiral (interesting — check parameters).")

st.markdown("""
**What you're seeing:**

- Spiral aligns with circular symmetry → smoother gradients  
- Zigzag introduces directional bias → banding risk  
- High sigma reduces differences (diffusion dominates)  
- Low sigma exposes path inefficiencies  

**Try this:**

- Reduce sigma → exaggerate pattern differences  
- Increase zigzag rows → reduce striping  
- Lower steps → simulate rushed pours  
""")

# ----------------------------
# Footer Insight
# ----------------------------
st.markdown("---")
st.markdown("""
### ☕ Real-World Translation

- **Sigma ≈ Pour Height + Turbulence**
- **Steps ≈ Pour Time / Control**
- **Pattern ≈ Pour Technique**

This is not just visualization — it's a proxy for **extraction uniformity**.
""")