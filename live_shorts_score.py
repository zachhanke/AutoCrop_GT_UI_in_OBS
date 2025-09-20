# obs_multi_crop_screenshot_loop.py
# pip install --upgrade obsws-python pillow

import base64, io, time, argparse, sys, os
from PIL import Image
from obsws_python import reqs

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def color_matches(pixel, target, tolerance):
    return all(abs(pixel[i] - target[i]) <= tolerance for i in range(3))

def load_crop_config(config_file):
    crops = []
    try:
        with open(config_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                try:
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) < 5:
                        print(f"Warning: Line {line_num} has insufficient parameters, skipping")
                        continue
                    x, y, w, h = map(int, parts[:4])
                    output_file = parts[4]
                    image_source = parts[5] if len(parts) > 5 else None
                    crops.append({
                        'x': x, 'y': y, 'w': w, 'h': h,
                        'output_file': output_file,
                        'image_source': image_source,
                        'line_num': line_num
                    })
                except (ValueError, IndexError) as e:
                    print(f"Warning: Error parsing line {line_num}: '{line}' - {e}")
                    continue
    except FileNotFoundError:
        print(f"Error: Config file '{config_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading config file: {e}")
        sys.exit(1)

    if not crops:
        print("Error: No valid crop configurations found")
        sys.exit(1)
    return crops

def get_pixel(image, x, y):
    if x is None or y is None:
        return None
    if 0 <= x < image.width and 0 <= y < image.height:
        return image.getpixel((x, y))[:3]
    print(f"Warning: coordinates ({x},{y}) out of bounds for screenshot {image.width}x{image.height}")
    return None

def main():
    p = argparse.ArgumentParser(description="Capture multiple cropped regions from OBS source with primary and secondary color checks")
    p.add_argument("--host", default="localhost")
    p.add_argument("--port", type=int, default=4455)
    p.add_argument("--password", required=True)
    p.add_argument("--source", required=True, help="Exact OBS source name to capture")

    # New: separate configs for true/false cases
    p.add_argument("--config_true", default="crop_config_true.txt", help="Crops when initial check is true")
    p.add_argument("--config_false", default="crop_config_false.txt", help="Crops when initial check is false but subcheck is true")

    # Back-compat: optional single config (ignored if the two above are present)
    p.add_argument("--config", default=None, help="Legacy single config (overridden by --config_true/--config_false if provided)")

    p.add_argument("--interval", type=float, default=10.0, help="Seconds between captures")

    # Initial check
    p.add_argument("--check_x", type=int, help="X for primary pixel check")
    p.add_argument("--check_y", type=int, help="Y for primary pixel check")
    p.add_argument("--check_color", help="Hex color for primary check, e.g. #FF0000 or FF0000")

    # Subcheck
    p.add_argument("--subcheck_x", type=int, help="X for secondary pixel check")
    p.add_argument("--subcheck_y", type=int, help="Y for secondary pixel check")
    p.add_argument("--subcheck_color", help="Hex color for secondary check, e.g. #00FF00 or 00FF00")

    p.add_argument("--color_tolerance", type=int, default=5, help="Tolerance for both checks (0-255)")

    p.add_argument("--debug", action="store_true", help="Save full screenshot before cropping")
    args = p.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Decide which configs to load
    config_true_path = os.path.join(script_dir, args.config_true) if args.config_true else None
    config_false_path = os.path.join(script_dir, args.config_false) if args.config_false else None

    # Legacy single-config path if true/false not specified
    if args.config and not (args.config_true or args.config_false):
        config_true_path = os.path.join(script_dir, args.config)
        config_false_path = None

    # Load crop sets
    crops_true = load_crop_config(config_true_path) if config_true_path else []
    crops_false = load_crop_config(config_false_path) if config_false_path else []

    print(f"Loaded {len(crops_true)} crops from {config_true_path if config_true_path else '(none)'}")
    if crops_false:
        print(f"Loaded {len(crops_false)} crops from {config_false_path}")

    # OBS connect
    try:
        c = reqs.ReqClient(host=args.host, port=args.port, password=args.password, timeout=5)
    except Exception as e:
        print(f"connect_failed: {e}", file=sys.stderr); sys.exit(1)

    # Try native size
    width = height = None
    try:
        si = c.get_input_settings(name=args.source)
        w = si.input_settings.get("width", 0)
        h = si.input_settings.get("height", 0)
        if w >= 8 and h >= 8:
            width, height = w, h
    except Exception:
        pass

    # Parse colors
    check_color_rgb = hex_to_rgb(args.check_color) if args.check_color else None
    subcheck_color_rgb = hex_to_rgb(args.subcheck_color) if args.subcheck_color else None

    if check_color_rgb is not None:
        print(f"Primary check at ({args.check_x},{args.check_y}) for {args.check_color} tol={args.color_tolerance}")
    if subcheck_color_rgb is not None:
        print(f"Secondary check at ({args.subcheck_x},{args.subcheck_y}) for {args.subcheck_color} tol={args.color_tolerance}")

    print(f"Capturing '{args.source}' every {args.interval}s")
    if args.debug:
        print("Debug mode: saving full screenshots")

    while True:
        try:
            # Screenshot
            if width and height and width >= 8 and height >= 8:
                shot = c.get_source_screenshot(name=args.source, img_format="png", width=width, height=height, quality=-1)
            else:
                shot = c.get_source_screenshot(name=args.source, img_format="png", width=1920, height=1080, quality=-1)

            b64 = shot.image_data
            if isinstance(b64, str) and b64.startswith("data:image"):
                b64 = b64.split(",", 1)[1]
            buf = base64.b64decode(b64)
            im = Image.open(io.BytesIO(buf)).convert("RGBA")

            if args.debug:
                debug_path = os.path.join(script_dir, "debug_full_screenshot.png")
                im.save(debug_path, format="PNG")
                print(f"Debug: Full screenshot saved to {debug_path}")

            # Decide which crop set to use
            use_true = False
            use_false = False

            # Primary check if provided
            if check_color_rgb is not None and args.check_x is not None and args.check_y is not None:
                pix = get_pixel(im, args.check_x, args.check_y)
                if pix is not None and color_matches(pix, check_color_rgb, args.color_tolerance):
                    use_true = True
                else:
                    # Subcheck if provided
                    if subcheck_color_rgb is not None and args.subcheck_x is not None and args.subcheck_y is not None:
                        spix = get_pixel(im, args.subcheck_x, args.subcheck_y)
                        if spix is not None and color_matches(spix, subcheck_color_rgb, args.color_tolerance):
                            use_false = True
                    # If no subcheck or it failed, skip this cycle
            else:
                # No checks configured -> default to true-set if present
                use_true = len(crops_true) > 0

            # Select crops
            selected_crops = crops_true if use_true else (crops_false if use_false else [])

            if not selected_crops:
                reason = "initial check failed and subcheck failed" if (check_color_rgb or subcheck_color_rgb) else "no crops selected"
                print(f"Screenshot skipped - {reason}")
                time.sleep(args.interval)
                continue

            # Process crops
            for crop_config in selected_crops:
                try:
                    x, y, w, h = crop_config['x'], crop_config['y'], crop_config['w'], crop_config['h']
                    output_file = crop_config['output_file']
                    image_source = crop_config['image_source']

                    if not os.path.isabs(output_file):
                        output_file = os.path.join(script_dir, output_file)

                    x = max(0, min(x, im.width))
                    y = max(0, min(y, im.height))
                    w = max(1, min(w, im.width - x))
                    h = max(1, min(h, im.height - y))

                    crop = im.crop((x, y, x + w, y + h))

                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    crop.save(output_file, format="PNG")

                    if image_source:
                        try:
                            cur = c.get_input_settings(name=image_source)
                            s = dict(cur.input_settings)
                            s["file"] = output_file
                            c.set_input_settings(name=image_source, settings=s, overlay=True)
                        except Exception as e:
                            print(f"Warning: Failed to update image source '{image_source}': {e}")

                except Exception as e:
                    print(f"Error processing crop from line {crop_config['line_num']}: {e}", file=sys.stderr)

        except Exception as e:
            print(f"capture_error: {e}", file=sys.stderr)

        time.sleep(args.interval)

if __name__ == "__main__":
    main()
