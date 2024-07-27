# Name: NIYUBAHWE UWACU Annick
# Unit: RW-CODING-ACADEMY-III
# S-code: s7
#Lecturer: Celestin NZEYIMANA

import platform
import psutil
import os
import socket
import time
import subprocess
import re
import datetime
from rich import print
from rich.table import Table
from rich.console import Console

console = Console()

AUTH_LOG_PATH = "/var/log/auth.log"

def get_system_info():
    os_type = platform.system()
    os_details = platform.uname()
    

# what the script does if the given system is windows

    if os_type == "Windows":
        return {
            "OS Type": os_type,
            "OS Version": os_details.version,
            "Node Name": os_details.node,
            "Release": os_details.release,
            "Machine": os_details.machine,
            "Processor": os_details.processor
        }
    
    # what the script does if the given system is linux
    elif os_type == "Linux":
        return {
            "OS Type": os_type,
            "Node Name": os_details.node,
            "Release": os_details.release,
            "Machine": os_details.machine,
            "Processor": os_details.processor,
            "Distribution": " ".join(platform.linux_distribution())
        }
    else:
        return {"OS Type": os_type}

#Fetching the system info
def display_system_info(system_info):
    table = Table(title="System Information")
    table.add_column("Property", justify="right", style="cyan")
    table.add_column("Value", justify="left", style="white")
    
    for key, value in system_info.items():
        table.add_row(key, str(value))
    console.print(table)

#Getting and displaying the network information
def get_network_info():
    hostname = socket.gethostname()
    private_ip = socket.gethostbyname(hostname)
    public_ip = subprocess.check_output(['curl', 'ifconfig.me']).decode('utf-8').strip()
    
    default_gateway = psutil.net_if_addrs()['en0'][1].address if 'en0' in psutil.net_if_addrs() else "Unknown"
    
    return {
        "Hostname": hostname,
        "Private IP": private_ip,
        "Public IP": public_ip,
        "Default Gateway": default_gateway
    }

def display_network_info(network_info):
    table = Table(title="Network Information")
    table.add_column("Property", justify="right", style="green")
    table.add_column("Value", justify="left", style="white")
    
    for key, value in network_info.items():
        table.add_row(key, str(value))
    console.print(table)


#Getting and displaying the disk information
def get_disk_info():
    partitions = psutil.disk_partitions()
    disk_usage = {}
    for partition in partitions:
        if partition.fstype:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_usage[partition.mountpoint] = {
                "Total Size": usage.total,
                "Used": usage.used,
                "Free": usage.free,
                "Percentage Used": usage.percent
            }
    return disk_usage

def display_disk_info(disk_info):
    for partition, usage in disk_info.items():
        table = Table(title=f"Disk Information - {partition}")
        table.add_column("Property", justify="right", style="magenta")
        table.add_column("Value", justify="left", style="white")
        
        for key, value in usage.items():
            table.add_row(key, str(value))
        console.print(table)


#Getting and displaying the top 5 largest directories
def get_largest_directories(path="/"):
    directories = {}
    for dirpath, dirnames, filenames in os.walk(path):
        total_size = sum(os.path.getsize(os.path.join(dirpath, f)) for f in filenames)
        directories[dirpath] = total_size

    sorted_dirs = sorted(directories.items(), key=lambda x: x[1], reverse=True)
    return sorted_dirs[:5]

def display_largest_directories(directories):
    table = Table(title="Largest Directories")
    table.add_column("Directory", justify="left", style="yellow")
    table.add_column("Size", justify="right", style="white")
    for dirpath, size in directories:
        table.add_row(dirpath, str(size))
    console.print(table)


#Monitoring the CPU Usage percentages every 10 seconds
def monitor_cpu_usage(interval=10):
    try:
        while True:
            console.print(f"[bold red]CPU Usage: {psutil.cpu_percent(interval=interval)}%[/bold red]")
    except KeyboardInterrupt:
        console.print("[bold green]CPU monitoring stopped.[/bold green]")


#Parsing the auth.log file on the UNIX-based systems 
def parse_auth_log():
    new_users = []
    deleted_users = []
    password_changes = []
    su_usage = []
    sudo_usage = []
    sudo_failures = []

    with open(AUTH_LOG_PATH, 'r') as file:
        for line in file:
            timestamp = line[:15]
            datetime_obj = datetime.datetime.strptime(timestamp, '%b %d %H:%M:%S')
            
            if re.search(r'new user', line):
                new_users.append((datetime_obj, line))
            elif re.search(r'deleted user', line):
                deleted_users.append((datetime_obj, line))
            elif re.search(r'password changed', line):
                password_changes.append((datetime_obj, line))
            elif re.search(r' su ', line):
                su_usage.append((datetime_obj, line))
            elif re.search(r'sudo: ', line):
                if 'command not found' in line:
                    sudo_failures.append((datetime_obj, line))
                else:
                    sudo_usage.append((datetime_obj, line))
    
    return {
        "New Users": new_users,
        "Deleted Users": deleted_users,
        "Password Changes": password_changes,
        "su Command Usage": su_usage,
        "sudo Command Usage": sudo_usage,
        "sudo Command Failures": sudo_failures
    }

def display_auth_log_info(log_info):
    for category, entries in log_info.items():
        table = Table(title=f"{category}")
        table.add_column("Timestamp", justify="left", style="blue")
        table.add_column("Log Entry", justify="left", style="white")
        
        for entry in entries:
            table.add_row(str(entry[0]), entry[1].strip())
        console.print(table)

def main():
    console.print("[bold cyan]System Information[/bold cyan]")
    display_system_info(get_system_info())
    
    console.print("\n[bold green]Network Information[/bold green]")
    display_network_info(get_network_info())
    
    console.print("\n[bold magenta]Disk Information[/bold magenta]")
    display_disk_info(get_disk_info())
    
    console.print("\n[bold yellow]Largest Directories[/bold yellow]")
    display_largest_directories(get_largest_directories())
    
    console.print("\n[bold red]Monitoring CPU Usage (Press Ctrl+C to stop)[/bold red]")
    monitor_cpu_usage()

    console.print("\n[bold blue]Auth Log Information[/bold blue]")
    display_auth_log_info(parse_auth_log())

if __name__ == "__main__":
    main()
