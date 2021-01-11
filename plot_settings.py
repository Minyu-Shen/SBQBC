import matplotlib.pyplot as plt
import numpy as np
import matplotlib.tri as tri


def get_curve_plot(x_label, y_label, x_font, y_font):
    plt.rc("text", usetex=True)
    fig, ax = plt.subplots()
    ax.set_xlabel(x_label, fontsize=x_font)
    ax.set_ylabel(y_label, fontsize=y_font)
    ax.grid(linestyle="-.", alpha=0.4)

    return fig, ax


def set_x_y_draw(x_label, y_label):
    # draw settings
    # plt.rc('text', usetex=True)
    # plt.rc('font', family='serif')
    fig, ax = plt.subplots()
    ax.set_xlabel(x_label, fontsize=13)
    ax.set_ylabel(y_label, fontsize=13)
    ax.grid(linestyle="--")
    ax.tick_params(axis="both", which="major", labelsize=11)

    return fig, ax


def plot_contour_by_lists(x, y, z):
    fig, (ax1, ax2) = plt.subplots(nrows=2)

    x, y, z = np.array(x), np.array(y), np.array(z)
    n_grid_x = 25
    n_grid_y = 25
    n_pts = x.shape[0]
    xi = np.linspace(x.min(), x.max(), n_grid_x)
    yi = np.linspace(y.min(), y.max(), n_grid_y)
    # Perform linear interpolation of the data (x,y)
    # on a grid defined by (xi,yi)
    triang = tri.Triangulation(x, y)
    interpolator = tri.LinearTriInterpolator(triang, z)
    Xi, Yi = np.meshgrid(xi, yi)
    zi = interpolator(Xi, Yi)

    ax1.contour(xi, yi, zi, levels=14, linewidths=0.5, colors="k")
    cntr1 = ax1.contourf(xi, yi, zi, levels=14, cmap="RdBu_r")

    fig.colorbar(cntr1, ax=ax1)
    ax1.plot(x, y, "ko", ms=2)
    ax1.set_title(
        "grid and contour (%d points, %d grid points)" % (n_pts, n_grid_x * n_grid_y)
    )

    ax2.tricontour(x, y, z, levels=14, linewidths=0.5, colors="k")
    cntr2 = ax2.tricontourf(x, y, z, levels=14, cmap="RdBu_r")

    fig.colorbar(cntr2, ax=ax2)
    # ax2.plot(x, y, "ko", ms=3)
    ax2.set_title("tricontour (%d points)" % n_pts)
    plt.subplots_adjust(hspace=0.5)

    return fig
