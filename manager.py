#!/usr/bin/env python3
import argparse
import gettext
import json
import locale
import os
import signal
import subprocess
import shutil
import sys
import time
import traceback
from datetime import datetime

# --- Configuration & i18n Setup ---
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, 'config.json')
PID_DIR = os.path.join(SCRIPT_DIR, 'pids')
LOCALE_DIR = os.path.join(SCRIPT_DIR, 'locales')

LOG_FILE_HANDLE = None

def _check_and_compile_translations():
    """
    Checks if .po files are newer than .mo files and recompiles them if necessary.
    """
    msgfmt_path = shutil.which('msgfmt')
    if not msgfmt_path:
        print("Warning: 'msgfmt' command not found. Cannot auto-compile translations.", file=sys.stderr)
        print("Please install gettext tools.", file=sys.stderr)
        return

    for dirpath, _, filenames in os.walk(LOCALE_DIR):
        for filename in filenames:
            if filename.endswith('.po'):
                po_file = os.path.join(dirpath, filename)
                mo_file = po_file[:-2] + 'mo'
                
                po_mtime = os.path.getmtime(po_file)
                
                needs_compile = not os.path.exists(mo_file) or po_mtime > os.path.getmtime(mo_file)
                
                if needs_compile:
                    try:
                        print(f"Compiling {po_file} to {mo_file}...", file=sys.stderr)
                        subprocess.run([msgfmt_path, '-o', mo_file, po_file], check=True, capture_output=True, text=True)
                    except subprocess.CalledProcessError as e:
                        print(f"Error compiling {po_file}: {e.stderr}", file=sys.stderr)
                    except Exception as e:
                        print(f"An unexpected error occurred during compilation of {po_file}: {e}", file=sys.stderr)

# --- Robust i18n Setup ---
_check_and_compile_translations()

try:
    locale.setlocale(locale.LC_ALL, '')
except locale.Error:
    print("Warning: Could not set locale from environment.", file=sys.stderr)

# Let gettext handle locale detection from environment variables
try:
    # By omitting 'languages', gettext will use environment variables (LANG, LC_MESSAGES)
    t = gettext.translation('messages', localedir=LOCALE_DIR, fallback=True)
except FileNotFoundError:
    # This is a fallback for cases where the 'locales' directory is missing.
    t = gettext.translation('messages', fallback=True)

_ = t.gettext


# --- Logging Functions ---
def setup_logging(config):
    """Sets up the global log file for the tool itself."""
    global LOG_FILE_HANDLE
    log_directory = config.get('settings', {}).get('log_directory')
    if not log_directory:
        raise ValueError(_("Error: 'log_directory' not defined in settings."))

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
    """Prints a structured message to console and writes to the global log file."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    level_str = _(level.upper())
    formatted_message = f"[{level_str}][{timestamp}] {message}"
    
    print(formatted_message, file=file)

    if LOG_FILE_HANDLE:
        LOG_FILE_HANDLE.write(formatted_message + "\n")
        LOG_FILE_HANDLE.flush()

def log_fatal_error(exc, config):
    """Logs a fatal error with full environment details."""
    error_log_dir = None
    log_directory = config.get('settings', {}).get('log_directory') if config else None
    
    if log_directory:
        error_log_dir = os.path.join(os.path.expanduser(log_directory), "error")
    else:
        error_log_dir = os.path.join(SCRIPT_DIR, "logs", "error")

    try:
        os.makedirs(error_log_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        error_log_path = os.path.join(error_log_dir, f"{timestamp}.log")

        with open(error_log_path, 'a', encoding='utf-8') as f:
            f.write("--- FATAL ERROR REPORT ---\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Exception: {exc}\n")
            f.write("Traceback:\n" + traceback.format_exc())
            f.write("-" * 20 + "\n")
            f.write("Environment Info:\n")
            f.write(f"  Python Version: {sys.version.replace('\\n', ' ')}\n")
            f.write(f"  Platform: {sys.platform}\n")
            f.write(f"  Arguments: {sys.argv}\n")
            f.write(f"  CWD: {os.getcwd()}\n")
            f.write(f"  LANG: {os.environ.get('LANG', 'Not set')}\n")
            f.write(f"  SCRIPT_DIR (resolved): {SCRIPT_DIR}\n")
            f.write("--- END OF REPORT ---\n")
        
        log(f"A critical error occurred. A detailed report has been saved to: {error_log_path}", level="FATAL", file=sys.stderr)

    except Exception as log_e:
        print(f"\nFATAL ERROR: {exc}\nLogging failed: {log_e}", file=sys.stderr)


# --- Configuration Validation ---
def validate_config(config):
    """Performs a deep validation of the configuration object."""
    if not isinstance(config, dict):
        raise ValueError(_("Root object must be a dictionary."))
    
    if 'settings' not in config or not isinstance(config['settings'], dict):
        raise ValueError(_("'settings' key is missing or not a dictionary."))
    
    if 'log_directory' not in config['settings']:
        raise ValueError(_("'log_directory' is missing in settings."))
    
    if 'services' not in config or not isinstance(config['services'], list):
        raise ValueError(_("'services' key is missing or not a list."))

    services = config['services']
    if not services:
        raise ValueError(_("No services configured. Please edit your 'config.json' to add services."))
    
    if len(services) == 1 and services[0].get("name") == "YOUR_SERVICE_NAME":
        raise ValueError(_("It seems you are using the default template. Please edit 'config.json' to configure your own services."))

    for i, service in enumerate(services):
        if not isinstance(service, dict):
            raise ValueError(_("Service at index {index} is not a dictionary.").format(index=i))
        
        has_command = 'command' in service
        has_shell_command = 'shell_command' in service
        
        if not (has_command ^ has_shell_command):
            raise ValueError(_("Service '{name}' must have either 'command' or 'shell_command', but not both.").format(name=service.get('name', f'at index {i}')))

        required_keys = ['name', 'enabled']
        for key in required_keys:
            if key not in service:
                raise ValueError(_("Service at index {index} is missing required key: '{key}'.").format(index=i, key=key))

        if has_command and not isinstance(service['command'], str):
            raise ValueError(_("Service '{name}' has a non-string value for key 'command'.").format(name=service.get('name')))
        
        if has_shell_command and not isinstance(service['shell_command'], str):
             raise ValueError(_("Service '{name}' has a non-string value for key 'shell_command'.").format(name=service.get('name')))

        if not isinstance(service['name'], str):
            raise ValueError(_("Service '{name}' has a non-string value for key 'name'.").format(name=service.get('name')))
        
        if not isinstance(service['enabled'], bool):
            raise ValueError(_("Service '{name}' has a non-boolean value for key 'enabled'.").format(name=service.get('name')))
        
        if 'args' in service and not isinstance(service['args'], list):
            raise ValueError(_("Service '{name}' has a non-list value for key 'args'.").format(name=service.get('name')))

        if 'env' in service and not isinstance(service['env'], dict):
            raise ValueError(_("Service '{name}' has a non-dictionary value for key 'env'.").format(name=service.get('name')))

# --- Helper Functions ---
def _get_service_pid_path(service_name):
    return os.path.join(PID_DIR, f"{service_name}.pid")

def _load_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(_("Error: Configuration file not found at {path}").format(path=CONFIG_PATH))
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        validate_config(config)
        return config
    except json.JSONDecodeError as e:
        raise ValueError(_("Error: Could not decode JSON from {path}").format(path=CONFIG_PATH)) from e
    except ValueError as e:
        raise e

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
        os.killpg(pid, 0)
    except (IOError, ValueError, OSError):
        return False
    else:
        return True

# --- Command Functions ---
def handle_check(args):
    """Handler for the 'check' command."""
    log(_("Configuration file is valid."))

def start_service(service, log_directory):
    name = service['name']
    if is_running(name):
        log(_("Service '{name}' is already running.").format(name=name), level="WARN")
        return

    try:
        base_log_dir = os.path.expanduser(log_directory)
        service_log_dir = os.path.join(base_log_dir, name)
        os.makedirs(service_log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_path = os.path.join(service_log_dir, f"{timestamp}.log")

        process_env = os.environ.copy()
        process_env.update(service.get('env', {}))
        
        log_file = open(log_path, 'a', encoding='utf-8')
        
        popen_args = {
            "stdout": log_file,
            "stderr": log_file,
            "env": process_env,
            "close_fds": True,
            "preexec_fn": os.setsid
        }
        
        if 'shell_command' in service:
            popen_args['shell'] = True
            command_to_run = service['shell_command']
        else:
            popen_args['shell'] = False
            command_to_run = [service['command']] + service.get('args', [])

        proc = subprocess.Popen(command_to_run, **popen_args)

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
        os.killpg(pid, signal.SIGTERM)
        
        time.sleep(1)
        
        if is_running(service_name):
            log(_("Process {pid} did not terminate gracefully. Sending SIGKILL.").format(pid=pid), level="WARN")
            os.killpg(pid, signal.SIGKILL)

    except (IOError, ValueError, OSError) as e:
        log(_("Error stopping service '{service_name}': {e}").format(service_name=service_name, e=e), level="ERROR", file=sys.stderr)
    finally:
        if os.path.exists(pid_path):
            os.remove(pid_path)
        log(_("Service '{service_name}' stopped.").format(service_name=service_name))


def handle_start(args):
    config = _load_config()
    services = config.get('services', [])
    
    log(_("Starting all enabled services..."))
    log_directory = config.get('settings', {}).get('log_directory')
    for service in services:
        if service.get('enabled', False):
            start_service(service, log_directory)

def handle_stop(args):
    _find_service(args.service_name, _load_config().get('services', []))
    stop_service(args.service_name)

def handle_restart(args):
    config = _load_config()
    log_directory = config.get('settings', {}).get('log_directory')
    service = _find_service(args.service_name, config.get('services', []))
    if service:
        stop_service(service['name'])
        time.sleep(0.5)
        start_service(service, log_directory)

def handle_status(args):
    config = _load_config()
    services = config.get('services', [])

    header = f"{_('SERVICE NAME'):<30} {_('ENABLED'):<10} {_('STATUS'):<10}"
    separator = "-" * 50
    
    print(header)
    print(separator)
    if LOG_FILE_HANDLE:
        log(header, level="INFO")
        log(separator, level="INFO")

    for service in services:
        name = service.get('name', 'Unnamed')
        enabled = _("yes") if service.get('enabled', False) else _("no")
        status = _("running") if is_running(name) else _("stopped")
        line = f"{name:<30} {enabled:<10} {status:<10}"
        print(line)
        if LOG_FILE_HANDLE:
            log(line, level="INFO")

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
    # Note: i18n setup is now done at the top level, before main()
    config = None
    try:
        config = _load_config()
        setup_logging(config)

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
        parser_check = subparsers.add_parser('check', help=_('Check the configuration file for syntax and schema errors.'))
        parser_check.set_defaults(func=handle_check)

        if sys.argv[1:]:
            args = parser.parse_args(sys.argv[1:])
        else:
            args = parser.parse_args(['start'])
        
        args.func(args)

    except (FileNotFoundError, ValueError) as e:
        log(f"{e}", level="ERROR", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        log_fatal_error(e, config)
        sys.exit(1)
    finally:
        if LOG_FILE_HANDLE:
            LOG_FILE_HANDLE.close()

if __name__ == "__main__":
    main()