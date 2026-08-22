#!/usr/bin/env python3
"""Build Ezra Kahn's recruiter-facing engineering portfolio PDF."""

from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageOps
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "portfolio" / "Ezra-Kahn-Engineering-Portfolio.pdf"
PAGE_W, PAGE_H = landscape(letter)

BG = HexColor("#F3F1EB")
INK = HexColor("#10151A")
MUTED = HexColor("#687583")
TEAL = HexColor("#0D8290")
RED = HexColor("#D84C5F")
PALE_BLUE = HexColor("#E7F1F3")
PALE_GRAY = HexColor("#E7E9EE")
LINE = HexColor("#CAD7DA")
CARD = HexColor("#FBFAF7")


def asset(path: str) -> Path:
    result = ROOT / path
    if not result.exists():
        raise FileNotFoundError(result)
    return result


def normalized_image(path: Path) -> Path:
    """Normalize camera orientation metadata for ReportLab image rendering."""
    with Image.open(path) as source:
        orientation = source.getexif().get(274, 1)
        if orientation == 1:
            return path
        normalized = ImageOps.exif_transpose(source)
        normalized_dir = ROOT / "tmp" / "pdfs" / "normalized"
        normalized_dir.mkdir(parents=True, exist_ok=True)
        output = normalized_dir / path.name
        save_args = {"quality": 95} if output.suffix.lower() in {".jpg", ".jpeg"} else {}
        normalized.save(output, **save_args)
        return output


def fit_image(path: Path, box_w: float, box_h: float):
    path = normalized_image(path)
    with Image.open(path) as image:
        image_w, image_h = image.size
    scale = min(box_w / image_w, box_h / image_h)
    return image_w * scale, image_h * scale


def draw_image_contain(c, path: Path, x, y, w, h, pad=8, background=white):
    path = normalized_image(path)
    c.setFillColor(background)
    c.roundRect(x, y, w, h, 10, fill=1, stroke=0)
    image_w, image_h = fit_image(path, w - 2 * pad, h - 2 * pad)
    c.drawImage(
        str(path),
        x + (w - image_w) / 2,
        y + (h - image_h) / 2,
        width=image_w,
        height=image_h,
        preserveAspectRatio=True,
        mask="auto",
    )


def draw_image_cover(c, path: Path, x, y, w, h):
    path = normalized_image(path)
    with Image.open(path) as image:
        image_w, image_h = image.size
    scale = max(w / image_w, h / image_h)
    scaled_w, scaled_h = image_w * scale, image_h * scale
    c.saveState()
    clip = c.beginPath()
    clip.roundRect(x, y, w, h, 12)
    c.clipPath(clip, stroke=0, fill=0)
    c.drawImage(
        str(path),
        x + (w - scaled_w) / 2,
        y + (h - scaled_h) / 2,
        width=scaled_w,
        height=scaled_h,
        preserveAspectRatio=True,
        mask="auto",
    )
    c.restoreState()


def wrapped_lines(text, font, size, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if stringWidth(candidate, font, size) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_text(c, text, x, y, max_width, font="Helvetica", size=10.5, leading=14, color=MUTED):
    c.setFillColor(color)
    c.setFont(font, size)
    for line in wrapped_lines(text, font, size, max_width):
        c.drawString(x, y, line)
        y -= leading
    return y


def draw_bullets(c, items, x, y, max_width, size=9.5, leading=12.5, gap=5):
    for item in items:
        c.setFillColor(RED)
        c.circle(x + 3, y + 3, 2.2, fill=1, stroke=0)
        y = draw_text(c, item, x + 14, y + 7, max_width - 14, size=size, leading=leading, color=MUTED)
        y -= gap
    return y


def draw_chips(c, labels, x, y, max_width, fill=PALE_GRAY):
    cursor_x = x
    cursor_y = y
    for label in labels:
        font, size = "Helvetica-Bold", 7.5
        chip_w = stringWidth(label, font, size) + 18
        if cursor_x + chip_w > x + max_width:
            cursor_x = x
            cursor_y -= 23
        c.setFillColor(fill)
        c.roundRect(cursor_x, cursor_y - 13, chip_w, 18, 5, fill=1, stroke=0)
        c.setFillColor(MUTED)
        c.setFont(font, size)
        c.drawString(cursor_x + 9, cursor_y - 7, label)
        cursor_x += chip_w + 7
    return cursor_y - 23


def draw_link(c, label, url, x, y, size=9, color=RED):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", size)
    c.drawString(x, y, label)
    width = stringWidth(label, "Helvetica-Bold", size)
    c.line(x, y - 2, x + width, y - 2)
    c.linkURL(url, (x, y - 4, x + width, y + size + 2), relative=0)


def page_base(c, number, section=None):
    c.setFillColor(BG)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.7)
    c.line(34, 27, PAGE_W - 34, 27)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7.5)
    c.drawString(34, 14, "EZRA KAHN  |  ENGINEERING PORTFOLIO")
    if section:
        c.drawCentredString(PAGE_W / 2, 14, section.upper())
    c.drawRightString(PAGE_W - 34, 14, f"{number:02d}")


def page_title(c, eyebrow, title, subtitle=None):
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(38, PAGE_H - 49, eyebrow.upper())
    c.setFillColor(INK)
    c.setFont("Times-Bold", 27)
    c.drawString(38, PAGE_H - 83, title)
    y = PAGE_H - 103
    if subtitle:
        y = draw_text(c, subtitle, 38, y, PAGE_W - 76, size=10.5, leading=14, color=MUTED)
    return y


def section_label(c, label, x, y):
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(x, y, label.upper())
    return y - 17


def new_page(c, page_number, section):
    c.showPage()
    page_base(c, page_number, section)


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=(PAGE_W, PAGE_H))
    c.setTitle("Ezra Kahn - Engineering Portfolio")
    c.setAuthor("Ezra Kahn")
    c.setSubject("Mechanical engineering and robotics portfolio")

    # 01 - Cover
    page_base(c, 1, "Portfolio")
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(44, PAGE_H - 58, "MECHANICAL ENGINEERING + ROBOTICS")
    c.setFillColor(INK)
    c.setFont("Times-Bold", 48)
    c.drawString(44, PAGE_H - 114, "Ezra Kahn")
    c.setFont("Times-Bold", 27)
    c.drawString(44, PAGE_H - 153, "Engineering Portfolio")
    y = draw_text(
        c,
        "B.S. Mechanical Engineering, Robotics Minor, Carnegie Mellon University",
        44,
        PAGE_H - 184,
        390,
        font="Helvetica-Bold",
        size=11,
        leading=15,
        color=MUTED,
    )
    y -= 17
    y = draw_text(
        c,
        "I design mechanical and robotic systems that turn difficult human needs into testable, manufacturable engineering solutions. My work spans wearable robotics, sensing hardware, embedded control, automation, and rapid fabrication.",
        44,
        y,
        395,
        font="Times-Roman",
        size=14,
        leading=20,
        color=INK,
    )
    draw_chips(c, ["SolidWorks", "ROS 2", "Python", "Embedded Systems", "Rapid Prototyping"], 44, y - 20, 405, PALE_BLUE)
    draw_image_cover(c, asset("assets/generated/ezra-kahn-portrait.png"), 500, 106, 236, 370)
    draw_link(c, "ezraikahn.com", "https://ezraikahn.com/", 44, 82, 10)
    draw_link(c, "GitHub", "https://github.com/eikahn922", 155, 82, 10)
    draw_link(c, "LinkedIn", "https://www.linkedin.com/in/ezra-i-kahn/", 216, 82, 10)
    draw_link(c, "eikahn@andrew.cmu.edu", "mailto:eikahn@andrew.cmu.edu", 294, 82, 10)

    # 02 - Portfolio map
    new_page(c, 2, "Selected Work")
    page_title(c, "Selected work", "Engineering across the full build cycle", "Research, design, implementation, and validation presented in a compact recruiter-ready format.")
    cards = [
        ("01", "Wearable Robotics Research", "Electronics packaging and adjustable IMU placement for hip-knee exoskeletons.", "03-04"),
        ("02", "Hip Exoskeleton Interfaces", "A passive thighbar and a rapid motor-stability strap solution.", "05-06"),
        ("03", "Engineering Internships", "Operational software systems at Dogwood Brands and closed-loop gas control at NYSCF.", "07-08"),
        ("04", "Personal Robotics", "Mechanical design, torque sizing, ROS 2 modeling, and Python launch tooling for a 3-DOF arm.", "09"),
        ("05", "Teams and Fabrication", "Academic engineering teams and leading a public two-story build under a one-week schedule.", "10-11"),
    ]
    x_positions = [38, 292, 546]
    for index, (num, title, desc, pages) in enumerate(cards):
        row, col = divmod(index, 3)
        x = x_positions[col]
        y_top = 430 - row * 186
        c.setFillColor(CARD)
        c.setStrokeColor(LINE)
        c.roundRect(x, y_top - 145, 216, 145, 12, fill=1, stroke=1)
        c.setFillColor(RED)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(x + 16, y_top - 21, num)
        c.drawRightString(x + 200, y_top - 21, f"PAGES {pages}")
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 13)
        draw_text(c, title, x + 16, y_top - 48, 184, font="Helvetica-Bold", size=13, leading=16, color=INK)
        draw_text(c, desc, x + 16, y_top - 82, 184, size=8.5, leading=11.5, color=MUTED)

    # 03 - Distributed electronics packaging
    new_page(c, 3, "Wearable Robotics Research")
    page_title(c, "MetaMobility Lab | June 2026-Present", "Distributed Electronics Packaging", "Compact, serviceable hardware for a distributed exoskeleton communications architecture.")
    left_x, left_w = 38, 340
    right_x, right_w = 402, 352
    y = section_label(c, "Problem and contribution", left_x, 442)
    y = draw_text(c, "I designed and fabricated enclosures that keep computation close to each IMU, reducing long cable runs across the wearable system.", left_x, y, left_w, size=10.5, leading=14, color=INK)
    y -= 12
    y = section_label(c, "Packaging requirements", left_x, y)
    y = draw_bullets(c, [
        "Lightweight and fast to 3D print.",
        "Shield status LEDs from infrared motion-capture cameras while preserving debug access.",
        "Keep connectors accessible, transfer cable loads into the housing, and avoid loading surface-mounted components.",
    ], left_x, y, left_w)
    y -= 8
    y = section_label(c, "Architecture evolution", left_x, y)
    draw_text(c, "The final QT Py and IMU package reduced enclosure size while preserving connector access, LED shielding, strain relief, and serviceability.", left_x, y, left_w, size=9.5, leading=13)
    draw_chips(c, ["SolidWorks", "3D Printing", "Sensor Integration", "Rapid Prototyping"], left_x, 91, left_w)
    draw_link(c, "View the full research repository", "https://github.com/eikahn922/exoskeleton_SensorPlacementProject", left_x, 55)
    draw_image_contain(c, asset("assets/projects/distributed-computing/teensy-imu-can-cad.png"), right_x, 292, 169, 145)
    draw_image_contain(c, asset("assets/projects/distributed-computing/prototype-wiring.jpg"), right_x + 183, 292, 169, 145)
    draw_image_contain(c, asset("assets/projects/distributed-computing/qtpy-imu-cad.png"), right_x, 109, 169, 145)
    draw_image_contain(c, asset("assets/projects/distributed-computing/prototype-enclosure.jpg"), right_x + 183, 109, 169, 145)
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(right_x, 448, "TEENSY + IMU + CAN PAL: CAD AND FABRICATED")
    c.drawString(right_x, 265, "QT PY + IMU: CAD AND FABRICATED")

    # 04 - Adjustable IMU positioning
    new_page(c, 4, "Wearable Robotics Research")
    page_title(c, "Sensor placement research", "Adjustable IMU Mounts", "Comparable sensor position and orientation across body sizes may reduce setup-driven variation and improve cross-participant model transfer.")
    cols = [38, 290, 542]
    items = [
        ("Shin", "Adjusts along the leg and around the cuff. A strap and foam interface limit slip while preserving fit adjustment.", "assets/projects/distributed-computing/shin-imu-cuff-integration.png", "In development"),
        ("Thigh", "A captured strap guide moves vertically and laterally. Retention hardware bounds travel and holds the selected position.", "assets/projects/distributed-computing/thigh-cuff-assembly-zoomed-out.png", "Version 2 CAD"),
        ("Pelvis", "A slider positions the IMU along the back plate and locks it relative to the exoskeleton. A static version remains the comparison baseline.", "assets/projects/distributed-computing/pelvis-adjustable-imu-full-system.png", "Completed CAD"),
    ]
    for x, (title, desc, image, status) in zip(cols, items):
        c.setFillColor(RED)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(x, 435, status.upper())
        c.setFillColor(INK)
        c.setFont("Times-Bold", 20)
        c.drawString(x, 405, title)
        draw_image_contain(c, asset(image), x, 205, 212, 175)
        draw_text(c, desc, x, 179, 212, size=9.5, leading=13, color=MUTED)
    c.setFillColor(PALE_BLUE)
    c.roundRect(38, 52, 716, 78, 10, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(54, 108, "RESEARCH QUESTION")
    draw_text(c, "Can adjustable sensor mounts produce more repeatable placement across participants and, in turn, more transferable gait-sensing algorithms? The mechanical systems are designed; comparative testing will quantify the benefit.", 54, 88, 684, size=9.5, leading=13, color=MUTED)

    # 05 - Thighbar
    new_page(c, 5, "Hip Exoskeleton Interfaces")
    page_title(c, "April-May 2026 | Final CAD release", "Hip Exoskeleton Thighbar", "A lightweight thigh interface with one passive translational degree of freedom for gait-driven misalignment compensation.")
    draw_image_contain(c, asset("assets/projects/thigh-bar/prismatic-thighbar-cover.png"), 404, 122, 350, 310)
    y = section_label(c, "What I designed", 38, 429)
    y = draw_text(c, "I designed a wraparound thighbar that connects the hip exoskeleton to the wearer. A guided prismatic rail lets the interface move vertically during gait, absorbing relative motion instead of forcing it into the leg.", 38, y, 332, size=10.5, leading=14, color=INK)
    y -= 15
    y = section_label(c, "Design requirements", 38, y)
    y = draw_bullets(c, [
        "Wrap securely and comfortably around the thigh.",
        "Allow controlled vertical travel without binding.",
        "Add misalignment compensation without another actuator or substantial added mass.",
    ], 38, y, 332)
    y -= 10
    y = section_label(c, "Outcome", 38, y)
    draw_text(c, "The final assembly combines the thigh wrap, slider, and exoskeleton connection in a compact serviceable mechanism that passively follows the wearer through gait.", 38, y, 332, size=9.5, leading=13)
    draw_chips(c, ["SolidWorks", "Wearable Interface Design", "Research Synthesis"], 38, 93, 332)
    draw_link(c, "View the full thighbar project", "https://github.com/eikahn922/exoskeleton_thighBar", 38, 55)

    # 06 - Motor stability
    new_page(c, 6, "Hip Exoskeleton Interfaces")
    page_title(c, "February-March 2026 | Temporary solution", "Motor-Stability Strap Attachments", "A rapid, reversible support created while the hip-exoskeleton pelvis was being repaired.")
    draw_image_contain(c, asset("assets/projects/motor-stability/adjustable-test-setup.png"), 404, 294, 168, 145)
    draw_image_contain(c, asset("assets/projects/motor-stability/cover.png"), 586, 294, 168, 145)
    draw_image_contain(c, asset("assets/projects/motor-stability/full-system-view-1.png"), 404, 108, 168, 145)
    draw_image_contain(c, asset("assets/projects/motor-stability/final-close-up-2.png"), 586, 108, 168, 145)
    y = section_label(c, "Need", 38, 430)
    y = draw_text(c, "A pelvis issue allowed the motor assembly to separate from its support. I created a strap interface to stabilize it until the pelvis repair was complete.", 38, y, 332, size=10.5, leading=14, color=INK)
    y -= 13
    y = section_label(c, "Test method", 38, y)
    y = draw_text(c, "A repositionable fixture compared strap locations. I then checked the selected layout in the full exoskeleton for fit, access, visible motion, and component interference.", 38, y, 332, size=9.5, leading=13)
    y -= 13
    y = section_label(c, "Outcome", 38, y)
    draw_text(c, "Testing identified and documented the preferred strap location in final CAD. The temporary support was ultimately unnecessary because the pelvis issue was resolved a few days after testing.", 38, y, 332, size=9.5, leading=13)
    draw_chips(c, ["SolidWorks", "Design Testing", "Rapid Problem Solving"], 38, 93, 332)
    draw_link(c, "View the motor-stability project", "https://github.com/eikahn922/exoskeleton_MotorStability", 38, 55)

    # 07 - Dogwood
    new_page(c, 7, "Engineering Internships")
    page_title(c, "Dogwood Brands | May 2025-Jan 2026", "Software Engineering Intern", "Internal automation and data systems for a boutique private equity firm operating consumer and franchise businesses.")
    draw_image_cover(c, asset("assets/projects/dogwood/dogwood-team.jpg"), 446, 278, 308, 165)
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(446, 458, "THE DOGWOOD BRANDS TEAM")
    projects = [
        ("KPI reporting", "Automated daily performance reporting for more than 60 Supercuts locations using Python and advanced Excel workflows."),
        ("Vendor web scraper", "Built a traceable Python pipeline for PDF, Excel, and CSV inputs that enriches vendor data from public websites and returns source URLs, confidence ratings, and review notes."),
        ("AI-powered HR chatbot", "Led implementation work with teammates in Pakistan and India, coordinating responsibilities across time zones and connecting technical decisions to recruiting needs."),
    ]
    y = 434
    for title, desc in projects:
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(38, y, title)
        y = draw_text(c, desc, 38, y - 19, 370, size=9.2, leading=12.5)
        y -= 13
    c.setFillColor(PALE_BLUE)
    c.roundRect(446, 101, 308, 145, 10, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(462, 221, "What the role developed")
    draw_bullets(c, [
        "Ownership of ambiguous, business-facing technical work.",
        "Team leadership and stakeholder alignment.",
        "Python, advanced Excel, web scraping, and data analytics.",
    ], 462, 194, 276, size=8.8, leading=11.5, gap=4)
    draw_chips(c, ["Python", "Advanced Excel", "Data Analytics", "Team Leadership"], 38, 90, 370)
    draw_link(c, "View public scraper", "https://github.com/eikahn922/webscraper", 38, 55)
    draw_link(c, "Visit Dogwood Brands", "https://dogwoodbrands.com/", 161, 55)

    # 08 - NYSCF
    new_page(c, 8, "Engineering Internships")
    page_title(c, "New York Stem Cell Foundation | Jun-Aug 2023", "Digital Gas-Pressure Control", "A prototype architecture for replacing manual adjustment with continuous sensing and closed-loop control on the NYSCF Array.")
    draw_image_contain(c, asset("assets/generated/nyscf-gas-pressure-poster.jpg"), 475, 95, 279, 345)
    y = section_label(c, "System architecture", 38, 433)
    y = draw_bullets(c, [
        "Integrated pressure, CO2, and O2 sensing through analog inputs and I2C communication.",
        "Mapped outputs to proportional valves for CO2, O2, and N2 flow.",
        "Designed a compact CAD housing for the gas-sensing hardware.",
    ], 38, y, 395)
    y -= 10
    y = section_label(c, "Control approach", 38, y)
    y = draw_text(c, "The prototype firmware runs a PID pressure loop with separate PI corrections for CO2 and O2. Remaining demand is assigned to nitrogen. Safety logic closes every valve if sensor data fails, becomes stale, or pressure exceeds the limit.", 38, y, 395, size=9.5, leading=13, color=INK)
    y -= 13
    y = section_label(c, "Confidentiality", 38, y)
    draw_text(c, "The public repository contains the prototype control algorithm and safeguards. All other implementation files remain confidential.", 38, y, 395, size=9.2, leading=12.5)
    draw_chips(c, ["Embedded C++", "PID/PI Control", "Sensor Integration", "SolidWorks"], 38, 90, 395)
    draw_link(c, "View the public control algorithm", "https://github.com/eikahn922/NYSCF-Gas-Pressure-Regulator-Code-", 38, 55)

    # 09 - Robot arm
    new_page(c, 9, "Personal Robotics")
    page_title(c, "June 2026-Present | In development", "3-DOF Robotic Arm", "Mechanical design, torque sizing, ROS 2 modeling, and Python launch tooling for a lightweight pick-and-place arm.")
    draw_image_contain(c, asset("assets/projects/robotic-arm/ros-kinematic-model.png"), 434, 279, 150, 162)
    draw_image_contain(c, asset("assets/projects/robotic-arm/solidworks-assembly.png"), 598, 279, 156, 162)
    draw_image_contain(c, asset("assets/projects/robotic-arm/ros-joint-state-demo-poster.png"), 434, 104, 320, 142, background=HexColor("#202428"))
    y = section_label(c, "Mechanical design", 38, 435)
    y = draw_text(c, "The SolidWorks assembly separates the base, waist, structural links, servo models, and geared gripper. PLA mass properties and center-of-mass locations feed the joint-load calculations.", 38, y, 360, size=9.5, leading=13, color=INK)
    y -= 9
    y = draw_text(c, "With a 10 g payload and 2.0 safety factor, the required torque is 7.65 kgf-cm at the shoulder and 3.88 kgf-cm at the elbow.", 38, y, 360, size=9.2, leading=12.5)
    y -= 15
    y = section_label(c, "ROS 2 model", 38, y)
    y = draw_text(c, "A five-link URDF/Xacro chain defines three revolute joints, axes, limits, origins, and transforms using the SolidWorks meshes. A Python launch file starts the state publishers and RViz together; the model is verified through RViz and the TF tree.", 38, y, 360, size=9.5, leading=13)
    y -= 14
    y = section_label(c, "Next validation", 38, y)
    draw_text(c, "The planned build uses an ESP32, PCA9685 PWM driver, separate fused 6 V servo rail, joint calibration, coordinated motion, and repeated pick-and-place testing.", 38, y, 360, size=9.2, leading=12.5)
    draw_chips(c, ["SolidWorks", "ROS 2", "Python", "URDF/Xacro", "Torque Analysis"], 38, 90, 360)
    draw_link(c, "View the project repository", "https://github.com/eikahn922/Robotic-Arm-project", 38, 55)
    draw_link(c, "Watch the motion demonstration", "https://ezraikahn.com/projects/robotic-arm.html#robotic-arm-video-title", 205, 55)

    # 10 - Academic activities
    new_page(c, 10, "Academic Engineering Teams")
    page_title(c, "Carnegie Mellon and FIRST Robotics", "Team-Based Engineering", "Mechanical design and leadership in multidisciplinary competition environments.")
    teams = [
        ("Carnegie Mellon Racing", "Structures and Electrical Integration", [
            "Model battery-enclosure components in SolidWorks while satisfying structural, packaging, and electrical-integration requirements.",
            "Coordinate enclosure geometry, component placement, and system interfaces across structures and electrical teams.",
        ], "CURRENT"),
        ("Avenues Robotics", "Mechanical Subteam Lead", [
            "Led mechanical design, fabrication, and iterative testing for competition robots.",
            "Helped develop systems that qualified for the World Championships, reached by approximately the top 2.5% of teams.",
        ], "2021-2024"),
    ]
    for i, (title, role, bullets, date) in enumerate(teams):
        x = 38 + i * 362
        c.setFillColor(CARD)
        c.setStrokeColor(LINE)
        c.roundRect(x, 125, 332, 309, 12, fill=1, stroke=1)
        c.setFillColor(RED)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(x + 20, 409, date)
        c.setFillColor(INK)
        c.setFont("Times-Bold", 23)
        c.drawString(x + 20, 370, title)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x + 20, 344, role)
        draw_bullets(c, bullets, x + 20, 309, 292, size=9.5, leading=13, gap=12)
        draw_chips(c, ["Teamwork", "Mechanical Design", "Iterative Testing"], x + 20, 166, 292)

    # 11 - Booth
    new_page(c, 11, "Building for Fun")
    page_title(c, "CMU Spring Carnival | 2025 and 2026", "Booth Manufacturing and Building Lead", "Led the construction of two public, multi-story wooden structures that placed 2nd and 3rd in the fraternity division.")
    draw_image_cover(c, asset("assets/projects/booth/finished-facade.jpg"), 428, 278, 158, 160)
    draw_image_cover(c, asset("assets/projects/booth/wall-framing-layout.jpg"), 600, 278, 154, 160)
    draw_image_cover(c, asset("assets/projects/booth/second-story-framing.jpg"), 428, 104, 326, 142)
    y = section_label(c, "One-week public build", 38, 430)
    y = draw_text(c, "Everything moved onto Midway the Friday before Carnival and had to open the next Thursday. I ran the build through framing plans, cut lists, wall layout, assembly, second-story construction, and final facade work.", 38, y, 350, size=10, leading=13.5, color=INK)
    y -= 14
    y = section_label(c, "Leadership under constraints", 38, y)
    y = draw_text(c, "I kept a rotating volunteer crew productive and safe while coordinating the sequence of dependent work. Walls had to be squared and sheathed before the deck, the deck before the second story, and painting after the structure stopped moving.", 38, y, 350, size=9.5, leading=13)
    y -= 14
    y = section_label(c, "Results", 38, y)
    draw_text(c, "The 2025 and 2026 builds placed 2nd and 3rd in the fraternity division, respectively.", 38, y, 350, size=9.5, leading=13)
    draw_chips(c, ["Fabrication", "Shop Drawings", "Assembly Sequencing", "Team Leadership"], 38, 90, 350)
    draw_link(c, "View the full build story", "https://ezraikahn.com/projects/booth.html", 38, 55)

    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()
