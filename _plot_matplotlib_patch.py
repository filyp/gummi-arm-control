import matplotlib
import matplotlib.animation as animation

# some monkey patch to allow updating text while blitting
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


