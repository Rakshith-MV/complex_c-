
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa

# Example function
def f(x, y):
    return np.sin(np.pi * x) * np.cos(np.pi * y) + 2

# Grid (needs even steps for Simpson)
n, m = 6, 6
x = np.linspace(0, 1, n+1)
y = np.linspace(0, 1, m+1)
X, Y = np.meshgrid(x, y, indexing="ij")
F = f(X, Y)

hx, hy = (x[-1]-x[0])/n, (y[-1]-y[0])/m

# Simpson weights (1D)
def simpson_weights(N):
    w = np.zeros(N+1, dtype=int)
    w[0], w[-1] = 1, 1
    for i in range(1, N):
        w[i] = 4 if i % 2 == 1 else 2
    return w

wx = simpson_weights(n)
wy = simpson_weights(m)

# 2D weight matrix
W = np.outer(wx, wy)

# Contribution matrix
C = (hx*hy/9) * W * F

# --- Plotting ---
fig = plt.figure(figsize=(12, 5))

# 1) Actual function surface
ax1 = fig.add_subplot(121, projection="3d")
ax1.plot_surface(X, Y, F, cmap="viridis", alpha=0.9)
ax1.set_title("Function Surface f(x,y)")
ax1.set_xlabel("x")
ax1.set_ylabel("y")
ax1.set_zlabel("f(x,y)")

# 2) Simpson contributions
ax2 = fig.add_subplot(122, projection="3d")
ax2.bar3d(X.ravel(), Y.ravel(), np.zeros_like(C.ravel()),
          dx=0.08, dy=0.08, dz=C.ravel(),
          color="teal", alpha=0.7, shade=True)
ax2.set_title("Simpson Contributions (weights × f × h_x h_y/9)")
ax2.set_xlabel("x")
ax2.set_ylabel("y")
ax2.set_zlabel("Contribution")

plt.tight_layout()
plt.show()