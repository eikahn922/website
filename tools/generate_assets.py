from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import random

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "generated"
OUT.mkdir(parents=True, exist_ok=True)

INK = (16, 21, 26)
PAPER = (246, 248, 250)
LINE = (215, 225, 231)
TEAL = (8, 126, 139)
RED = (209, 73, 91)
AMBER = (237, 174, 73)
GREEN = (47, 125, 89)
WHITE = (255, 255, 255)


def font(size, bold=False):
    names = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
    ]
    for name in names:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            pass
    return ImageFont.load_default()


def draw_grid(draw, size, step=56, color=(231, 237, 241), width=1):
    w, h = size
    for x in range(0, w + step, step):
        draw.line((x, 0, x, h), fill=color, width=width)
    for y in range(0, h + step, step):
        draw.line((0, y, w, y), fill=color, width=width)


def rounded_rect(draw, box, radius=8, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def label(draw, text, xy, fill=INK, size=34, bold=True):
    draw.text(xy, text, fill=fill, font=font(size, bold=bold))


def bolt_pattern(draw, center, rx, ry, count, color=INK):
    cx, cy = center
    for i in range(count):
        a = math.tau * i / count
        x = cx + math.cos(a) * rx
        y = cy + math.sin(a) * ry
        draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=color)


def save(img, name):
    img.save(OUT / name, optimize=True)


def hero():
    w, h = 1800, 1050
    img = Image.new("RGB", (w, h), (22, 27, 31))
    draw = ImageDraw.Draw(img)
    random.seed(7)

    for y in range(h):
        shade = int(22 + y / h * 18)
        draw.line((0, y, w, y), fill=(shade, shade + 5, shade + 7))

    for x in range(-100, w + 120, 84):
        draw.line((x, 0, x - 260, h), fill=(44, 58, 66), width=2)
    for y in range(40, h, 90):
        draw.line((0, y, w, y + 110), fill=(39, 49, 55), width=2)

    base_y = 800
    draw.line((210, base_y, 1410, base_y), fill=(210, 220, 225), width=18)
    draw.line((250, base_y + 56, 1490, base_y + 56), fill=(83, 102, 110), width=10)
    for x in range(280, 1450, 125):
        draw.line((x, base_y - 50, x + 34, base_y + 96), fill=(120, 138, 145), width=8)

    # Robot arm silhouette.
    joints = [(650, 720), (785, 525), (1025, 470), (1188, 340)]
    widths = [54, 46, 34]
    for (a, b), width in zip(zip(joints, joints[1:]), widths):
        draw.line((*a, *b), fill=(235, 239, 241), width=width)
        draw.line((*a, *b), fill=(70, 92, 102), width=max(6, width // 5))
    for idx, (x, y) in enumerate(joints):
        fill = [RED, TEAL, AMBER, GREEN][idx]
        draw.ellipse((x - 54, y - 54, x + 54, y + 54), fill=fill, outline=WHITE, width=8)
        draw.ellipse((x - 18, y - 18, x + 18, y + 18), fill=(25, 29, 32))
    draw.line((1188, 340, 1280, 300), fill=WHITE, width=14)
    draw.line((1280, 300, 1340, 260), fill=AMBER, width=10)
    draw.line((1280, 300, 1360, 330), fill=AMBER, width=10)

    # Table, instruments, and scope-like shapes.
    rounded_rect(draw, (1110, 610, 1560, 750), 8, fill=(233, 238, 242), outline=(90, 110, 120), width=4)
    rounded_rect(draw, (1165, 650, 1320, 710), 6, fill=(35, 44, 50), outline=TEAL, width=5)
    for i, color in enumerate([GREEN, AMBER, RED]):
        draw.ellipse((1360 + i * 46, 665, 1390 + i * 46, 695), fill=color)
    draw.line((360, 830, 460, 420), fill=(230, 236, 239), width=16)
    draw.line((460, 420, 560, 830), fill=(230, 236, 239), width=16)
    draw.line((400, 600, 520, 600), fill=TEAL, width=10)

    # Blueprint annotations.
    for x, y, txt in [(190, 185, "TORQUE"), (1250, 170, "ACTUATION"), (310, 915, "TEST RIG")]:
        rounded_rect(draw, (x, y, x + 190, y + 52), 6, fill=(255, 255, 255), outline=None)
        draw.text((x + 18, y + 14), txt, fill=INK, font=font(22, bold=True))
    img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=120))
    save(img, "hero-robotics-lab.png")


def favicon():
    img = Image.new("RGB", (192, 192), INK)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((18, 18, 174, 174), radius=24, fill=TEAL)
    draw.line((52, 132, 84, 68, 124, 68, 142, 132), fill=WHITE, width=14, joint="curve")
    for x, y, c in [(84, 68, RED), (124, 68, AMBER), (142, 132, GREEN)]:
        draw.ellipse((x - 18, y - 18, x + 18, y + 18), fill=c, outline=WHITE, width=5)
    save(img, "favicon.png")


def project_canvas(title, subtitle, accent, name, variant):
    w, h = 900, 600
    img = Image.new("RGB", (w, h), PAPER)
    draw = ImageDraw.Draw(img)
    draw_grid(draw, (w, h), step=50)
    draw.rectangle((0, 0, w, 84), fill=INK)
    draw.rectangle((0, 84, w, 96), fill=accent)
    draw.text((32, 24), title, fill=WHITE, font=font(31, bold=True))
    draw.text((w - 270, 30), subtitle, fill=(226, 232, 236), font=font(20, bold=True))

    if variant == "exo":
        draw.line((170, 470, 250, 235, 370, 215, 440, 480), fill=INK, width=16, joint="curve")
        draw.line((250, 235, 260, 420), fill=TEAL, width=18)
        draw.line((370, 215, 485, 305, 560, 470), fill=INK, width=14)
        for c in [(250, 235), (260, 420), (370, 215), (485, 305)]:
            draw.ellipse((c[0] - 34, c[1] - 34, c[0] + 34, c[1] + 34), fill=accent, outline=INK, width=5)
        rounded_rect(draw, (580, 190, 785, 380), 8, fill=WHITE, outline=INK, width=4)
        for i, value in enumerate([0.62, 0.86, 0.48, 0.74]):
            y = 220 + i * 34
            draw.rectangle((612, y, 612 + int(125 * value), y + 14), fill=[TEAL, RED, AMBER, GREEN][i])
            draw.rectangle((612, y, 742, y + 14), outline=LINE, width=2)
        label(draw, "LOAD PATH", (92, 128), accent, 24)
    elif variant == "arm":
        center = (460, 330)
        draw.line((170, 460, 720, 460), fill=INK, width=16)
        draw.line((280, 430, 420, 275), fill=INK, width=38)
        draw.line((420, 275, 620, 240), fill=TEAL, width=32)
        draw.line((620, 240, 710, 185), fill=INK, width=22)
        for c, r, col in [((280, 430), 52, RED), ((420, 275), 50, AMBER), ((620, 240), 43, GREEN), ((710, 185), 34, accent)]:
            draw.ellipse((c[0] - r, c[1] - r, c[0] + r, c[1] + r), fill=WHITE, outline=col, width=12)
            draw.ellipse((c[0] - 12, c[1] - 12, c[0] + 12, c[1] + 12), fill=INK)
        draw.arc((160, 255, 360, 455), 210, 330, fill=RED, width=6)
        draw.arc((365, 150, 505, 290), 200, 325, fill=AMBER, width=6)
        bolt_pattern(draw, center, 250, 150, 12, color=(95, 107, 116))
        label(draw, "6 DOF STUDY", (94, 128), accent, 24)
    elif variant == "pressure":
        rounded_rect(draw, (90, 210, 280, 420), 8, fill=WHITE, outline=INK, width=4)
        draw.arc((120, 245, 250, 375), 190, 350, fill=RED, width=8)
        draw.line((185, 310, 230, 282), fill=INK, width=6)
        draw.ellipse((177, 302, 193, 318), fill=INK)
        for x in [340, 475, 610]:
            rounded_rect(draw, (x, 235, x + 95, 365), 8, fill=WHITE, outline=INK, width=4)
            draw.line((x + 48, 365, x + 48, 445), fill=INK, width=5)
        draw.line((280, 315, 705, 315), fill=TEAL, width=12)
        draw.line((705, 315, 765, 230), fill=TEAL, width=10)
        draw.line((705, 315, 765, 410), fill=TEAL, width=10)
        for x in [325, 458, 592, 704]:
            draw.ellipse((x - 18, 297, x + 18, 333), fill=accent, outline=INK, width=4)
        label(draw, "CLOSED LOOP", (92, 128), accent, 24)
    elif variant == "software":
        rounded_rect(draw, (78, 145, 390, 420), 8, fill=WHITE, outline=INK, width=4)
        rounded_rect(draw, (430, 145, 810, 420), 8, fill=WHITE, outline=INK, width=4)
        for i, color in enumerate([RED, AMBER, GREEN]):
            draw.ellipse((105 + i * 32, 174, 124 + i * 32, 193), fill=color)
        for i, value in enumerate([0.78, 0.45, 0.91, 0.58]):
            y = 232 + i * 38
            draw.rectangle((116, y, 345, y + 18), outline=LINE, width=2)
            draw.rectangle((116, y, 116 + int(220 * value), y + 18), fill=[TEAL, RED, AMBER, GREEN][i])
        bubbles = [(485, 220, 695, 268), (545, 290, 765, 338), (490, 360, 655, 408)]
        for i, box in enumerate(bubbles):
            rounded_rect(draw, box, 8, fill=(235, 244, 245), outline=TEAL if i == 1 else LINE, width=3)
        label(draw, "AUTOMATION", (92, 128), accent, 24)
    elif variant == "racing":
        points = [(105, 365), (250, 265), (505, 245), (745, 345), (820, 415), (170, 430)]
        draw.line(points + [points[0]], fill=INK, width=8)
        for a, b in zip(points, points[1:] + [points[0]]):
            draw.line((a[0], a[1], b[0], b[1]), fill=INK, width=8)
        draw.line((250, 265, 170, 430, 505, 245, 745, 345), fill=TEAL, width=7)
        rounded_rect(draw, (355, 305, 585, 400), 8, fill=WHITE, outline=RED, width=5)
        for x, y in [(170, 430), (745, 345), (250, 265), (505, 245), (820, 415), (105, 365)]:
            draw.ellipse((x - 15, y - 15, x + 15, y + 15), fill=accent, outline=INK, width=3)
        label(draw, "STRUCTURES", (92, 128), accent, 24)
    elif variant == "competition":
        rounded_rect(draw, (150, 260, 560, 430), 8, fill=WHITE, outline=INK, width=5)
        for x in [190, 300, 410, 500]:
            draw.ellipse((x - 30, 400, x + 30, 460), fill=(60, 68, 74), outline=INK, width=5)
            draw.ellipse((x - 12, 418, x + 12, 442), fill=accent)
        draw.line((560, 300, 700, 250, 800, 300), fill=INK, width=14, joint="curve")
        draw.ellipse((782, 282, 818, 318), fill=accent, outline=INK, width=4)
        for i, x in enumerate([185, 260, 335, 410, 485]):
            draw.polygon([(x, 260), (x + 46, 260), (x + 23, 205)], fill=[RED, AMBER, TEAL, GREEN, RED][i])
        draw.rectangle((600, 400, 800, 460), outline=INK, width=5)
        draw.text((618, 415), "WORLDS", fill=INK, font=font(22, bold=True))
        label(draw, "COMP ROBOT", (92, 128), accent, 24)
    elif variant == "architecture":
        rounded_rect(draw, (140, 190, 760, 460), 8, fill=WHITE, outline=INK, width=5)
        draw.line((140, 330, 760, 330), fill=LINE, width=3)
        draw.line((300, 190, 300, 460), fill=LINE, width=3)
        draw.line((520, 190, 520, 460), fill=LINE, width=3)
        draw.polygon([(140, 330), (450, 190), (760, 330)], outline=accent, width=8)
        for x in [190, 260, 590, 660]:
            draw.rectangle((x, 360, x + 40, 460), outline=INK, width=4)
        draw.line((330, 460, 330, 400, 470, 400, 470, 460), fill=TEAL, width=6)
        for x, y, w2, h2 in [(365, 230, 70, 60), (455, 230, 70, 60)]:
            draw.rectangle((x, y, x + w2, y + h2), outline=RED, width=4)
        label(draw, "SITE PLAN", (92, 128), accent, 24)
    elif variant == "booth":
        rounded_rect(draw, (130, 180, 760, 470), 8, fill=WHITE, outline=INK, width=5)
        draw.line((170, 470, 210, 545), fill=INK, width=10)
        draw.line((720, 470, 690, 545), fill=INK, width=10)
        colors = [RED, AMBER, TEAL, GREEN]
        for i in range(9):
            x0 = 145 + i * 68
            draw.polygon([(x0, 180), (x0 + 54, 180), (x0 + 27, 250)], fill=colors[i % len(colors)])
        for x in [250, 360, 470, 580, 690]:
            draw.line((x, 292, x + 38, 400), fill=INK, width=8)
            draw.ellipse((x - 20, 270, x + 20, 310), fill=accent, outline=INK, width=3)
        draw.rectangle((220, 410, 680, 440), fill=INK)
        label(draw, "SIDE BUILDS", (92, 128), accent, 24)

    draw.rectangle((28, h - 70, w - 28, h - 28), fill=INK)
    draw.text((48, h - 60), "PLACEHOLDER MEDIA SLOT", fill=WHITE, font=font(19, bold=True))
    save(img, name)


def main():
    favicon()
    hero()
    project_canvas("MetaMobility Lab", "wearable robotics", TEAL, "metamobility-exoskeleton.png", "exo")
    project_canvas("Robotic Arm", "manipulator", RED, "robot-arm.png", "arm")
    project_canvas("Pressure Control", "internship", AMBER, "stem-cell-pressure-system.png", "pressure")
    project_canvas("Dogwood Systems", "automation", GREEN, "dogwood-automation.png", "software")
    project_canvas("CM Racing", "structures", RED, "racing-structures.png", "racing")
    project_canvas("Avenues Robotics", "competition", GREEN, "avenues-robotics.png", "competition")
    project_canvas("ACE GNY", "architecture", AMBER, "ace-gny.png", "architecture")
    project_canvas("Booth + Fun", "builds", TEAL, "booth-fun.png", "booth")


if __name__ == "__main__":
    main()
