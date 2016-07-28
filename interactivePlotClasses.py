import matplotlib.pyplot as plt
import matplotlib.lines as mlines

class AxesSequence(object):
    """Creates a series of axes in a figure where only one is displayed at any
    given time. Which plot is displayed is controlled by the arrow keys."""
    def __init__(self):
        self.fig = plt.figure()
        self.axes = []
        self._i = 0 # Currently displayed axes index
        self._n = 0 # Last created axes index
        self.fig.canvas.mpl_connect('key_press_event', self.on_keypress)

    def __iter__(self):
        while True:
            yield self.new()

    def new(self):
        # The label needs to be specified so that a new axes will be created
        # instead of "add_axes" just returning the original one.
        ax = self.fig.add_axes([0.15, 0.1, 0.8, 0.8], visible=False, label=self._n)
        self._n += 1
        self.axes.append(ax)
        return ax

    def on_keypress(self, event):
        if event.key == 'right':
            self.next_plot()
        elif event.key == 'left':
            self.prev_plot()
        else:
            return
        self.fig.canvas.draw()

    def next_plot(self):
        if self._i < len(self.axes):
            self.axes[self._i].set_visible(False)
            self.axes[self._i+1].set_visible(True)
            self._i += 1

    def prev_plot(self):
        if self._i > 0:
            self.axes[self._i].set_visible(False)
            self.axes[self._i-1].set_visible(True)
            self._i -= 1

    def show(self):
        self.axes[0].set_visible(True)
        plt.show()


class AxesVisibility(object):
    def __init__(self, axeNames, columns):
        self.axeNames = axeNames
        self.columns = columns
        self.fig = plt.figure(figsize=(16,9))
        self.axes = []
        self._n = 0 # Last created axes index
        self.legendAxe = self.make_legend_axe()

    def __iter__(self):
        while True:
            yield self.new()

    def make_legend_axe(self):
        ax = self.fig.add_axes([0.05, 0.35, 0.9, 0.60], frameon=False, label='legend')
        ax.set_title('Click on legend line to toggle line on/off')
        ax.set_xlabel("Attribute Index")
        ax.set_ylabel("Attribute Values")
        ax.set_xticks(range(len(self.columns)))
        ax.set_xticklabels(self.columns)

        return ax

    def new(self):
        # The label needs to be specified so that a new axes will be created
        # instead of "add_axes" just returning the original one.
        ax = self.legendAxe.twiny().twinx()
        ax.grid(b=False)
        ax.get_xaxis().set_ticks([])
        ax.get_yaxis().set_ticks([])
        ax.set_label(self.axeNames[self._n])
        self._n += 1
        self.axes.append(ax)
        return ax

    def generate_legend(self):
        handles = []
        for ax in self.axes:
            for line in ax.get_lines():
                handles.append((line, line.get_label()))
                break

        toggleLabel = 'Hide All'
        handles.append((mlines.Line2D([], [], label=toggleLabel), toggleLabel))
        handles, labels = zip(*handles)
        legend = self.legendAxe.legend(handles, labels, bbox_to_anchor=(0.1, -0.4, 0.9, 0.30), ncol=5)

        lined, axes = {}, self.axes
        axes.append(None)
        for legLine, legAxe in zip(legend.get_lines(), axes):
            legLine.set_picker(5)  # 5 pts tolerance
            if legLine.get_label() == toggleLabel:
                lined[legLine] = False
            else:
                lined[legLine] = legAxe

        def on_pick(event):
            # on the pick event, find the orig line corresponding to the
            # legend proxy line, and toggle the visibility
            legLine = event.artist
            legAxe = lined[legLine]
            togglePop = [k for k, v in lined.items() if v == True or v == False][0]
            toggleStatus = lined.pop(togglePop)

            if legAxe is True:
                toggleStatus = not toggleStatus
                for line, axe in lined.items():
                    is_visible = True
                    axe.set_visible(is_visible)
                    line.set_alpha(1.0)
            elif legAxe is False:
                toggleStatus = not toggleStatus
                for line, axe in lined.items():
                    is_visible = False
                    axe.set_visible(is_visible)
                    line.set_alpha(0.2)
            else:
                is_visible = not legAxe.get_visible()
                legAxe.set_visible(is_visible)

            lined[togglePop] = toggleStatus

            if is_visible:
                legLine.set_alpha(1.0)
            else:
                legLine.set_alpha(0.2)
            self.fig.canvas.draw()

        self.fig.canvas.mpl_connect('pick_event', on_pick)

    def show(self):
        self.generate_legend()
        plt.show()
