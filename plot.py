"""
main file
filters raw data from the current sensors and plots it
handles mouse commands:
    x position  ->  set servo angle
    scroll      ->  set arm stiffness
"""

from collections import deque

import matplotlib.pyplot as plt
from scipy import signal

import talk
from config._matplotlib_animation_patch import *
from config.constants import FILTER_WINDOW_SIZE, FILTER_CUTOFF, \
    PLOT_EVERY_TH, PLOT_X_SIZE, MAX_ANGLE


# plot class
class SignalPlot(object):
    """
    Receives raw data
    applies low pass filter to remove noise
    and plots
    """

    def __init__(self,):
        # apply plot settings
        self.buff1 = deque([0.0] * PLOT_X_SIZE)
        self.buff2 = deque([0.0] * PLOT_X_SIZE)
        self.info_text = ''
        self.counter = 0

        # initialize filter
        self.filter_coef = signal.firwin(FILTER_WINDOW_SIZE, FILTER_CUTOFF)
        self.filter_state1 = signal.lfilter_zi(self.filter_coef, 1)
        self.filter_state2 = signal.lfilter_zi(self.filter_coef, 1)

    def add(self, i1, i2):
        """
        filters noise from given data, and then adds to plotting buffer
        :param i1:    raw data from the current sensor 1
        :param i2:    raw data from the current sensor 2
        """

        i1, i2 = self.filter(i1, i2)
        self.counter = (self.counter + 1) % PLOT_EVERY_TH  # modulate plotting speed
        if self.counter == 0:
            self.add_to_buff(self.buff1, i1)
            self.add_to_buff(self.buff2, i2)

    def filter(self, i1, i2):
        """filter out noise from raw sensor data"""
        i1, self.filter_state1 = signal.lfilter(self.filter_coef, 1, [i1], zi=self.filter_state1)
        i2, self.filter_state2 = signal.lfilter(self.filter_coef, 1, [i2], zi=self.filter_state2)
        return i1, i2

    def add_to_buff(self, buff, value):
        """
        add new value to the buffer
        if the buffer size is maximum, delete the oldest value
        """
        if len(buff) < PLOT_X_SIZE:
            buff.append(value)
        else:
            buff.pop()
            buff.appendleft(value)

    def update(self, frame_number, plot1, plot2, info_display):
        """
        update plot
        it's called every frame by the animation function
        :param frame_number:    (not used) number of animation frame
        :param plot1:           plot in the display to be updated
        :param plot2:           plot in the display to be updated
        :param info_display:    text displayed at the top to be updated
        """
        plot1.set_data(range(PLOT_X_SIZE), self.buff1)
        plot2.set_data(range(PLOT_X_SIZE), self.buff2)
        info_display.set_text(self.info_text)
        return plot1, plot2, info_display


def main():
    # set plot parameters
    plt.style.use('dark_background')
    fig = plt.figure()
    signal_plot = SignalPlot()

    # turn on serial communication
    controller = talk.ServoController(signal_plot)
    reader = talk.Reader(signal_plot)
    reader.start()

    # set up animation
    ax = plt.axes(xlim=(0, PLOT_X_SIZE), ylim=(0, 1))
    plot1, = ax.plot([], [])
    plot2, = ax.plot([], [])
    info_display = ax.text(0.05, 1.05, '', fontsize=14, transform=ax.transAxes)
    anim = animation.FuncAnimation(fig, signal_plot.update,
                                   fargs=(plot1, plot2, info_display),
                                   interval=25,
                                   blit=True)

    # set callbacks
    def key_command_handle(event):
        """close window when q is pressed"""
        if event.key == 'q':  # TODO 27 -> esc   ??
            plt.close()
    fig.canvas.mpl_connect('key_press_event', key_command_handle)

    def set_angle_by_mouse(event):
        """handle changing angle mouse command"""
        if event.inaxes:
            mouse_position = event.xdata / PLOT_X_SIZE
            controller.angle = int(mouse_position * MAX_ANGLE)
            controller.send()
    fig.canvas.mpl_connect('motion_notify_event', set_angle_by_mouse)

    def set_stiffness_by_mouse(event):
        """handle changing stiffness mouse command"""
        controller.stiffness += event.step
        controller.send()
    fig.canvas.mpl_connect('scroll_event', set_stiffness_by_mouse)


    # show plot (blocking)
    plt.show()

    # clean up
    reader.kill()
    reader.join()


if __name__ == '__main__':
    main()
