#!/usr/bin/env python3
"""Prepare derived, namespaced artwork without changing upstream binaries."""
from pathlib import Path
import configparser
import json

root = Path(__file__).resolve().parents[1]
breeze = root / 'src/breeze'
plugin = breeze / 'kstyle/breezestyleplugin.cpp'
text = plugin.read_text().replace('QLatin1String("breeze")', 'QLatin1String("bypssd")').replace('QStringLiteral("Breeze")', 'QStringLiteral("BYPSSD")')
plugin.write_text(text)
(breeze / 'kstyle/breeze.json').write_text('{ "Keys": [ "BYPSSD" ] }\n')
cmake = breeze / 'kstyle/CMakeLists.txt'
text = cmake.read_text()
line = '\nset_target_properties(breeze${QT_MAJOR_VERSION} PROPERTIES OUTPUT_NAME bypssdstyle${QT_MAJOR_VERSION})\n'
if line not in text:
    cmake.write_text(text + line)

colors = configparser.ConfigParser(interpolation=None)
colors.optionxform = str
colors.read(breeze / 'colors/BreezeDark.colors')
for section in colors.sections():
    if section.startswith('Colors:'):
        for key in ('DecorationFocus', 'DecorationHover', 'ForegroundActive', 'ForegroundLink'):
            if key in colors[section]:
                colors[section][key] = '255,184,0'
        if section == 'Colors:Selection':
            colors[section]['BackgroundNormal'] = '255,184,0'
            colors[section]['BackgroundAlternate'] = '230,166,0'
            colors[section]['ForegroundNormal'] = '0,0,0'
            colors[section]['ForegroundInactive'] = '32,32,32'
            colors[section]['ForegroundActive'] = '0,0,0'
            colors[section]['ForegroundLink'] = '0,0,0'
    if section == 'General':
        for key in list(colors[section]):
            if key.startswith('Name'):
                del colors[section][key]
        colors[section]['Name'] = 'BYPSSD Renacer'
        colors[section]['AccentColor'] = '255,184,0'
with (root / 'branding/BYPSSDRenacer.colors').open('w') as out:
    out.write('# Derived from BreezeDark.colors; LGPL-2.0-or-later.\n')
    out.write('\n'.join(line for line in (breeze / 'colors/BreezeDark.colors').read_text().splitlines() if line.startswith('# SPDX-')) + '\n')
    colors.write(out, space_around_delimiters=False)

splash = (root / 'branding/splash/Splash.qml').read_text()
(root / 'branding/look-and-feel/contents/splash/Splash.qml').write_text(splash)

metadata = {'KPlugin': {'Id': 'com.bypssd.desktop', 'Name': 'BYPSSD OS Renacer', 'Description': 'Escritorio BYPSSD para oficina y educación', 'Version': '1.0', 'License': 'GPL-2.0-or-later', 'Authors': [{'Name': 'BYPSSD Informática Retro'}]}, 'KPackageStructure': 'Plasma/LookAndFeel', 'X-Plasma-APIVersion': '2'}
(root / 'branding/look-and-feel/metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
