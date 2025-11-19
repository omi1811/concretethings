"""Utility script to generate basic PWA icon assets."""
from pathlib import Path
from PIL import Image, ImageDraw

PUBLIC_DIR = Path(__file__).resolve().parent.parent / "public"
PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

ICON_SPECS = (
    (192, "#1D4ED8", "#DBEAFE"),
    (512, "#1D4ED8", "#DBEAFE"),
)

for size, primary_color, highlight_color in ICON_SPECS:
    canvas = Image.new("RGBA", (size, size), "#1E40AF")
    draw = ImageDraw.Draw(canvas)

    margin = int(size * 0.08)
    draw.rounded_rectangle(
        (margin, margin, size - margin, size - margin),
        radius=int(size * 0.18),
        fill=primary_color,
    )

    draw.rectangle(
        (
            int(size * 0.25),
            int(size * 0.35),
            int(size * 0.75),
            int(size * 0.55),
        ),
        fill=highlight_color,
    )

    draw.rectangle(
        (
            int(size * 0.3),
            int(size * 0.6),
            int(size * 0.48),
            int(size * 0.78),
        ),
        fill="#93C5FD",
    )

    draw.rectangle(
        (
            int(size * 0.52),
            int(size * 0.6),
            int(size * 0.7),
            int(size * 0.78),
        ),
        fill="#3B82F6",
    )

    output_path = PUBLIC_DIR / f"icon-{size}.png"
    canvas.save(output_path)
    print(f"Generated {output_path}")
