// Derived from Plasma Workspace v6.8.2 default layout.
// SPDX-License-Identifier: GPL-2.0-or-later
loadTemplate("org.kde.plasma.desktop.defaultPanel");
var allDesktops = desktopsForActivity(currentActivity());
for (var i = 0; i < allDesktops.length; i++) {
    allDesktops[i].wallpaperPlugin = "org.kde.image";
    allDesktops[i].currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    allDesktops[i].writeConfig("Image", "file:///usr/share/bypssd/wallpaper.png");
    allDesktops[i].writeConfig("FillMode", 1);
    allDesktops[i].writeConfig("Color", "#000000");
}
var allPanels = panels();
for (var p = 0; p < allPanels.length; p++) {
    var widgets = allPanels[p].widgets();
    for (var w = 0; w < widgets.length; w++) {
        if (widgets[w].type === "org.kde.plasma.kickoff") {
            widgets[w].currentConfigGroup = ["General"];
            widgets[w].writeConfig("icon", "bypssd-logo");
        }
        if (widgets[w].type === "org.kde.plasma.icontasks" || widgets[w].type === "org.kde.plasma.taskmanager") {
            widgets[w].currentConfigGroup = ["General"];
            widgets[w].writeConfig("launchers", "applications:systemsettings.desktop,applications:org.kde.discover.desktop,applications:org.kde.dolphin.desktop,applications:chromium-browser.desktop,applications:libreoffice-writer.desktop");
        }
    }
}
