#!/usr/bin/env python3
"""
Lucide Icons to Razor Components Generator
Downloads all icons from lucide.dev and converts them to Razor components
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET
import re

def to_pascal_case(name):
    """Convert kebab-case to PascalCase"""
    parts = name.split('-')
    return ''.join(part.capitalize() for part in parts) + 'Icon'

def extract_svg_content(svg_path):
    """Extract viewBox and inner content from SVG"""
    with open(svg_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract viewBox
    viewbox_match = re.search(r'viewBox="([^"]+)"', content)
    viewbox = viewbox_match.group(1) if viewbox_match else "0 0 24 24"
    
    # Extract inner SVG content
    inner_match = re.search(r'<svg[^>]*>(.*?)</svg>', content, re.DOTALL)
    inner_content = inner_match.group(1).strip() if inner_match else ""
    
    return viewbox, inner_content

def generate_razor_component(viewbox, inner_content):
    """Generate Razor component from SVG"""
    # Indent inner content
    indented = '\n    '.join(line for line in inner_content.split('\n') if line.strip())
    
    razor = f"""@inherits IconBase

<svg xmlns="http://www.w3.org/2000/svg"
     width="@Width"
     height="@Height"
     viewBox="{viewbox}"
     focusable="false"
     fill="none"
     stroke="currentColor"
     stroke-width="@StrokeWidth"
     stroke-linecap="round"
     stroke-linejoin="round"
     @attributes="@AdditionalAttributes">
    {indented}
</svg>
"""
    return razor

def main():
    output_path = Path("src/LumexUI.Shared.Icons")
    
    # Check if output path exists
    if not output_path.exists():
        print(f"Error: Output path '{output_path}' not found!")
        sys.exit(1)
    
    # Create temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        repo_dir = temp_dir / "lucide-icons"
        
        print("Cloning lucide-icons repository...")
        result = subprocess.run(
            ["git", "clone", "--depth", "1", "https://github.com/lucide-icons/lucide.git", str(repo_dir)],
            capture_output=True
        )
        
        if result.returncode != 0:
            print(f"Error: Failed to clone repository: {result.stderr.decode()}")
            sys.exit(1)
        
        icons_dir = repo_dir / "icons"
        
        if not icons_dir.exists():
            print("Error: Icons directory not found in repository!")
            sys.exit(1)
        
        # Get all SVG files
        svg_files = sorted(icons_dir.glob("*.svg"))
        total = len(svg_files)
        
        print(f"Found {total} icons to convert")
        print("")
        
        success_count = 0
        fail_count = 0
        
        # Process each SVG
        for i, svg_file in enumerate(svg_files, 1):
            try:
                # Convert filename to component name
                component_name = to_pascal_case(svg_file.stem)
                output_file = output_path / f"{component_name}.razor"
                
                # Extract SVG data
                viewbox, inner_content = extract_svg_content(svg_file)
                
                # Generate component
                razor_content = generate_razor_component(viewbox, inner_content)
                
                # Write component
                output_file.write_text(razor_content, encoding='utf-8')
                
                success_count += 1
                
                # Progress indicator
                if success_count % 100 == 0:
                    print(f"Generated {success_count}/{total} icons...")
                
            except Exception as e:
                fail_count += 1
                print(f"Warning: Failed to process {svg_file.name}: {e}")
        
        print("")
        print(f"Generation complete!")
        print(f"Successfully generated: {success_count} icons")
        if fail_count > 0:
            print(f"Failed: {fail_count} icons")
        
        print("")
        print(f"Icons location: {output_path.absolute()}")
        print(f"All done! Your icons are ready to use!")
        print("")
        print("Usage example:")
        print('  <ActivityIcon Width="24" Height="24" />')
        print("")

if __name__ == "__main__":
    main()
