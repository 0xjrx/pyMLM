#!/usr/bin/env python3
import argparse
import csv
import logging
import os
import sys

def create_parser():
    parser = argparse.ArgumentParser(
        description='Music library parser and organizer, USE AT YOUR OWN RISK :)\nIndexing follows the structure "Library/Artist/Album/Tracks" ',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Global arguments
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '-d', '--directory',
        default='Test',
        help='Directory to walk (default: Test)'
    )
    
    parser.add_argument(
        '-i', '--index',
        action='store_true',
        help='Enable folder and file indexing only' 
    )
    
    parser.add_argument(
        '-r', '--rename',
        action='store_true',
        help='Folder renaming (includes indexing)' 
    )
    
    parser.add_argument(
        '-o', '--output',
        default=os.path.join('index', 'album_index.md'),
        help='Index output file (default: index/album_index.md)'
    )
    
    return parser

def main():
    """Main function."""
    parser = create_parser()
    args = parser.parse_args()
    
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(levelname)s: %(message)s')
    
    target_dir = args.directory
    
    if not os.path.exists(target_dir):
        logging.error(f"Directory '{target_dir}' does not exist.")
        return 1
        
    logging.info(f"Scanning music library in: {target_dir}")
    
    try:
        artists = os.listdir(target_dir)
    except Exception as e:
        logging.error(f"Failed to read directory: {e}")
        return 1
        
    artist_dirs = [a for a in artists if os.path.isdir(os.path.join(target_dir, a))]
    
    if not artist_dirs:
        logging.info("No artist directories found.")
        return 0
        
    is_csv = args.output.lower().endswith('.csv')
    
    markdown_content = "# Music Library Index\n\n"
    csv_rows = []
    
    if args.rename:
        print("\nProcessing and renaming albums by artist...")
        
        for artist in artist_dirs:
            artist_path = os.path.join(target_dir, artist)
            
            try:
                albums = os.listdir(artist_path)
            except Exception as e:
                logging.error(f"Failed to read artist folder '{artist}': {e}")
                continue
                
            album_dirs = [al for al in albums if os.path.isdir(os.path.join(artist_path, al))]
            
            if album_dirs and not is_csv:
                markdown_content += f"## {artist}\n"
                
            for album in album_dirs:
                old_album_path = os.path.join(artist_path, album)
                
                if "[DIGITAL]" in album or "[CD]" in album:
                    print(f"Skipping already tagged album: {album}")
                    new_album_name = album
                else:
                    print(f"\n--- Artist: {artist} ---")
                    print(f"Found Album: {album}")
                    var = input("Is this (1) CD rip or (2) DIGITAL? (Enter 1 or 2): ").strip()
                    
                    if var == "1":
                        new_album_name = f"{album} [CD]"
                    elif var == "2":
                        new_album_name = f"{album} [DIGITAL]"
                    else:
                        logging.warning("Invalid choice. Keeping original name.")
                        new_album_name = album
                
                # Separate
                if "[CD]" in new_album_name:
                    clean_title = new_album_name.replace(" [CD]", "").strip()
                    fmt = "CD"
                elif "[DIGITAL]" in new_album_name:
                    clean_title = new_album_name.replace(" [DIGITAL]", "").strip()
                    fmt = "DIGITAL"
                else:
                    clean_title = new_album_name
                    fmt = "Unknown"

                markdown_content += f"- {new_album_name}\n"
                new_album_path = os.path.join(artist_path, new_album_name)
                
                # Rename folder first so we can scan tracks from the correct path
                try:
                    if old_album_path != new_album_path:
                        os.rename(old_album_path, new_album_path)
                        logging.info(f"Successfully renamed album to: {new_album_name}")
                except Exception as e:
                    logging.error(f"Could not rename album '{album}': {e}")
                
                # Collect track files inside the album directory
                try:
                    album_contents = os.listdir(new_album_path)
                    tracks = [item for item in album_contents if os.path.isfile(os.path.join(new_album_path, item))]
                except Exception:
                    tracks = []

                if is_csv:
                    if tracks:
                        for track in tracks:
                            csv_rows.append([artist, clean_title, fmt, track])
                    else:
                        # Fallback
                        csv_rows.append([artist, clean_title, fmt, ""])

            if album_dirs and not is_csv:
                markdown_content += "\n"

    elif args.index:
        print("\nGenerating library index...")
        
        for artist in artist_dirs:
            artist_path = os.path.join(target_dir, artist)
            try:
                albums = os.listdir(artist_path)
            except Exception:
                continue
                
            album_dirs = [al for al in albums if os.path.isdir(os.path.join(artist_path, al))]
            
            if album_dirs:
                if not is_csv:
                    markdown_content += f"## {artist}\n"
                
                for album in album_dirs:
                    if "[CD]" in album:
                        clean_title = album.replace(" [CD]", "").strip()
                        fmt = "CD"
                    elif "[DIGITAL]" in album:
                        clean_title = album.replace(" [DIGITAL]", "").strip()
                        fmt = "DIGITAL"
                    else:
                        clean_title = album
                        fmt = "Unknown"
                        
                    markdown_content += f"- {album}\n"
                    
                    album_path = os.path.join(artist_path, album)
                    try:
                        album_contents = os.listdir(album_path)
                        tracks = [item for item in album_contents if os.path.isfile(os.path.join(album_path, item))]
                    except Exception:
                        tracks = []
                        
                    if is_csv:
                        if tracks:
                            for track in tracks:
                                csv_rows.append([artist, clean_title, fmt, track])
                        else:
                            csv_rows.append([artist, clean_title, fmt, ""])
                    
                if not is_csv:
                    markdown_content += "\n"
    else:
        print("Please specify an action flag: -r/--rename (to rename and index) or -i/--index (to index only).")
        return 0

    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    if is_csv:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Artist", "Album", "Format", "Track"])
            writer.writerows(csv_rows)
        logging.info(f"CSV index successfully written to {args.output}")
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        logging.info(f"Markdown index successfully written to {args.output}")
        
    return 0

if __name__ == '__main__':
    sys.exit(main())