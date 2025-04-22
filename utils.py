# utils.py

def additive_blend(colors):
    r = g = b = 0
    for cr, cg, cb, ca in colors:
        alpha = ca / 255.0
        r += cr * alpha
        g += cg * alpha
        b += cb * alpha
    return (min(int(r), 255), min(int(g), 255), min(int(b), 255), 255)
