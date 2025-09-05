#!/usr/bin/env python3
"""
Bazzite Gaming Performance Monitor & Dashboard
Real-time system monitoring with gaming-specific metrics
Version: 1.0.0
"""

import os
import sys
import time
import json
import psutil
import subprocess
import threading
import curses
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import Dict, List, Tuple, Optional
import signal
import argparse

# ============================================================================
# ANSI COLOR CODES
# ============================================================================

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    CLEAR = '\033[2J\033[H'

# ============================================================================
# PERFORMANCE METRICS COLLECTOR
# ============================================================================

class MetricsCollector:
    """Collect system performance metrics"""
    
    def __init__(self):
        self.history_size = 60  # Keep 60 seconds of history
        self.cpu_history = deque(maxlen=self.history_size)
        self.gpu_history = deque(maxlen=self.history_size)
        self.ram_history = deque(maxlen=self.history_size)
        self.temp_history = deque(maxlen=self.history_size)
        self.fps_history = deque(maxlen=self.history_size)
        
    def get_cpu_metrics(self) -> Dict:
        """Get CPU performance metrics"""
        try:
            # CPU usage per core
            per_cpu = psutil.cpu_percent(percpu=True)
            
            # CPU frequency
            freq = psutil.cpu_freq()
            
            # CPU temperature (Intel specific)
            temp = self._get_cpu_temp()
            
            # Load average
            load_avg = os.getloadavg()
            
            return {
                'usage': psutil.cpu_percent(),
                'per_core': per_cpu,
                'frequency': freq.current if freq else 0,
                'max_freq': freq.max if freq else 0,
                'temperature': temp,
                'load_avg': load_avg,
                'cores': psutil.cpu_count(logical=False),
                'threads': psutil.cpu_count(logical=True)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_gpu_metrics(self) -> Dict:
        """Get NVIDIA GPU metrics"""
        try:
            # Use nvidia-smi for GPU metrics
            cmd = "nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,clocks.gr,clocks.mem,power.draw --format=csv,noheader,nounits"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                values = result.stdout.strip().split(', ')
                return {
                    'usage': float(values[0]),
                    'memory_used': float(values[1]),
                    'memory_total': float(values[2]),
                    'temperature': float(values[3]),
                    'clock_graphics': float(values[4]),
                    'clock_memory': float(values[5]),
                    'power_draw': float(values[6])
                }
        except Exception as e:
            return {'error': str(e)}
        
        return {}
    
    def get_memory_metrics(self) -> Dict:
        """Get RAM metrics"""
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'total': mem.total,
                'used': mem.used,
                'available': mem.available,
                'percent': mem.percent,
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_percent': swap.percent
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_disk_metrics(self) -> Dict:
        """Get disk I/O metrics"""
        try:
            io_counters = psutil.disk_io_counters()
            
            return {
                'read_bytes': io_counters.read_bytes,
                'write_bytes': io_counters.write_bytes,
                'read_count': io_counters.read_count,
                'write_count': io_counters.write_count,
                'read_time': io_counters.read_time,
                'write_time': io_counters.write_time
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_network_metrics(self) -> Dict:
        """Get network metrics"""
        try:
            net = psutil.net_io_counters()
            
            return {
                'bytes_sent': net.bytes_sent,
                'bytes_recv': net.bytes_recv,
                'packets_sent': net.packets_sent,
                'packets_recv': net.packets_recv,
                'errin': net.errin,
                'errout': net.errout,
                'dropin': net.dropin,
                'dropout': net.dropout
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_gaming_metrics(self) -> Dict:
        """Get gaming-specific metrics"""
        metrics = {}
        
        # Check if Steam is running
        steam_running = self._is_process_running('steam')
        metrics['steam_running'] = steam_running
        
        # Check if GameMode is active
        gamemode_active = self._check_gamemode()
        metrics['gamemode_active'] = gamemode_active
        
        # Check if MangoHud is running
        mangohud_running = self._is_process_running('mangohud')
        metrics['mangohud_active'] = mangohud_running
        
        # Get Proton games running
        proton_games = self._get_proton_games()
        metrics['proton_games'] = proton_games
        
        # Check compositor status (KWin)
        compositor_active = self._check_compositor()
        metrics['compositor_active'] = compositor_active
        
        return metrics
    
    def _get_cpu_temp(self) -> float:
        """Get CPU temperature"""
        try:
            # Try different methods to get CPU temp
            # Method 1: coretemp
            temp_files = Path('/sys/class/hwmon').glob('*/temp*_input')
            temps = []
            
            for temp_file in temp_files:
                try:
                    with open(temp_file, 'r') as f:
                        temp = float(f.read().strip()) / 1000.0
                        if temp > 0 and temp < 150:  # Sanity check
                            temps.append(temp)
                except:
                    continue
            
            if temps:
                return max(temps)  # Return highest temp
            
        except:
            pass
        
        return 0.0
    
    def _is_process_running(self, process_name: str) -> bool:
        """Check if a process is running"""
        for proc in psutil.process_iter(['name']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    return True
            except:
                continue
        return False
    
    def _check_gamemode(self) -> bool:
        """Check if GameMode is active"""
        try:
            result = subprocess.run("gamemoded -s", shell=True, capture_output=True, text=True)
            return "is active" in result.stdout.lower()
        except:
            return False
    
    def _get_proton_games(self) -> List[str]:
        """Get list of running Proton games"""
        games = []
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'proton' in cmdline.lower() and 'wine' in cmdline.lower():
                    # Extract game name from process
                    games.append(proc.info['name'])
            except:
                continue
        return games
    
    def _check_compositor(self) -> bool:
        """Check if KWin compositor is active"""
        try:
            result = subprocess.run("qdbus org.kde.KWin /Compositor active", 
                                  shell=True, capture_output=True, text=True)
            return "true" in result.stdout.lower()
        except:
            return True  # Assume active if can't check

# ============================================================================
# TERMINAL DASHBOARD
# ============================================================================

class TerminalDashboard:
    """Real-time terminal dashboard using curses"""
    
    def __init__(self):
        self.collector = MetricsCollector()
        self.running = True
        self.update_interval = 1.0  # Update every second
        
    def start(self, stdscr):
        """Start the dashboard"""
        # Configure curses
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(1)    # Non-blocking input
        stdscr.timeout(100)  # Refresh timeout
        
        # Initialize colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        
        while self.running:
            try:
                # Clear screen
                stdscr.clear()
                
                # Get terminal size
                height, width = stdscr.getmaxyx()
                
                # Collect metrics
                cpu_metrics = self.collector.get_cpu_metrics()
                gpu_metrics = self.collector.get_gpu_metrics()
                mem_metrics = self.collector.get_memory_metrics()
                disk_metrics = self.collector.get_disk_metrics()
                net_metrics = self.collector.get_network_metrics()
                gaming_metrics = self.collector.get_gaming_metrics()
                
                # Draw header
                self._draw_header(stdscr, width)
                
                # Draw sections
                row = 3
                row = self._draw_cpu_section(stdscr, cpu_metrics, row, width)
                row = self._draw_gpu_section(stdscr, gpu_metrics, row, width)
                row = self._draw_memory_section(stdscr, mem_metrics, row, width)
                row = self._draw_gaming_section(stdscr, gaming_metrics, row, width)
                row = self._draw_network_section(stdscr, net_metrics, row, width)
                
                # Draw footer
                self._draw_footer(stdscr, height, width)
                
                # Refresh display
                stdscr.refresh()
                
                # Check for quit key
                key = stdscr.getch()
                if key == ord('q') or key == ord('Q'):
                    self.running = False
                
                # Sleep
                time.sleep(self.update_interval)
                
            except KeyboardInterrupt:
                self.running = False
            except curses.error:
                pass  # Ignore curses errors (terminal resize, etc)
    
    def _draw_header(self, stdscr, width):
        """Draw dashboard header"""
        title = "🎮 BAZZITE GAMING PERFORMANCE MONITOR 🎮"
        subtitle = f"RTX 5080 | i9-10850K | 64GB RAM | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Center the title
        title_x = max(0, (width - len(title)) // 2)
        subtitle_x = max(0, (width - len(subtitle)) // 2)
        
        stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
        stdscr.addstr(0, title_x, title)
        stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)
        
        stdscr.attron(curses.color_pair(5))
        stdscr.addstr(1, subtitle_x, subtitle)
        stdscr.attroff(curses.color_pair(5))
        
        # Draw separator
        stdscr.addstr(2, 0, "─" * width)
    
    def _draw_cpu_section(self, stdscr, metrics, start_row, width):
        """Draw CPU metrics section"""
        row = start_row
        
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(row, 0, "CPU METRICS")
        stdscr.attroff(curses.A_BOLD)
        row += 1
        
        if 'error' not in metrics:
            # Overall usage
            usage = metrics.get('usage', 0)
            color = self._get_color_for_value(usage, 50, 80)
            stdscr.addstr(row, 2, f"Usage: ")
            stdscr.attron(curses.color_pair(color))
            stdscr.addstr(f"{usage:.1f}%")
            stdscr.attroff(curses.color_pair(color))
            
            # Frequency
            freq = metrics.get('frequency', 0)
            max_freq = metrics.get('max_freq', 0)
            stdscr.addstr(row, 25, f"Freq: {freq:.0f}/{max_freq:.0f} MHz")
            
            # Temperature
            temp = metrics.get('temperature', 0)
            if temp > 0:
                temp_color = self._get_color_for_value(temp, 60, 80)
                stdscr.addstr(row, 50, f"Temp: ")
                stdscr.attron(curses.color_pair(temp_color))
                stdscr.addstr(f"{temp:.1f}°C")
                stdscr.attroff(curses.color_pair(temp_color))
            row += 1
            
            # Per-core usage (simplified view)
            per_core = metrics.get('per_core', [])
            if per_core:
                stdscr.addstr(row, 2, "Cores: ")
                for i, core_usage in enumerate(per_core[:8]):  # Show first 8 cores
                    color = self._get_color_for_value(core_usage, 50, 80)
                    stdscr.attron(curses.color_pair(color))
                    stdscr.addstr(f"█" if core_usage > 75 else "▓" if core_usage > 50 else "▒" if core_usage > 25 else "░")
                    stdscr.attroff(curses.color_pair(color))
                row += 1
            
            # Load average
            load_avg = metrics.get('load_avg', (0, 0, 0))
            stdscr.addstr(row, 2, f"Load: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}")
            row += 1
        
        return row + 1
    
    def _draw_gpu_section(self, stdscr, metrics, start_row, width):
        """Draw GPU metrics section"""
        row = start_row
        
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(row, 0, "GPU METRICS (RTX 5080)")
        stdscr.attroff(curses.A_BOLD)
        row += 1
        
        if metrics and 'error' not in metrics:
            # GPU usage
            usage = metrics.get('usage', 0)
            color = self._get_color_for_value(usage, 50, 80)
            stdscr.addstr(row, 2, f"Usage: ")
            stdscr.attron(curses.color_pair(color))
            stdscr.addstr(f"{usage:.1f}%")
            stdscr.attroff(curses.color_pair(color))
            
            # Temperature
            temp = metrics.get('temperature', 0)
            temp_color = self._get_color_for_value(temp, 70, 85)
            stdscr.addstr(row, 25, f"Temp: ")
            stdscr.attron(curses.color_pair(temp_color))
            stdscr.addstr(f"{temp:.0f}°C")
            stdscr.attroff(curses.color_pair(temp_color))
            
            # Power draw
            power = metrics.get('power_draw', 0)
            stdscr.addstr(row, 50, f"Power: {power:.0f}W")
            row += 1
            
            # VRAM usage
            vram_used = metrics.get('memory_used', 0)
            vram_total = metrics.get('memory_total', 0)
            if vram_total > 0:
                vram_percent = (vram_used / vram_total) * 100
                color = self._get_color_for_value(vram_percent, 50, 80)
                stdscr.addstr(row, 2, f"VRAM: ")
                stdscr.attron(curses.color_pair(color))
                stdscr.addstr(f"{vram_used:.0f}/{vram_total:.0f} MB ({vram_percent:.1f}%)")
                stdscr.attroff(curses.color_pair(color))
            row += 1
            
            # Clocks
            core_clock = metrics.get('clock_graphics', 0)
            mem_clock = metrics.get('clock_memory', 0)
            stdscr.addstr(row, 2, f"Clocks: Core {core_clock:.0f} MHz, Memory {mem_clock:.0f} MHz")
            row += 1
        else:
            stdscr.addstr(row, 2, "GPU data unavailable")
            row += 1
        
        return row + 1
    
    def _draw_memory_section(self, stdscr, metrics, start_row, width):
        """Draw memory metrics section"""
        row = start_row
        
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(row, 0, "MEMORY METRICS")
        stdscr.attroff(curses.A_BOLD)
        row += 1
        
        if 'error' not in metrics:
            # RAM usage
            total_gb = metrics.get('total', 0) / (1024**3)
            used_gb = metrics.get('used', 0) / (1024**3)
            percent = metrics.get('percent', 0)
            
            color = self._get_color_for_value(percent, 50, 80)
            stdscr.addstr(row, 2, f"RAM: ")
            stdscr.attron(curses.color_pair(color))
            stdscr.addstr(f"{used_gb:.1f}/{total_gb:.1f} GB ({percent:.1f}%)")
            stdscr.attroff(curses.color_pair(color))
            row += 1
            
            # Swap usage
            swap_total = metrics.get('swap_total', 0) / (1024**3)
            swap_used = metrics.get('swap_used', 0) / (1024**3)
            swap_percent = metrics.get('swap_percent', 0)
            
            if swap_total > 0:
                stdscr.addstr(row, 2, f"Swap: {swap_used:.1f}/{swap_total:.1f} GB ({swap_percent:.1f}%)")
                row += 1
        
        return row + 1
    
    def _draw_gaming_section(self, stdscr, metrics, start_row, width):
        """Draw gaming status section"""
        row = start_row
        
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(row, 0, "GAMING STATUS")
        stdscr.attroff(curses.A_BOLD)
        row += 1
        
        # Steam status
        steam = metrics.get('steam_running', False)
        color = 1 if steam else 3
        stdscr.addstr(row, 2, "Steam: ")
        stdscr.attron(curses.color_pair(color))
        stdscr.addstr("RUNNING" if steam else "NOT RUNNING")
        stdscr.attroff(curses.color_pair(color))
        
        # GameMode status
        gamemode = metrics.get('gamemode_active', False)
        color = 1 if gamemode else 2
        stdscr.addstr(row, 25, "GameMode: ")
        stdscr.attron(curses.color_pair(color))
        stdscr.addstr("ACTIVE" if gamemode else "INACTIVE")
        stdscr.attroff(curses.color_pair(color))
        
        # Compositor status
        compositor = metrics.get('compositor_active', True)
        color = 2 if compositor else 1
        stdscr.addstr(row, 50, "Compositor: ")
        stdscr.attron(curses.color_pair(color))
        stdscr.addstr("ON" if compositor else "OFF")
        stdscr.attroff(curses.color_pair(color))
        row += 1
        
        # Proton games
        games = metrics.get('proton_games', [])
        if games:
            stdscr.addstr(row, 2, f"Proton Games: {', '.join(games[:3])}")  # Show first 3
            row += 1
        
        return row + 1
    
    def _draw_network_section(self, stdscr, metrics, start_row, width):
        """Draw network metrics section"""
        row = start_row
        
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(row, 0, "NETWORK METRICS")
        stdscr.attroff(curses.A_BOLD)
        row += 1
        
        if 'error' not in metrics:
            # Calculate rates (this is simplified, should track over time)
            bytes_sent = metrics.get('bytes_sent', 0) / (1024**2)  # MB
            bytes_recv = metrics.get('bytes_recv', 0) / (1024**2)  # MB
            
            stdscr.addstr(row, 2, f"Total: ↑ {bytes_sent:.1f} MB  ↓ {bytes_recv:.1f} MB")
            row += 1
            
            # Errors and drops
            errors = metrics.get('errin', 0) + metrics.get('errout', 0)
            drops = metrics.get('dropin', 0) + metrics.get('dropout', 0)
            
            if errors > 0 or drops > 0:
                color = 3 if errors > 0 else 2
                stdscr.attron(curses.color_pair(color))
                stdscr.addstr(row, 2, f"Errors: {errors}  Drops: {drops}")
                stdscr.attroff(curses.color_pair(color))
                row += 1
        
        return row + 1
    
    def _draw_footer(self, stdscr, height, width):
        """Draw dashboard footer"""
        footer = "Press 'q' to quit | F1: Help | F2: Settings | F3: Logs"
        footer_row = height - 1
        
        stdscr.addstr(footer_row - 1, 0, "─" * width)
        stdscr.attron(curses.color_pair(4))
        stdscr.addstr(footer_row, 0, footer)
        stdscr.attroff(curses.color_pair(4))
    
    def _get_color_for_value(self, value, warning_threshold, critical_threshold):
        """Get color pair based on value and thresholds"""
        if value >= critical_threshold:
            return 3  # Red
        elif value >= warning_threshold:
            return 2  # Yellow
        else:
            return 1  # Green

# ============================================================================
# JSON METRICS EXPORTER
# ============================================================================

class MetricsExporter:
    """Export metrics to JSON for external monitoring"""
    
    def __init__(self, output_dir: Path = Path("/var/log/gaming-metrics")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.collector = MetricsCollector()
    
    def export_current_metrics(self) -> Path:
        """Export current metrics to JSON file"""
        timestamp = datetime.now().isoformat()
        
        metrics = {
            'timestamp': timestamp,
            'cpu': self.collector.get_cpu_metrics(),
            'gpu': self.collector.get_gpu_metrics(),
            'memory': self.collector.get_memory_metrics(),
            'disk': self.collector.get_disk_metrics(),
            'network': self.collector.get_network_metrics(),
            'gaming': self.collector.get_gaming_metrics()
        }
        
        # Write to timestamped file
        filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Also update latest.json
        latest_path = self.output_dir / "latest.json"
        with open(latest_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        return filepath
    
    def start_continuous_export(self, interval: int = 5):
        """Start continuous metrics export"""
        print(f"Starting continuous metrics export (interval: {interval}s)")
        print(f"Output directory: {self.output_dir}")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                filepath = self.export_current_metrics()
                print(f"Exported metrics to {filepath}")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nStopping metrics export")

# ============================================================================
# SIMPLE CONSOLE MONITOR
# ============================================================================

class SimpleMonitor:
    """Simple console-based monitor without curses"""
    
    def __init__(self):
        self.collector = MetricsCollector()
    
    def display_once(self):
        """Display metrics once"""
        print(Colors.CLEAR)
        print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}  BAZZITE GAMING PERFORMANCE MONITOR{Colors.ENDC}")
        print(f"{Colors.OKCYAN}  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
        
        # CPU metrics
        cpu = self.collector.get_cpu_metrics()
        if 'error' not in cpu:
            print(f"\n{Colors.OKBLUE}CPU METRICS:{Colors.ENDC}")
            print(f"  Usage: {self._color_value(cpu.get('usage', 0), 50, 80)}%")
            print(f"  Frequency: {cpu.get('frequency', 0):.0f}/{cpu.get('max_freq', 0):.0f} MHz")
            temp = cpu.get('temperature', 0)
            if temp > 0:
                print(f"  Temperature: {self._color_value(temp, 60, 80)}°C")
            load = cpu.get('load_avg', (0, 0, 0))
            print(f"  Load Average: {load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f}")
        
        # GPU metrics
        gpu = self.collector.get_gpu_metrics()
        if gpu and 'error' not in gpu:
            print(f"\n{Colors.OKBLUE}GPU METRICS (RTX 5080):{Colors.ENDC}")
            print(f"  Usage: {self._color_value(gpu.get('usage', 0), 50, 80)}%")
            print(f"  Temperature: {self._color_value(gpu.get('temperature', 0), 70, 85)}°C")
            print(f"  Power Draw: {gpu.get('power_draw', 0):.0f}W")
            vram_used = gpu.get('memory_used', 0)
            vram_total = gpu.get('memory_total', 0)
            if vram_total > 0:
                vram_percent = (vram_used / vram_total) * 100
                print(f"  VRAM: {vram_used:.0f}/{vram_total:.0f} MB ({self._color_value(vram_percent, 50, 80)}%)")
            print(f"  Core Clock: {gpu.get('clock_graphics', 0):.0f} MHz")
            print(f"  Memory Clock: {gpu.get('clock_memory', 0):.0f} MHz")
        
        # Memory metrics
        mem = self.collector.get_memory_metrics()
        if 'error' not in mem:
            print(f"\n{Colors.OKBLUE}MEMORY METRICS:{Colors.ENDC}")
            total_gb = mem.get('total', 0) / (1024**3)
            used_gb = mem.get('used', 0) / (1024**3)
            percent = mem.get('percent', 0)
            print(f"  RAM: {used_gb:.1f}/{total_gb:.1f} GB ({self._color_value(percent, 50, 80)}%)")
            
            swap_total = mem.get('swap_total', 0) / (1024**3)
            if swap_total > 0:
                swap_used = mem.get('swap_used', 0) / (1024**3)
                swap_percent = mem.get('swap_percent', 0)
                print(f"  Swap: {swap_used:.1f}/{swap_total:.1f} GB ({swap_percent:.1f}%)")
        
        # Gaming status
        gaming = self.collector.get_gaming_metrics()
        print(f"\n{Colors.OKBLUE}GAMING STATUS:{Colors.ENDC}")
        
        steam = gaming.get('steam_running', False)
        print(f"  Steam: {self._status_color(steam, 'RUNNING', 'NOT RUNNING')}")
        
        gamemode = gaming.get('gamemode_active', False)
        print(f"  GameMode: {self._status_color(gamemode, 'ACTIVE', 'INACTIVE')}")
        
        compositor = gaming.get('compositor_active', True)
        print(f"  Compositor: {self._status_color(not compositor, 'OFF (Good for gaming)', 'ON')}")
        
        games = gaming.get('proton_games', [])
        if games:
            print(f"  Proton Games: {', '.join(games)}")
        
        print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
    
    def monitor_continuous(self, interval: int = 2):
        """Continuous monitoring"""
        print("Starting continuous monitoring (Press Ctrl+C to stop)")
        
        try:
            while True:
                self.display_once()
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Monitoring stopped{Colors.ENDC}")
    
    def _color_value(self, value, warning, critical):
        """Color a value based on thresholds"""
        if value >= critical:
            return f"{Colors.FAIL}{value:.1f}{Colors.ENDC}"
        elif value >= warning:
            return f"{Colors.WARNING}{value:.1f}{Colors.ENDC}"
        else:
            return f"{Colors.OKGREEN}{value:.1f}{Colors.ENDC}"
    
    def _status_color(self, condition, true_text, false_text):
        """Color status text"""
        if condition:
            return f"{Colors.OKGREEN}{true_text}{Colors.ENDC}"
        else:
            return f"{Colors.WARNING}{false_text}{Colors.ENDC}"

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Gaming Performance Monitor')
    parser.add_argument('--mode', choices=['dashboard', 'simple', 'export'], 
                       default='dashboard',
                       help='Monitoring mode')
    parser.add_argument('--interval', type=int, default=2,
                       help='Update interval in seconds')
    parser.add_argument('--export-dir', type=str, 
                       default='/var/log/gaming-metrics',
                       help='Directory for metric exports')
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'dashboard':
            # Start curses dashboard
            dashboard = TerminalDashboard()
            curses.wrapper(dashboard.start)
        
        elif args.mode == 'simple':
            # Simple console monitor
            monitor = SimpleMonitor()
            monitor.monitor_continuous(args.interval)
        
        elif args.mode == 'export':
            # JSON export mode
            exporter = MetricsExporter(Path(args.export_dir))
            exporter.start_continuous_export(args.interval)
    
    except KeyboardInterrupt:
        print("\nShutting down...")
        return 0
    except Exception as e:
        print(f"{Colors.FAIL}Error: {str(e)}{Colors.ENDC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())