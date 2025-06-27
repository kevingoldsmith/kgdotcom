#!/usr/bin/env python3
"""
Compare directory structures and file contents between output/ and lkgoutput/ directories.
"""

import os
import sys
import filecmp
import difflib
from pathlib import Path
from typing import Set, List, Tuple


def get_all_files(directory: Path) -> Set[str]:
    """Get all files in directory relative to the directory root."""
    files = set()
    if not directory.exists():
        return files
    
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            full_path = Path(root) / filename
            relative_path = full_path.relative_to(directory)
            files.add(str(relative_path))
    
    return files


def compare_directories(dir1: Path, dir2: Path) -> Tuple[Set[str], Set[str], Set[str]]:
    """Compare two directories and return (common, only_in_dir1, only_in_dir2)."""
    files1 = get_all_files(dir1)
    files2 = get_all_files(dir2)
    
    common = files1.intersection(files2)
    only_in_dir1 = files1 - files2
    only_in_dir2 = files2 - files1
    
    return common, only_in_dir1, only_in_dir2


def compare_file_contents(file1: Path, file2: Path) -> bool:
    """Compare contents of two files. Returns True if identical."""
    try:
        return filecmp.cmp(file1, file2, shallow=False)
    except (OSError, IOError):
        return False


def show_file_diff(file1: Path, file2: Path, relative_path: str):
    """Show diff between two files."""
    try:
        with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
            lines1 = f1.readlines()
            lines2 = f2.readlines()
        
        diff = list(difflib.unified_diff(
            lines1, lines2,
            fromfile=f"output/{relative_path}",
            tofile=f"lkgoutput/{relative_path}",
            lineterm=''
        ))
        
        if diff:
            print(f"\n--- Differences in {relative_path} ---")
            for line in diff[:50]:  # Limit output
                print(line)
            if len(diff) > 50:
                print(f"... ({len(diff) - 50} more lines)")
    
    except (UnicodeDecodeError, IOError):
        print(f"\n--- Binary file difference in {relative_path} ---")


def main():
    """Main comparison function."""
    output_dir = Path("output")
    lkg_dir = Path("lkgoutput")
    
    if not output_dir.exists():
        print("ERROR: output/ directory does not exist")
        sys.exit(1)
    
    if not lkg_dir.exists():
        print("ERROR: lkgoutput/ directory does not exist")
        sys.exit(1)
    
    print("Comparing output/ and lkgoutput/ directories...")
    print("=" * 50)
    
    # Compare directory structures
    common_files, only_in_output, only_in_lkg = compare_directories(output_dir, lkg_dir)
    
    # Report structure differences
    if only_in_output:
        print(f"\nFiles only in output/ ({len(only_in_output)}):")
        for file in sorted(only_in_output):
            print(f"  + {file}")
    
    if only_in_lkg:
        print(f"\nFiles only in lkgoutput/ ({len(only_in_lkg)}):")
        for file in sorted(only_in_lkg):
            print(f"  - {file}")
    
    # Compare common files
    different_files = []
    identical_files = []
    
    for relative_path in sorted(common_files):
        file1 = output_dir / relative_path
        file2 = lkg_dir / relative_path
        
        if compare_file_contents(file1, file2):
            identical_files.append(relative_path)
        else:
            different_files.append(relative_path)
    
    # Report file differences
    print(f"\nFile comparison results:")
    print(f"  Identical files: {len(identical_files)}")
    print(f"  Different files: {len(different_files)}")
    
    if different_files:
        print(f"\nDifferent files ({len(different_files)}):")
        for file in different_files:
            print(f"  ~ {file}")
        
        # Show diffs for different files
        if len(different_files) <= 10:  # Only show diffs for first 10 files
            for relative_path in different_files:
                file1 = output_dir / relative_path
                file2 = lkg_dir / relative_path
                show_file_diff(file1, file2, relative_path)
        else:
            print(f"\n(Too many different files to show diffs - showing first 10)")
            for relative_path in different_files[:10]:
                file1 = output_dir / relative_path
                file2 = lkg_dir / relative_path
                show_file_diff(file1, file2, relative_path)
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"  Total files in output/: {len(get_all_files(output_dir))}")
    print(f"  Total files in lkgoutput/: {len(get_all_files(lkg_dir))}")
    print(f"  Common files: {len(common_files)}")
    print(f"  Files only in output/: {len(only_in_output)}")
    print(f"  Files only in lkgoutput/: {len(only_in_lkg)}")
    print(f"  Identical files: {len(identical_files)}")
    print(f"  Different files: {len(different_files)}")
    
    if different_files or only_in_output or only_in_lkg:
        print("\nDirectories are DIFFERENT")
        sys.exit(1)
    else:
        print("\nDirectories are IDENTICAL")
        sys.exit(0)


if __name__ == "__main__":
    main()