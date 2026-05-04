import os
from PIL import Image

def extract_mv_character(img, char_width=48, char_height=96):
    """
    Extracts specific frames from a 2688x1920 Modern Exteriors/Interiors 
    sprite sheet and formats them into a 144x384 RPG Maker MV character sheet.
    """
    # Create a blank 3x4 character sheet (144x384)
    char_sheet = Image.new("RGBA", (char_width * 3, char_height * 4), (0, 0, 0, 0))

    # Define source Y coordinates (Row 1 = 0, Row 3 = 2)
    idle_y = 0 * char_height
    walk_y = 2 * char_height

    # Helper function to crop a specific grid cell from the source image
    def get_frame(col, y_offset):
        left = col * char_width
        right = left + char_width
        return img.crop((left, y_offset, right, y_offset + char_height))

    # --- ROW 1: DOWN (Forward) ---
    # MV wants: [Walk 1, Idle, Walk 2]
    # Source Walk: Cols 18 to 23 (6 frames). Source Idle: Col 3
    char_sheet.paste(get_frame(18, walk_y), (0, 0))               # Step Left (Frame 1)
    char_sheet.paste(get_frame(3, idle_y),  (char_width, 0))      # Idle
    char_sheet.paste(get_frame(23, walk_y), (char_width * 2, 0))  # Step Right (Frame 6)

    # --- ROW 2: LEFT ---
    # Source Walk: Cols 12 to 17 (6 frames). Source Idle: Col 2
    char_sheet.paste(get_frame(12, walk_y), (0, char_height))
    char_sheet.paste(get_frame(2, idle_y),  (char_width, char_height))
    char_sheet.paste(get_frame(17, walk_y), (char_width * 2, char_height))

    # --- ROW 3: RIGHT ---
    # Source Walk: Cols 0 to 5 (6 frames). Source Idle: Col 0
    char_sheet.paste(get_frame(0, walk_y),  (0, char_height * 2))
    char_sheet.paste(get_frame(0, idle_y),  (char_width, char_height * 2))
    char_sheet.paste(get_frame(5, walk_y),  (char_width * 2, char_height * 2))

    # --- ROW 4: UP (Back) ---
    # Source Walk: Cols 6 to 11 (6 frames). Source Idle: Col 1
    char_sheet.paste(get_frame(6, walk_y),  (0, char_height * 3))
    char_sheet.paste(get_frame(1, idle_y),  (char_width, char_height * 3))
    char_sheet.paste(get_frame(11, walk_y),  (char_width * 2, char_height * 3))

    return char_sheet

def combine_batch(filepaths, output_filepath, char_width=48, char_height=96):
    """Parses and combines 8 raw source sheets into a single 4x2 grid."""
    
    # Final output dimensions (4 characters wide x 2 characters tall)
    # Each character is 3 frames wide (144px) and 4 frames tall (384px)
    SINGLE_SHEET_WIDTH = char_width * 3
    SINGLE_SHEET_HEIGHT = char_height * 4
    OUTPUT_WIDTH = SINGLE_SHEET_WIDTH * 4
    OUTPUT_HEIGHT = SINGLE_SHEET_HEIGHT * 2

    master_sheet = Image.new("RGBA", (OUTPUT_WIDTH, OUTPUT_HEIGHT), (0, 0, 0, 0))

    for i, filepath in enumerate(filepaths):
        try:
            # Load the massive 2688x1920 raw sheet
            raw_img = Image.open(filepath).convert("RGBA")
            
            # Optional check to warn if the source file isn't the expected size
            if raw_img.size != (2688, 1920):
                print(f"  -> Warning: {os.path.basename(filepath)} is {raw_img.size}, expected 2688x1920. Attempting to parse anyway.")

            # Extract and format the specific character
            formatted_char = extract_mv_character(raw_img, char_width, char_height)

            # Calculate grid position for the master sheet
            col = i % 4
            row = i // 4
            paste_x = col * SINGLE_SHEET_WIDTH
            paste_y = row * SINGLE_SHEET_HEIGHT

            master_sheet.paste(formatted_char, (paste_x, paste_y), formatted_char)

        except Exception as e:
            print(f"  -> Error processing {filepath}: {e}")
            return False

    try:
        master_sheet.save(output_filepath)
        return True
    except Exception as e:
        print(f"  -> Error saving {output_filepath}: {e}")
        return False

def main():
    RAW_DIR = "Raw"
    READY_DIR = "Game Ready"

    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(READY_DIR, exist_ok=True)

    all_files = sorted([f for f in os.listdir(RAW_DIR) if f.endswith('.png')])
    total_files = len(all_files)

    print("-" * 50)
    print("RPG Maker MV: Auto-Cropper & Batch Combiner (6-Frame Version)")
    print("-" * 50)

    if total_files == 0:
        print(f"No PNG files found in the '{RAW_DIR}' folder.")
        print("Please drop your raw 2688x1920 sheets in there and run again.")
        return

    print(f"Found {total_files} PNG files in '{RAW_DIR}'.\n")

    if total_files % 8 != 0:
        remainder = total_files % 8
        print(f"Warning: Files ({total_files}) are not a multiple of 8.")
        print(f"The last {remainder} file(s) will be ignored to ensure full sheets.\n")

    success_count = 0
    for i in range(0, total_files - (total_files % 8), 8):
        batch_files = all_files[i:i+8]
        batch_paths = [os.path.join(RAW_DIR, f) for f in batch_files]
        
        batch_number = (i // 8) + 1
        output_filename = f"Combined_Sprite_{batch_number:02d}.png"
        output_filepath = os.path.join(READY_DIR, output_filename)

        print(f"Processing Batch {batch_number}...")
        for file in batch_files:
            print(f"  + Cropping: {file}")

        if combine_batch(batch_paths, output_filepath):
            print(f"  => Successfully saved: {output_filename}\n")
            success_count += 1

    print("-" * 50)
    print(f"Finished! Processed {success_count * 8} raw images into {success_count} game-ready sheet(s).")
    print(f"Check the '{READY_DIR}' folder.")
    print("-" * 50)

if __name__ == "__main__":
    main()