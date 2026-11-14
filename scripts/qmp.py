#!/usr/bin/env python3
"""Issue one QMP command to the disposable BYPSSD test VM."""
from pathlib import Path
import json
import os
import socket
import sys

project = Path(__file__).resolve().parents[1]
with socket.socket(socket.AF_UNIX) as sock:
    sock.settimeout(20)
    sock.connect(os.environ.get('BYPSSD_QMP_SOCKET',str(project/'out/qemu-test/qmp.sock')))
    stream = sock.makefile('rwb')
    def receive():
        while True:
            raw = stream.readline()
            if not raw:
                raise RuntimeError('QMP connection closed')
            result = json.loads(raw)
            if 'return' in result or 'error' in result:
                return result
    json.loads(stream.readline())
    stream.write(b'{"execute":"qmp_capabilities"}\r\n')
    stream.flush()
    receive()
    cmd = {'execute':sys.argv[1]}
    if len(sys.argv)>2:
        cmd['arguments']=json.loads(sys.argv[2])
    stream.write((json.dumps(cmd)+'\r\n').encode())
    stream.flush()
    print(json.dumps(receive(),ensure_ascii=False))
