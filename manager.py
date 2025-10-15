#!/usr/bin/env python3
import argparse
import gettext
import json
import locale
import os
import signal
import subprocess
import sys
import time

# --- Configuration & i18n Setup ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, 'config.json')
PID_DIR = os.path.join(SCRIPT_DIR, 'pids')
LOCALE_DIR = os.path.join(SCRIPT_DIR, 'locales')

# Set up translation
try:
    locale.setlocale(locale.LC_ALL, '')
except locale.Error:
    print("Warning: Could not set locale.", file=sys.stderr)

# Use 'launch_server' as the domain for our translations
t = gettext.translation('messages', localedir=LOCALE_DIR, fallback=True)
_ = t.gettext

# --- Helper Functions ---

def _get_service_pid_path(service_name):
    """Returns the absolute path to a service's PID file."""
    return os.path.join(PID_DIR, f"{service_name}.pid")

def _load_config():
    """Loads and returns the service configurations from config.json."""
    if not os.path.exists(CONFIG_PATH):
        print(_("Error: Configuration file not found at {path}").format(path=CONFIG_PATH), file=sys.stderr)
        sys.exit(1)
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(_("Error: Could not decode JSON from {path}").format(path=CONFIG_PATH), file=sys.stderr)
        sys.exit(1)

def _save_config(services):
    """Saves the service configurations back to config.json."""
    with open(CONFIG_PATH, 'w') as f:
        json.dump(services, f, indent=2)

def _find_service(service_name, services):
    """Finds a service by name in the configuration list."""
    for service in services:
        if service.get('name') == service_name:
            return service
    print(_("Error: Service '{service_name}' not found in configuration.").format(service_name=service_name), file=sys.stderr)
    return None

def is_running(service_name):
    """Checks if a service is running by checking its PID file and process status."""
    pid_path = _get_service_pid_path(service_name)
    if not os.path.exists(pid_path):
        return False
    try:
        with open(pid_path, 'r') as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)  # Check if process exists
    except (IOError, ValueError, OSError):
        return False
    else:
        return True

# --- Command Functions ---

def start_service(service):
    """Starts a single service and records its PID."""
    name = service['name']
    if is_running(name):
        print(_("Service '{name}' is already running.").format(name=name))
        return

    command = service.get('command')
    log_path = service.get('log_path')

    try:
        log_dir = os.path.dirname(log_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        process_env = os.environ.copy()
        process_env.update(service.get('env', {}))
        
        log_file = open(log_path, 'a')
        
        proc = subprocess.Popen(
            [command] + service.get('args', []),
            stdout=log_file,
            stderr=log_file,
            env=process_env,
            close_fds=True
        )

        os.makedirs(PID_DIR, exist_ok=True)
        with open(_get_service_pid_path(name), 'w') as f:
            f.write(str(proc.pid))
        
        print(_("Successfully launched service '{name}' with PID {pid}.").format(name=name, pid=proc.pid))

    except Exception as e:
        print(_("Error launching service '{name}': {e}").format(name=name, e=e), file=sys.stderr)

def stop_service(service_name, services):
    """Stops a single running service."""
    if not is_running(service_name):
        print(_("Service '{service_name}' is not running.").format(service_name=service_name))
        return

    pid_path = _get_service_pid_path(service_name)
    try:
        with open(pid_path, 'r') as f:
            pid = int(f.read().strip())
        
        print(_("Stopping service '{service_name}' (PID: {pid})...").format(service_name=service_name, pid=pid))
        os.kill(pid, signal.SIGTERM)
        
        time.sleep(1)
        
        if is_running(service_name):
            print(_("Process {pid} did not terminate gracefully. Sending SIGKILL.").format(pid=pid))
            os.kill(pid, signal.SIGKILL)

    except (IOError, ValueError, OSError) as e:
        print(_("Error stopping service '{service_name}': {e}").format(service_name=service_name, e=e), file=sys.stderr)
    finally:
        if os.path.exists(pid_path):
            os.remove(pid_path)
        print(_("Service '{service_name}' stopped.").format(service_name=service_name))

def handle_start(args):
    """Handler for the 'start' command."""
    print(_("Starting all enabled services..."))
    services = _load_config()
    for service in services:
        if service.get('enabled', False):
            start_service(service)

def handle_stop(args):
    """Handler for the 'stop' command."""
    services = _load_config()
    service = _find_service(args.service_name, services)
    if service:
        stop_service(service['name'], services)

def handle_restart(args):
    """Handler for the 'restart' command."""
    services = _load_config()
    service = _find_service(args.service_name, services)
    if service:
        stop_service(service['name'], services)
        time.sleep(0.5)
        start_service(service)

def handle_status(args):
    """Handler for the 'status' command."""
    services = _load_config()
    print(f"{_('SERVICE NAME'):<30} {_('ENABLED'):<10} {_('STATUS'):<10}")
    print("-" * 50)
    for service in services:
        name = service.get('name', 'Unnamed')
        enabled = _("yes") if service.get('enabled', False) else _("no")
        status = _("running") if is_running(name) else _("stopped")
        print(f"{name:<30} {enabled:<10} {status:<10}")

def _toggle_service(service_name, enabled_status):
    """Helper to enable or disable a service in the config."""
    services = _load_config()
    service = _find_service(service_name, services)
    if service:
        if service.get('enabled') == enabled_status:
            status_text = _("enabled") if enabled_status else _("disabled")
            print(_("Service '{service_name}' is already {status_text}.").format(service_name=service_name, status_text=status_text))
            return
        
        service['enabled'] = enabled_status
        _save_config(services)
        status_text = _("Enabled") if enabled_status else _("Disabled")
        print(_("Service '{service_name}' has been {status_text} in the configuration.").format(service_name=service_name, status_text=status_text.lower()))
        return True
    return False

def handle_enable(args):
    """Handler for the 'enable' command."""
    _toggle_service(args.service_name, True)

def handle_disable(args):
    """Handler for the 'disable' command."""
    services = _load_config()
    service = _find_service(args.service_name, services)
    if service:
        if is_running(service['name']):
            stop_service(service['name'], services)
        _toggle_service(args.service_name, False)

def main():
    """Main function to parse arguments and dispatch commands."""
    parser = argparse.ArgumentParser(description=_("A tool to manage background services on macOS."))
    subparsers = parser.add_subparsers(dest='command', help=_('Available commands'))
    subparsers.required = True

    parser_start = subparsers.add_parser('start', help=_('Start all enabled services (default action for launchd).'))
    parser_start.set_defaults(func=handle_start)

    parser_stop = subparsers.add_parser('stop', help=_('Stop a running service (temporary).'))
    parser_stop.add_argument('service_name', help=_('The name of the service to stop.'))
    parser_stop.set_defaults(func=handle_stop)
    
    parser_restart = subparsers.add_parser('restart', help=_('Restart a service.'))
    parser_restart.add_argument('service_name', help=_('The name of the service to restart.'))
    parser_restart.set_defaults(func=handle_restart)

    parser_status = subparsers.add_parser('status', help=_('Show the status of all configured services.'))
    parser_status.set_defaults(func=handle_status)

    parser_enable = subparsers.add_parser('enable', help=_('Enable a service in the configuration file.'))
    parser_enable.add_argument('service_name', help=_('The name of the service to enable.'))
    parser_enable.set_defaults(func=handle_enable)

    parser_disable = subparsers.add_parser('disable', help=_('Stop and disable a service in the configuration file (permanent).'))
    parser_disable.add_argument('service_name', help=_('The name of the service to disable.'))
    parser_disable.set_defaults(func=handle_disable)

    if sys.argv[1:]:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(['start'])
        
    args.func(args)

if __name__ == "__main__":
    main()