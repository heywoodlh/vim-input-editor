#!/usr/bin/env python3
import os
import subprocess
import argparse

# Exit with error message if not on Linux/BSD or not using X11
if os.name != 'posix' or os.environ.get('DISPLAY') is None:
    raise SystemExit('vim-ime only works on Linux/BSD with X11')

# Quietly check if external dependency xclip and xdotool are installed
deps = True
try:
    subprocess.check_output(['which', 'xclip'])
except subprocess.CalledProcessError:
    print("xclip is not installed")
    deps = False
try:
    subprocess.check_output(['which', 'xdotool'])
except subprocess.CalledProcessError:
    print("xdotool is not installed")
    deps = False

# Exit with deps equal false
if not deps:
    exit(1)

# Create required str arguments: 
parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outfile', type=str, required=True)
parser.add_argument('-c', '--cmd', type=str, required=True)
# Create optional clipboard-edit argument that does not accept values
parser.add_argument('-e', '--clipboard-edit', action='store_true', help='edit clipboard contents')
# Create optional clipboard-copy argument that does not accept values
parser.add_argument('-p', '--clipboard-copy', action='store_true', help='copy to clipboard')
args = parser.parse_args()

# Quietly check if first word in cmd argument is actually installed on system
try:
    subprocess.check_output(['which', args.cmd.split()[0]])
except subprocess.CalledProcessError:
    print(args.cmd.split()[0] + " is not installed")
    exit(1)

# Make sure outfile is empty
with open(args.outfile, 'w') as f:
    f.write('')
    f.close()

# If clipboard editing mode is enabled, write the clipboard to outfile
if args.clipboard_edit:
    subprocess.call(['xclip', '-o', '-selection', 'clipboard'], stdout=open(args.outfile, 'w'))

# Set ime_cmd variable to cmd argument plus the outfile argument
ime_cmd = args.cmd + " " + args.outfile

# Run ime_cmd command as a string and save its exit code
exit_code = subprocess.run(ime_cmd, shell=True).returncode

# If exit code is 0, read outfile and use xdotool to type it unless clipboard copy mode is enabled
if exit_code == 0:
    with open(args.outfile, 'r') as f:
        if not args.clipboard_copy:
            subprocess.call(['xdotool', 'type', '--clearmodifiers', f.read()])
        else:
            subprocess.call(['xclip', '-selection', 'clipboard'], stdin=f)
        f.close()
