#!/bin/bash
check() { return 255; }
depends() { echo 'shutdown'; }
installkernel() { instmods -o usbhid hid_generic xhci_pci xhci_hcd; }
install() {
 inst_multiple chvt stty timeout
 inst_multiple -o eject plymouth
 inst_hook shutdown 99 "$moddir/remove-media.sh"
}
