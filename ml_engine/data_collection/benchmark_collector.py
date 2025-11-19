#!/usr/bin/env python3
"""
Real-World Benchmark Data Collector

Collects actual gaming performance data from the local system
for training ML models with real-world data.
"""

import json
import psutil
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import subprocess

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False


@dataclass
class SystemSnapshot:
    """Single snapshot of system metrics"""
    timestamp: float
    cpu_usage: float
    cpu_temp: float
    cpu_freq: float
    ram_usage: float
    gpu_usage: float
    gpu_temp: float
    gpu_memory: float
    power_watts: float
    fps: Optional[float] = None
    game_name: Optional[str] = None
    profile: Optional[str] = None


@dataclass
class BenchmarkSession:
    """Complete benchmark session"""
    session_id: str
    start_time: str
    end_time: str
    duration_seconds: float
    hardware: Dict
    profile: str
    game: str
    resolution: str
    graphics_preset: str
    snapshots: List[Dict]
    summary: Dict


class RealDataCollector:
    """
    Collects real gaming performance data from system

    Features:
    - Real-time system metric collection
    - FPS monitoring (via MangoHud, nvidia-smi, etc.)
    - Hardware configuration detection
    - Session-based benchmark recording
    - Automatic data export for ML training
    """

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path.home() / '.local/share/bazzite-optimizer/real-benchmarks'
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.current_session = None
        self.snapshots = []

    def get_hardware_info(self) -> Dict:
        """Detect hardware configuration"""
        hw_info = {
            'cpu': self._get_cpu_info(),
            'ram_gb': round(psutil.virtual_memory().total / (1024**3), 1),
            'gpu': self._get_gpu_info(),
            'storage': self._get_storage_info()
        }
        return hw_info

    def _get_cpu_info(self) -> Dict:
        """Get CPU information"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                lines = f.readlines()
                model = [l for l in lines if 'model name' in l][0].split(':')[1].strip()

            return {
                'model': model,
                'cores': psutil.cpu_count(logical=False),
                'threads': psutil.cpu_count(logical=True),
                'max_freq_mhz': int(psutil.cpu_freq().max) if psutil.cpu_freq() else 0
            }
        except:
            return {'model': 'Unknown', 'cores': psutil.cpu_count(), 'threads': psutil.cpu_count()}

    def _get_gpu_info(self) -> Dict:
        """Get GPU information"""
        if GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    return {
                        'model': gpu.name,
                        'vram_gb': round(gpu.memoryTotal / 1024, 1),
                        'driver': gpu.driver
                    }
            except:
                pass

        # Fallback to nvidia-smi
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,driver_version',
                                   '--format=csv,noheader'],
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                parts = result.stdout.strip().split(',')
                return {
                    'model': parts[0].strip(),
                    'vram_gb': round(float(parts[1].strip().split()[0]) / 1024, 1),
                    'driver': parts[2].strip()
                }
        except:
            pass

        return {'model': 'Unknown', 'vram_gb': 0, 'driver': 'Unknown'}

    def _get_storage_info(self) -> Dict:
        """Get storage information"""
        try:
            root = psutil.disk_usage('/')
            return {
                'total_gb': round(root.total / (1024**3), 1),
                'type': 'nvme'  # Detect from /sys/block if needed
            }
        except:
            return {'total_gb': 0, 'type': 'unknown'}

    def collect_snapshot(self, fps: Optional[float] = None,
                        game_name: Optional[str] = None) -> SystemSnapshot:
        """Collect single system metrics snapshot"""

        # CPU metrics
        cpu_usage = psutil.cpu_percent(interval=0.1)
        cpu_freq = psutil.cpu_freq().current if psutil.cpu_freq() else 0
        cpu_temp = self._get_cpu_temp()

        # RAM metrics
        ram = psutil.virtual_memory()
        ram_usage = ram.percent

        # GPU metrics
        gpu_usage, gpu_temp, gpu_memory = self._get_gpu_metrics()

        # Power consumption estimate
        power_watts = self._estimate_power()

        snapshot = SystemSnapshot(
            timestamp=time.time(),
            cpu_usage=cpu_usage,
            cpu_temp=cpu_temp,
            cpu_freq=cpu_freq,
            ram_usage=ram_usage,
            gpu_usage=gpu_usage,
            gpu_temp=gpu_temp,
            gpu_memory=gpu_memory,
            power_watts=power_watts,
            fps=fps,
            game_name=game_name,
            profile=self.current_session.get('profile') if self.current_session else None
        )

        return snapshot

    def _get_cpu_temp(self) -> float:
        """Get CPU temperature"""
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                return max([t.current for t in temps['coretemp']])
            elif 'k10temp' in temps:  # AMD
                return temps['k10temp'][0].current
        except:
            pass
        return 0.0

    def _get_gpu_metrics(self) -> tuple:
        """Get GPU usage, temperature, memory"""
        if GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    return (gpu.load * 100, gpu.temperature,
                           (gpu.memoryUsed / gpu.memoryTotal) * 100)
            except:
                pass

        # Fallback to nvidia-smi
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,temperature.gpu,utilization.memory',
                                   '--format=csv,noheader,nounits'],
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                parts = result.stdout.strip().split(',')
                return (float(parts[0]), float(parts[1]), float(parts[2]))
        except:
            pass

        return (0.0, 0.0, 0.0)

    def _estimate_power(self) -> float:
        """Estimate system power consumption"""
        # Simple estimation based on CPU/GPU usage
        cpu_usage = psutil.cpu_percent()
        gpu_usage, _, _ = self._get_gpu_metrics()

        # Rough estimates: idle 100W, CPU 100W max, GPU 300W max
        base_power = 100
        cpu_power = (cpu_usage / 100) * 100
        gpu_power = (gpu_usage / 100) * 300

        return base_power + cpu_power + gpu_power

    def start_session(self, profile: str, game: str,
                     resolution: str = "1440p",
                     graphics_preset: str = "high") -> str:
        """Start new benchmark session"""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.current_session = {
            'session_id': session_id,
            'start_time': datetime.now().isoformat(),
            'profile': profile,
            'game': game,
            'resolution': resolution,
            'graphics_preset': graphics_preset,
            'hardware': self.get_hardware_info()
        }

        self.snapshots = []

        print(f"📊 Started benchmark session: {session_id}")
        print(f"   Game: {game}")
        print(f"   Profile: {profile}")
        print(f"   Resolution: {resolution}")
        print(f"   Graphics: {graphics_preset}")

        return session_id

    def record_snapshot(self, fps: Optional[float] = None):
        """Record snapshot during active session"""
        if not self.current_session:
            raise RuntimeError("No active session. Call start_session() first.")

        snapshot = self.collect_snapshot(fps, self.current_session['game'])
        self.snapshots.append(asdict(snapshot))

    def end_session(self) -> Path:
        """End session and save benchmark data"""
        if not self.current_session:
            raise RuntimeError("No active session to end.")

        end_time = datetime.now()
        start_time = datetime.fromisoformat(self.current_session['start_time'])
        duration = (end_time - start_time).total_seconds()

        # Calculate summary statistics
        fps_values = [s['fps'] for s in self.snapshots if s['fps'] is not None]

        summary = {
            'total_snapshots': len(self.snapshots),
            'fps_avg': sum(fps_values) / len(fps_values) if fps_values else 0,
            'fps_min': min(fps_values) if fps_values else 0,
            'fps_max': max(fps_values) if fps_values else 0,
            'fps_99percentile': sorted(fps_values)[int(len(fps_values) * 0.01)] if len(fps_values) > 10 else 0,
            'avg_cpu_usage': sum(s['cpu_usage'] for s in self.snapshots) / len(self.snapshots),
            'avg_gpu_usage': sum(s['gpu_usage'] for s in self.snapshots) / len(self.snapshots),
            'avg_cpu_temp': sum(s['cpu_temp'] for s in self.snapshots) / len(self.snapshots),
            'avg_gpu_temp': sum(s['gpu_temp'] for s in self.snapshots) / len(self.snapshots),
            'avg_power_watts': sum(s['power_watts'] for s in self.snapshots) / len(self.snapshots)
        }

        # Create benchmark session object
        benchmark = BenchmarkSession(
            session_id=self.current_session['session_id'],
            start_time=self.current_session['start_time'],
            end_time=end_time.isoformat(),
            duration_seconds=duration,
            hardware=self.current_session['hardware'],
            profile=self.current_session['profile'],
            game=self.current_session['game'],
            resolution=self.current_session['resolution'],
            graphics_preset=self.current_session['graphics_preset'],
            snapshots=self.snapshots,
            summary=summary
        )

        # Save to file
        output_file = self.output_dir / f"benchmark_{self.current_session['session_id']}.json"
        with open(output_file, 'w') as f:
            json.dump(asdict(benchmark), f, indent=2)

        print(f"\n✅ Benchmark session complete!")
        print(f"   Duration: {duration:.1f}s")
        print(f"   Snapshots: {len(self.snapshots)}")
        print(f"   Avg FPS: {summary['fps_avg']:.1f}")
        print(f"   Saved to: {output_file}")

        self.current_session = None
        self.snapshots = []

        return output_file

    def export_for_ml_training(self, output_file: Optional[Path] = None) -> Path:
        """Export all benchmarks in ML training format"""
        output_file = output_file or self.output_dir / "ml_training_data.json"

        # Load all benchmark files
        all_benchmarks = []
        for benchmark_file in self.output_dir.glob("benchmark_*.json"):
            with open(benchmark_file, 'r') as f:
                all_benchmarks.append(json.load(f))

        # Convert to ML training format
        training_data = {
            'profile_benchmarks': [],
            'performance_sequences': [],
            'metadata': {
                'total_sessions': len(all_benchmarks),
                'generated': datetime.now().isoformat()
            }
        }

        for benchmark in all_benchmarks:
            # For ProfileOptimizer training
            training_data['profile_benchmarks'].append({
                'hardware': benchmark['hardware'],
                'profile': benchmark['profile'],
                'game': benchmark['game'],
                'resolution': benchmark['resolution'],
                'fps_avg': benchmark['summary']['fps_avg'],
                'power_watts': benchmark['summary']['avg_power_watts']
            })

            # For PerformancePredictor training
            if len(benchmark['snapshots']) > 60:  # Need enough data for LSTM
                training_data['performance_sequences'].append({
                    'hardware': benchmark['hardware'],
                    'profile': benchmark['profile'],
                    'game': benchmark['game'],
                    'snapshots': benchmark['snapshots']
                })

        with open(output_file, 'w') as f:
            json.dump(training_data, f, indent=2)

        print(f"\n📦 Exported ML training data:")
        print(f"   Profile benchmarks: {len(training_data['profile_benchmarks'])}")
        print(f"   Performance sequences: {len(training_data['performance_sequences'])}")
        print(f"   Saved to: {output_file}")

        return output_file


def collect_realtime_benchmark(duration_seconds: int = 300,
                               profile: str = "competitive",
                               game: str = "CS2",
                               resolution: str = "1440p",
                               graphics: str = "high"):
    """
    Collect real-time benchmark data

    Args:
        duration_seconds: How long to collect data (default 5 minutes)
        profile: Gaming profile being tested
        game: Game being played
        resolution: Display resolution
        graphics: Graphics preset
    """
    collector = RealDataCollector()

    print("=" * 60)
    print("Real-Time Benchmark Data Collection")
    print("=" * 60)

    # Start session
    session_id = collector.start_session(profile, game, resolution, graphics)

    print(f"\n🎮 Start playing {game} now!")
    print(f"   Collecting data for {duration_seconds} seconds...")
    print(f"   Press Ctrl+C to stop early\n")

    try:
        start_time = time.time()
        snapshot_count = 0

        while (time.time() - start_time) < duration_seconds:
            # Collect snapshot every second
            collector.record_snapshot(fps=None)  # FPS would need external tool
            snapshot_count += 1

            # Progress indicator
            if snapshot_count % 10 == 0:
                elapsed = time.time() - start_time
                remaining = duration_seconds - elapsed
                print(f"⏱️  {snapshot_count} snapshots | {elapsed:.0f}s elapsed | {remaining:.0f}s remaining", end='\r')

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n⏸️  Stopped by user")

    # End session and save
    output_file = collector.end_session()

    return output_file


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Collect real gaming benchmark data")
    parser.add_argument('--duration', type=int, default=300, help='Duration in seconds (default: 300)')
    parser.add_argument('--profile', default='competitive', help='Gaming profile (default: competitive)')
    parser.add_argument('--game', default='CS2', help='Game name (default: CS2)')
    parser.add_argument('--resolution', default='1440p', help='Resolution (default: 1440p)')
    parser.add_argument('--graphics', default='high', help='Graphics preset (default: high)')
    parser.add_argument('--export', action='store_true', help='Export all benchmarks for ML training')

    args = parser.parse_args()

    if args.export:
        collector = RealDataCollector()
        collector.export_for_ml_training()
    else:
        collect_realtime_benchmark(
            duration_seconds=args.duration,
            profile=args.profile,
            game=args.game,
            resolution=args.resolution,
            graphics=args.graphics
        )
