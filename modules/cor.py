from matplotlib import cm
# modules/utils.py

import colorsys

def gerar_cor(idx):
    cores_base = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
        "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
        "#bcbd22", "#17becf"
    ]
    if idx < len(cores_base):
        return cores_base[idx]
    else:
        h = (idx * 0.61803398875) % 1
        r, g, b = colorsys.hsv_to_rgb(h, 0.6, 0.9)
        return '#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255))
