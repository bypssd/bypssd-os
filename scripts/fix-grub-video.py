#!/usr/bin/env python3
"""Repair nested GRUB function declarations in the x86 upstream template."""
from pathlib import Path
import sys

def repair(text):
    if 'function load_video' not in text:
        return text
    start=text.index('if [ ')
    end=text.index('\nload_video\n',start)+len('\nload_video\n')
    block=text[start:end]
    if block.count('function load_video')!=2:
        return text
    variable='$$grub_platform' if '$$grub_platform' in block else '$grub_platform'
    replacement=('insmod all_video\n\n'
        f'if [ "{variable}" == "efi" ]; then\n'
        '    set basicgfx="nomodeset"\n'
        'else\n'
        '    set basicgfx="nomodeset vga=791"\n'
        'fi\n')
    return text[:start]+replacement+text[end:]

if __name__=='__main__':
    source=Path(sys.argv[1]);target=Path(sys.argv[2])
    original=source.read_text();updated=repair(original)
    target.write_text(updated)
    print('GRUB video block repaired' if updated!=original else 'GRUB video block already valid')
