"""
Analytics Dashboard for Community Statistics

Provides web-based dashboard for visualizing community
benchmark data and model performance.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AnalyticsDashboard:
    """
    Analytics dashboard for community data visualization

    Generates statistics and provides data for web dashboard.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path.home() / '.local/share/bazzite-optimizer/community-data'
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def generate_dashboard_data(self) -> Dict:
        """
        Generate complete dashboard data

        Returns:
            Dashboard data dict with all statistics
        """
        return {
            'overview': self._get_overview_stats(),
            'profiles': self._get_profile_analytics(),
            'hardware': self._get_hardware_distribution(),
            'performance': self._get_performance_trends(),
            'games': self._get_game_statistics(),
            'timestamp': datetime.now().isoformat()
        }

    def _get_overview_stats(self) -> Dict:
        """Get overview statistics"""
        submissions_file = self.data_dir / 'submissions.json'

        if not submissions_file.exists():
            return {
                'total_benchmarks': 0,
                'unique_systems': 0,
                'last_updated': None
            }

        try:
            with open(submissions_file, 'r') as f:
                data = json.load(f)

            submissions = data.get('submissions', [])

            # Calculate date ranges
            if submissions:
                dates = [datetime.fromisoformat(s['timestamp']) for s in submissions]
                min_date = min(dates)
                max_date = max(dates)

                # Last 7 days submissions
                seven_days_ago = datetime.now() - timedelta(days=7)
                recent = len([d for d in dates if d > seven_days_ago])
            else:
                min_date = None
                max_date = None
                recent = 0

            return {
                'total_benchmarks': len(submissions),
                'unique_systems': len(set(s['hardware_hash'] for s in submissions)),
                'recent_submissions_7d': recent,
                'first_submission': min_date.isoformat() if min_date else None,
                'last_submission': max_date.isoformat() if max_date else None,
                'last_updated': data.get('last_updated')
            }

        except Exception as e:
            logger.error(f"Failed to get overview stats: {e}")
            return {}

    def _get_profile_analytics(self) -> Dict:
        """Get profile-specific analytics"""
        aggregated_file = self.data_dir / 'aggregated_stats.json'

        if not aggregated_file.exists():
            return {}

        try:
            with open(aggregated_file, 'r') as f:
                data = json.load(f)

            profiles = data.get('profiles', {})

            # Enhance with percentages
            total = sum(p['count'] for p in profiles.values())

            for profile in profiles:
                profiles[profile]['percentage'] = (profiles[profile]['count'] / total) * 100

            return profiles

        except Exception as e:
            logger.error(f"Failed to get profile analytics: {e}")
            return {}

    def _get_hardware_distribution(self) -> Dict:
        """Get hardware distribution statistics"""
        submissions_file = self.data_dir / 'submissions.json'

        if not submissions_file.exists():
            return {}

        try:
            with open(submissions_file, 'r') as f:
                data = json.load(f)

            submissions = data.get('submissions', [])

            # CPU cores distribution
            cpu_cores = {}
            for s in submissions:
                cores = s.get('cpu_cores', 0)
                cpu_cores[cores] = cpu_cores.get(cores, 0) + 1

            # RAM distribution
            ram_dist = {}
            for s in submissions:
                ram = s.get('ram_gb', 0)
                ram_dist[ram] = ram_dist.get(ram, 0) + 1

            # GPU vendors
            gpu_vendors = {}
            for s in submissions:
                vendor = s.get('gpu_vendor', 'unknown')
                gpu_vendors[vendor] = gpu_vendors.get(vendor, 0) + 1

            # GPU VRAM distribution
            vram_dist = {}
            for s in submissions:
                vram = s.get('gpu_vram_gb', 0)
                vram_dist[vram] = vram_dist.get(vram, 0) + 1

            return {
                'cpu_cores': cpu_cores,
                'ram_gb': ram_dist,
                'gpu_vendors': gpu_vendors,
                'gpu_vram_gb': vram_dist
            }

        except Exception as e:
            logger.error(f"Failed to get hardware distribution: {e}")
            return {}

    def _get_performance_trends(self) -> Dict:
        """Get performance trends over time"""
        submissions_file = self.data_dir / 'submissions.json'

        if not submissions_file.exists():
            return {}

        try:
            with open(submissions_file, 'r') as f:
                data = json.load(f)

            submissions = data.get('submissions', [])

            # Group by date
            daily_stats = {}

            for s in submissions:
                date = datetime.fromisoformat(s['timestamp']).date().isoformat()

                if date not in daily_stats:
                    daily_stats[date] = {
                        'count': 0,
                        'fps_sum': 0,
                        'power_sum': 0
                    }

                daily_stats[date]['count'] += 1
                daily_stats[date]['fps_sum'] += s.get('fps_avg', 0)
                daily_stats[date]['power_sum'] += s.get('power_watts', 0)

            # Calculate averages
            trends = []
            for date in sorted(daily_stats.keys()):
                stats = daily_stats[date]
                trends.append({
                    'date': date,
                    'benchmarks': stats['count'],
                    'avg_fps': stats['fps_sum'] / stats['count'],
                    'avg_power': stats['power_sum'] / stats['count']
                })

            return {
                'daily_trends': trends,
                'total_days': len(trends)
            }

        except Exception as e:
            logger.error(f"Failed to get performance trends: {e}")
            return {}

    def _get_game_statistics(self) -> Dict:
        """Get game-specific statistics"""
        aggregated_file = self.data_dir / 'aggregated_stats.json'

        if not aggregated_file.exists():
            return {}

        try:
            with open(aggregated_file, 'r') as f:
                data = json.load(f)

            games = data.get('games', {})

            # Sort by count
            sorted_games = sorted(
                games.items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )

            return {
                'top_games': sorted_games[:10],
                'total_game_types': len(games)
            }

        except Exception as e:
            logger.error(f"Failed to get game statistics: {e}")
            return {}

    def export_dashboard_html(self, output_file: Path) -> bool:
        """
        Export dashboard as standalone HTML

        Args:
            output_file: Output HTML file

        Returns:
            True if export successful
        """
        try:
            dashboard_data = self.generate_dashboard_data()

            html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Bazzite Optimizer Analytics Dashboard</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .card {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; margin-top: 0; }}
        .stat {{ display: inline-block; margin: 10px 20px; }}
        .stat-value {{ font-size: 32px; font-weight: bold; color: #4CAF50; }}
        .stat-label {{ color: #666; font-size: 14px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f0f0f0; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Bazzite Gaming Optimizer Analytics Dashboard</h1>

        <div class="card">
            <h2>Overview</h2>
            <div class="stat">
                <div class="stat-value">{dashboard_data['overview'].get('total_benchmarks', 0)}</div>
                <div class="stat-label">Total Benchmarks</div>
            </div>
            <div class="stat">
                <div class="stat-value">{dashboard_data['overview'].get('unique_systems', 0)}</div>
                <div class="stat-label">Unique Systems</div>
            </div>
            <div class="stat">
                <div class="stat-value">{dashboard_data['overview'].get('recent_submissions_7d', 0)}</div>
                <div class="stat-label">Recent (7d)</div>
            </div>
        </div>

        <div class="card">
            <h2>Profile Usage</h2>
            <table>
                <tr>
                    <th>Profile</th>
                    <th>Benchmarks</th>
                    <th>Avg FPS</th>
                    <th>Avg Power (W)</th>
                    <th>Usage %</th>
                </tr>
                {''.join(f'''
                <tr>
                    <td>{profile}</td>
                    <td>{data['count']}</td>
                    <td>{data.get('avg_fps', 0):.1f}</td>
                    <td>{data.get('avg_power', 0):.1f}</td>
                    <td>{data.get('percentage', 0):.1f}%</td>
                </tr>
                ''' for profile, data in dashboard_data['profiles'].items())}
            </table>
        </div>

        <div class="card">
            <h2>Hardware Distribution</h2>
            <h3>GPU Vendors</h3>
            <table>
                <tr>
                    <th>Vendor</th>
                    <th>Count</th>
                </tr>
                {''.join(f'''
                <tr>
                    <td>{vendor}</td>
                    <td>{count}</td>
                </tr>
                ''' for vendor, count in dashboard_data['hardware'].get('gpu_vendors', {}).items())}
            </table>
        </div>

        <p style="text-align: center; color: #999; margin-top: 40px;">
            Generated: {dashboard_data['timestamp']}<br>
            Bazzite Gaming Optimizer v1.3.0
        </p>
    </div>
</body>
</html>
"""

            with open(output_file, 'w') as f:
                f.write(html_template)

            logger.info(f"Dashboard exported to {output_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to export dashboard: {e}")
            return False
