import talk
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from config import *
from collections import deque
from scipy import signal
from time import time


# some magic patch to allow updating text while blitting
# don't try to understand
# from https://stackoverflow.com/questions/17558096/animated-title-in-matplotlib/39262547
def _blit_draw(self, artists, bg_cache):
    updated_ax = []
    for a in artists:
        if a.axes not in bg_cache:
            bg_cache[a.axes] = a.figure.canvas.copy_from_bbox(a.axes.figure.bbox)
        a.axes.draw_artist(a)
        updated_ax.append(a.axes)
    for ax in set(updated_ax):
        ax.figure.canvas.blit(ax.figure.bbox)


matplotlib.animation.Animation._blit_draw = _blit_draw


# plot class
class SignalPlot:
    """
    Receives raw data,
    applies low pass filter to remove noise
    and plots
    """

    def __init__(self, max_len):
        # plot settings
        self.maxLen = max_len
        self.ax = deque([0.0] * max_len)
        self.ay = deque([0.0] * max_len)
        self.info_text = ''
        self.counter = 0

        # initialize filter
        self.b = signal.firwin(FILTER_WINDOW_SIZE, FILTER_CUTOFF)
        self.filter_state1 = signal.lfilter_zi(self.b, 1)
        self.filter_state2 = signal.lfilter_zi(self.b, 1)

    def add(self, data):
        x1, x2 = data
        x1, x2 = self.filter(x1, x2)
        self.counter = (self.counter + 1) % PLOT_EVERY_TH  # modulate plotting speed
        if self.counter == 0:
            self.add_to_buf(self.ax, x1)
            self.add_to_buf(self.ay, x2)

    def filter(self, x1, x2):
        x1, self.filter_state1 = signal.lfilter(self.b, 1, [x1], zi=self.filter_state1)
        x2, self.filter_state2 = signal.lfilter(self.b, 1, [x2], zi=self.filter_state2)
        return x1, x2

    def add_to_buf(self, buf, val):
        if len(buf) < self.maxLen:
            buf.append(val)
        else:
            buf.pop()
            buf.appendleft(val)

    # update plot
    # it's called every frame by the animation function
    def update(self, frameNum, a0, a1, info_display):
        a0.set_data(range(self.maxLen), self.ax)
        a1.set_data(range(self.maxLen), self.ay)
        info_display.set_text(self.info_text)
        return a0, a1, info_display


def key_command_handle(event):
    if event.key == 'q':
        plt.close()


def main():
    # set plot parameters
    plt.style.use('dark_background')
    fig = plt.figure()
    signal_plot = SignalPlot(PLOT_X_SIZE)

    # turn on serial communication
    controller = talk.ServoController(signal_plot)
    reader = talk.Reader(signal_plot)
    reader.start()

    # set up animation
    ax = plt.axes(xlim=(0, PLOT_X_SIZE), ylim=(YMIN, YMAX))
    a0, = ax.plot([], [])
    a1, = ax.plot([], [])
    txt = ax.text(0.05, 1.05, '', fontsize=14, transform=ax.transAxes)
    anim = animation.FuncAnimation(fig, signal_plot.update,
                                   fargs=(a0, a1, txt),
                                   interval=25,
                                   blit=True)

    # set callbacks
    fig.canvas.mpl_connect('key_press_event', key_command_handle)
    fig.canvas.mpl_connect('motion_notify_event', controller.set_angle)
    fig.canvas.mpl_connect('scroll_event', controller.set_stiffness)

    # show plot (blocking)
    plt.show()

    # clean up
    reader.kill()
    reader.join()


if __name__ == '__main__':
    main()
