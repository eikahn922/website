# Ezra Kahn Portfolio Website

Static personal portfolio site for mechanical engineering, robotics, lab, internship, software, and side-build project placeholders.

## Structure

- `index.html` - single-page portfolio content, grouped into About/Links, Work (by category), Experience, and a closing contact section
- `styles.css` - responsive styling and layout
- `script.js` - footer year and icon rendering
- `assets/generated/` - local PNG placeholder visuals
- `assets/resume/` - resume PDF linked from the hero, About, and contact sections
- `tools/generate_assets.py` - regenerates the placeholder images

## Local Preview

```bash
python3 -m http.server 8080
```

Then open `http://localhost:8080`.

## GitHub Pages

This repo is configured as a static site. In GitHub, enable Pages from the `main` branch and root directory.

## Update Projects

Replace the project card text and PNGs as real project photos, CAD renders, videos, writeups, and code links become available.
