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
from datetime import datetime

# --- Configuration & i18n Setup ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, 'config.json')
PID_DIR = os.path.join(SCRIPT_DIR, 'pids')
LOCALE_DIR = os.path.join(SCRIPT_DIR, 'locales')

LOG_FILE_HANDLE = None

try:
    locale.setlocale(locale.LC_ALL, '')
except locale.Error:
    print("Warning: Could not set locale.", file=sys.stderr)

t = gettext.translation('messages', localedir=LOCALE_DIR, fallback=True)
_ = t.gettext

# --- Logging Functions ---
def setup_logging(config):
    """Sets up the global log file for the tool itself."""
    global LOG_FILE_HANDLE
    log_directory = config.get('settings', {}).get('log_directory')
    if not log_directory:
        print(_("Error: 'log_directory' not defined in settings."), file=sys.stderr)
        return

    try:
        base_log_dir = os.path.expanduser(log_directory)
        tool_log_dir = os.path.join(base_log_dir, "launch_server")
        os.makedirs(tool_log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_path = os.path.join(tool_log_dir, f"{timestamp}.log")
        LOG_FILE_HANDLE = open(log_path, 'a', encoding='utf-8')
    except Exception as e:
        print(f"Warning: Could not create tool log file: {e}", file=sys.stderr)
        LOG_FILE_HANDLE = None

def log(message, level="INFO", file=sys.stdout):
    """Prints to console and writes to the global log file with structured format."""
    # For status table, don't add log prefix to console output
    is_status_line = "yes" in message or "no" in message or "---" in message
    
    if not is_status_line:
        print(message, file=file)
    else:
        # Still print the raw table line to the console
        print(message, file=sys.stdout)

    if LOG_FILE_HANDLE:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{level.upper()}][{timestamp}] {message}\n"
        LOG_FILE_HANDLE.write(log_entry)
        LOG_FILE_HANDLE.flush()

# --- Helper Functions ---
def _get_service_pid_path(service_name):
    return os.path.join(PID_DIR, f"{service_name}.pid")

def _load_config():
    if not os.path.exists(CONFIG_PATH):
        print(_("Error: Configuration file not found at {path}").format(path=CONFIG_PATH), file=sys.stderr)
        sys.exit(1)
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(_("Error: Could not decode JSON from {path}").format(path=CONFIG_PATH), file=sys.stderr)
        sys.exit(1)

def _save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

def _find_service(service_name, services):
    for service in services:
        if service.get('name') == service_name:
            return service
    log(_("Error: Service '{service_name}' not found in configuration.").format(service_name=service_name), level="ERROR", file=sys.stderr)
    return None

def is_running(service_name):
    pid_path = _get_service_pid_path(service_name)
    if not os.path.exists(pid_path):
        return False
    try:
        with open(pid_path, 'r') as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)
    except (IOError, ValueError, OSError):
        return False
    else:
        return True

# --- Command Functions ---
def start_service(service, log_directory):
    name = service['name']
    if is_running(name):
        log(_("Service '{name}' is already running.").format(name=name), level="WARN")
        return

    command = service.get('command')
    
    try:
        base_log_dir = os.path.expanduser(log_directory)
        service_log_dir = os.path.join(base_log_dir, name)
        os.makedirs(service_log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_path = os.path.join(service_log_dir, f"{timestamp}.log")

        process_env = os.environ.copy()
        process_env.update(service.get('env', {}))
        
        log_file = open(log_path, 'a', encoding='utf-8')
        
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
        
        log(_("Successfully launched service '{name}' with PID {pid}.").format(name=name, pid=proc.pid))

    except Exception as e:
        log(_("Error launching service '{name}': {e}").format(name=name, e=e), level="ERROR", file=sys.stderr)

def stop_service(service_name):
    if not is_running(service_name):
        log(_("Service '{service_name}' is not running.").format(service_name=service_name), level="WARN")
        return

    pid_path = _get_service_pid_path(service_name)
    try:
        with open(pid_path, 'r') as f:
            pid = int(f.read().strip())
        
        log(_("Stopping service '{service_name}' (PID: {pid})...").format(service_name=service_name, pid=pid))
        os.kill(pid, signal.SIGTERM)
        
        time.sleep(1)
        
        if is_running(service_name):
            log(_("Process {pid} did not terminate gracefully. Sending SIGKILL.").format(pid=pid), level="WARN")
            os.kill(pid, signal.SIGKILL)

    except (IOError, ValueError, OSError) as e:
        log(_("Error stopping service '{service_name}': {e}").format(service_name=service_name, e=e), level="ERROR", file=sys.stderr)
    finally:
        if os.path.exists(pid_path):
            os.remove(pid_path)
        log(_("Service '{service_name}' stopped.").format(service_name=service_name))

def handle_start(args):
    log(_("Starting all enabled services..."))
    config = _load_config()
    log_directory = config.get('settings', {}).get('log_directory')
    if not log_directory:
        log(_("Error: 'log_directory' not defined in settings."), level="ERROR", file=sys.stderr)
        sys.exit(1)

    for service in config.get('services', []):
        if service.get('enabled', False):
            start_service(service, log_directory)

def handle_stop(args):
    _find_service(args.service_name, _load_config().get('services', []))
    stop_service(args.service_name)

def handle_restart(args):
    config = _load_config()
    log_directory = config.get('settings', {}).get('log_directory')
    if not log_directory:
        log(_("Error: 'log_directory' not defined in settings."), level="ERROR", file=sys.stderr)
        sys.exit(1)

    service = _find_service(args.service_name, config.get('services', []))
    if service:
        stop_service(service['name'])
        time.sleep(0.5)
        start_service(service, log_directory)

def handle_status(args):
    config = _load_config()
    services = config.get('services', [])
    log(f"{_('SERVICE NAME'):<30} {_('ENABLED'):<10} {_('STATUS'):<10}")
    log("-" * 50)
    for service in services:
        name = service.get('name', 'Unnamed')
        enabled = _("yes") if service.get('enabled', False) else _("no")
        status = _("running") if is_running(name) else _("stopped")
        log(f"{name:<30} {enabled:<10} {status:<10}")

def _toggle_service(service_name, enabled_status):
    config = _load_config()
    service = _find_service(service_name, config.get('services', []))
    if service:
        if service.get('enabled') == enabled_status:
            status_text = _("enabled") if enabled_status else _("disabled")
            log(_("Service '{service_name}' is already {status_text}.").format(service_name=service_name, status_text=status_text), level="WARN")
            return
        
        service['enabled'] = enabled_status
        _save_config(config)
        status_text = _("Enabled") if enabled_status else _("Disabled")
        log(_("Service '{service_name}' has been {status_text} in the configuration.").format(service_name=service_name, status_text=status_text.lower()))
        return True
    return False

def handle_enable(args):
    _toggle_service(args.service_name, True)

def handle_disable(args):
    if _find_service(args.service_name, _load_config().get('services', [])):
        if is_running(args.service_name):
            stop_service(args.service_name)
        _toggle_service(args.service_name, False)

def main():
    config = _load_config()
    setup_logging(config)

    parser = argparse.ArgumentParser(description=_("A tool to manage background services on macOS."))
    subparsers = parser.add_subparsers(dest='command', help=_('Available commands'))
    subparsers.required = True

    # ... (parser setup remains the same)
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
        
    try:
        args.func(args)
    finally:
        if LOG_FILE_HANDLE:
            LOG_FILE_HANDLE.close()

if __name__ == "__main__":
    main()