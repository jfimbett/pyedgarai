import os
import json
import argparse
import shutil
import sys

def get_relative_path(base, path):
    """
    Calculates the relative path of a module for import statements.
    """
    try:
        # This is tricky. A robust solution uses AST, but for now, a heuristic:
        if 'src' in base:
            base = base.split('src' + os.sep)[1]
        
        parts = base.split(os.sep)
        if parts[-1] == '__init__.py':
            parts.pop()
        
        return '.'.join(parts)
    except Exception:
        return base.replace(os.sep, '.')


def update_references(move_map, dry_run=False):
    """
    Find and replace file paths and import statements in all project files.
    """
    print("\n[INFO] Starting import and path reference updates...")
    
    # Invert map for easier lookup
    inverse_move_map = {v: k for k, v in move_map.items()}
    
    # Get all text-based files to scan
    files_to_scan = []
    for root, _, files in os.walk('.'):
        if 'archive' in root or '.git' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith(('.py', '.md', '.ipynb', '.txt', '.json')):
                files_to_scan.append(os.path.join(root, file))

    for file_path in files_to_scan:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (IOError, UnicodeDecodeError) as e:
            print(f"[WARN] Could not read {file_path}: {e}")
            continue

        original_content = content

        for new_path, old_path in inverse_move_map.items():
            # 1. Update direct file path references
            content = content.replace(old_path, new_path)

            # 2. Update Python import statements
            if old_path.endswith('.py'):
                old_module_path = get_relative_path(os.path.splitext(old_path)[0], file_path)
                new_module_path = get_relative_path(os.path.splitext(new_path)[0], file_path)
                
                # from src.pyedgarai.utils -> from pyedgarai.utils
                if new_module_path.startswith('pyedgarai'):
                    new_module_path = new_module_path.replace('src.','')

                if old_module_path != new_module_path:
                    content = content.replace(f'from {old_module_path}', f'from {new_module_path}')
                    content = content.replace(f'import {old_module_path}', f'import {new_module_path}')


        if content != original_content:
            print(f"[INFO] Updating references in: {file_path}")
            if not dry_run:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                except IOError as e:
                    print(f"[ERROR] Could not write to {file_path}: {e}")


def move_files(dry_run=False):
    """
    Moves files based on the move_map.json file.
    """
    workspace_root = os.getcwd()
    move_map_path = os.path.join(workspace_root, 'move_map.json')

    try:
        with open(move_map_path, 'r') as f:
            move_map = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] 'move_map.json' not found in {workspace_root}. Aborting.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"[ERROR] 'move_map.json' is not valid JSON. Aborting.")
        sys.exit(1)

    for old_path_rel, new_path_rel in move_map.items():
        old_path_abs = os.path.join(workspace_root, old_path_rel)
        new_path_abs = os.path.join(workspace_root, new_path_rel)

        if not os.path.exists(old_path_abs):
            print(f"[WARN] Source file not found, skipping: {old_path_rel}")
            continue

        new_dir = os.path.dirname(new_path_abs)
        if not os.path.exists(new_dir):
            print(f"[INFO] Creating directory: {new_dir}")
            if not dry_run:
                os.makedirs(new_dir)

        print(f"  - Moving: '{old_path_rel}' -> '{new_path_rel}'")
        if not dry_run:
            try:
                shutil.move(old_path_abs, new_path_abs)
            except Exception as e:
                print(f"[ERROR] Failed to move '{old_path_rel}': {e}")
    
    return move_map


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reorganize the repository by moving files according to 'move_map.json' and updating references."
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Simulate the file moves and reference updates without making any changes."
    )
    parser.add_argument(
        "--skip-imports",
        action="store_true",
        help="Skip the import/path reference update step."
    )

    args = parser.parse_args()

    if args.dry_run:
        print("--- DRY RUN MODE ---")
        print("No files will be moved or modified.\n")

    print("[STEP 1] Moving files...")
    moved_map = move_files(dry_run=args.dry_run)
    print("[SUCCESS] File moving step complete.\n")

    if not args.skip_imports:
        print("[STEP 2] Updating imports and file path references...")
        update_references(moved_map, dry_run=args.dry_run)
        print("[SUCCESS] Reference update step complete.\n")
    else:
        print("[INFO] Skipped reference updates as requested.")

    print("Reorganization script finished.")
