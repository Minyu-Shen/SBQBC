import matplotlib.pyplot as plt


def set_x_y_draw(x_label, y_label):
    # draw settings
    # plt.rc('text', usetex=True)
    # plt.rc('font', family='serif')
    fig, ax = plt.subplots()
    ax.set_xlabel(x_label, fontsize=13)
    ax.set_ylabel(y_label, fontsize=13)
    ax.grid(linestyle='--')
    ax.tick_params(axis='both', which='major', labelsize=11)

    return plt, ax

