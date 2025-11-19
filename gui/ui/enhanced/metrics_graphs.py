"""
Enhanced Metrics Graphs with Historical Data Visualization
Provides matplotlib-based historical graphs for CPU, GPU, Memory metrics
"""

import logging
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from collections import deque

try:
    import gi
    gi.require_version('Gtk', '4.0')
    from gi.repository import Gtk, GLib
except ImportError:
    pass

try:
    import matplotlib
    matplotlib.use('GTK4Agg')
    from matplotlib.backends.backend_gtk4agg import FigureCanvasGTK4Agg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logging.warning("matplotlib not available - historical graphs disabled")


class HistoricalMetricsGraph(Gtk.Box):
    """Historical metrics graph widget using matplotlib"""

    def __init__(self, title: str, metric_name: str, unit: str = "", color: str = "#3584e4"):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.title = title
        self.metric_name = metric_name
        self.unit = unit
        self.color = color
        self.logger = logging.getLogger(__name__)

        # Data storage (last 300 seconds = 5 minutes)
        self.max_data_points = 300
        self.timestamps: deque = deque(maxlen=self.max_data_points)
        self.values: deque = deque(maxlen=self.max_data_points)

        self._create_ui()

    def _create_ui(self):
        """Create the graph UI"""
        if not MATPLOTLIB_AVAILABLE:
            # Fallback to simple label if matplotlib not available
            label = Gtk.Label()
            label.set_markup(f"<b>{self.title}</b>\n(matplotlib required for graphs)")
            label.set_halign(Gtk.Align.CENTER)
            label.set_valign(Gtk.Align.CENTER)
            self.append(label)
            return

        # Create matplotlib figure
        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.figure.patch.set_facecolor('#1e1e1e')  # Dark background

        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#2d2d2d')
        self.ax.set_title(self.title, color='white', fontsize=12, fontweight='bold')
        self.ax.set_xlabel('Time', color='white')
        self.ax.set_ylabel(f'{self.metric_name} ({self.unit})', color='white')
        self.ax.tick_params(colors='white')
        self.ax.grid(True, alpha=0.3, color='gray')

        # Initialize empty plot
        self.line, = self.ax.plot([], [], color=self.color, linewidth=2)
        self.ax.set_xlim(0, 300)  # 5 minutes
        self.ax.set_ylim(0, 100)   # Will auto-adjust

        # Create canvas
        self.canvas = FigureCanvas(self.figure)
        self.canvas.set_size_request(800, 400)

        # Add canvas to widget
        self.append(self.canvas)

    def add_data_point(self, value: float, timestamp: Optional[datetime] = None):
        """Add a new data point to the graph"""
        if not MATPLOTLIB_AVAILABLE:
            return

        if timestamp is None:
            timestamp = datetime.now()

        self.timestamps.append(timestamp)
        self.values.append(value)

        self._update_graph()

    def _update_graph(self):
        """Update the graph with current data"""
        if not MATPLOTLIB_AVAILABLE or len(self.values) == 0:
            return

        try:
            # Convert timestamps to seconds from first timestamp
            if len(self.timestamps) > 0:
                first_time = self.timestamps[0]
                x_data = [(t - first_time).total_seconds() for t in self.timestamps]
            else:
                x_data = []

            y_data = list(self.values)

            # Update plot data
            self.line.set_data(x_data, y_data)

            # Auto-adjust y-axis
            if len(y_data) > 0:
                y_min = max(0, min(y_data) - 5)
                y_max = max(y_data) + 10
                self.ax.set_ylim(y_min, y_max)

            # Auto-adjust x-axis
            if len(x_data) > 0:
                x_max = max(x_data[-1] + 10, 60)  # At least 60 seconds
                self.ax.set_xlim(0, x_max)

            # Redraw canvas
            self.canvas.draw()

        except Exception as e:
            self.logger.error(f"Failed to update graph: {e}")

    def clear(self):
        """Clear all data"""
        self.timestamps.clear()
        self.values.clear()
        if MATPLOTLIB_AVAILABLE:
            self.line.set_data([], [])
            self.canvas.draw()


class MultiMetricsGraphPanel(Gtk.Box):
    """Panel containing multiple metrics graphs"""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)

        self.graphs: Dict[str, HistoricalMetricsGraph] = {}
        self._create_ui()

    def _create_ui(self):
        """Create the multi-graph panel"""
        # Header
        header = Gtk.Label()
        header.set_markup("<big><b>Historical Metrics (Last 5 Minutes)</b></big>")
        header.set_halign(Gtk.Align.START)
        self.append(header)

        # Scrolled window for graphs
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)

        # Container for graphs
        self.graphs_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.graphs_box.set_margin_start(12)
        self.graphs_box.set_margin_end(12)

        scrolled.set_child(self.graphs_box)
        self.append(scrolled)

        # Create default graphs
        self._create_default_graphs()

    def _create_default_graphs(self):
        """Create default metric graphs"""
        # CPU Usage
        self.add_graph('cpu_usage', 'CPU Usage', 'CPU', '%', '#e01b24')

        # CPU Temperature
        self.add_graph('cpu_temp', 'CPU Temperature', 'Temperature', '°C', '#f66151')

        # GPU Usage
        self.add_graph('gpu_usage', 'GPU Usage', 'GPU', '%', '#3584e4')

        # GPU Temperature
        self.add_graph('gpu_temp', 'GPU Temperature', 'Temperature', '°C', '#62a0ea')

        # RAM Usage
        self.add_graph('ram_usage', 'RAM Usage', 'Memory', '%', '#33d17a')

        # VRAM Usage
        self.add_graph('vram_usage', 'VRAM Usage', 'Video Memory', '%', '#26a269')

    def add_graph(self, graph_id: str, title: str, metric_name: str,
                  unit: str = "", color: str = "#3584e4"):
        """Add a new graph to the panel"""
        graph = HistoricalMetricsGraph(title, metric_name, unit, color)
        self.graphs[graph_id] = graph
        self.graphs_box.append(graph)

    def update_metric(self, graph_id: str, value: float):
        """Update a specific metric graph"""
        if graph_id in self.graphs:
            self.graphs[graph_id].add_data_point(value)

    def update_metrics_from_dict(self, metrics: Dict[str, float]):
        """Update multiple metrics from a dictionary"""
        for metric_name, value in metrics.items():
            self.update_metric(metric_name, value)

    def clear_all(self):
        """Clear all graphs"""
        for graph in self.graphs.values():
            graph.clear()


class CompactMetricsGraph(Gtk.DrawingArea):
    """Compact sparkline-style graph for dashboard use"""

    def __init__(self, width: int = 200, height: int = 60):
        super().__init__()
        self.set_size_request(width, height)

        self.values: deque = deque(maxlen=60)  # Last 60 data points
        self.color = (0.2, 0.5, 0.8, 1.0)  # RGBA

        self.set_draw_func(self._draw_graph)

    def _draw_graph(self, area, cr, width, height):
        """Draw the sparkline graph"""
        if len(self.values) == 0:
            return

        # Background
        cr.set_source_rgb(0.1, 0.1, 0.1)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        # Calculate points
        points = list(self.values)
        if len(points) < 2:
            return

        max_val = max(points) if max(points) > 0 else 100
        x_step = width / (len(points) - 1)

        # Draw line
        cr.set_source_rgba(*self.color)
        cr.set_line_width(2)

        for i, value in enumerate(points):
            x = i * x_step
            y = height - (value / max_val * height * 0.9) - height * 0.05

            if i == 0:
                cr.move_to(x, y)
            else:
                cr.line_to(x, y)

        cr.stroke()

        # Fill area under curve
        cr.set_source_rgba(self.color[0], self.color[1], self.color[2], 0.3)
        for i, value in enumerate(points):
            x = i * x_step
            y = height - (value / max_val * height * 0.9) - height * 0.05
            if i == 0:
                cr.move_to(x, height)
                cr.line_to(x, y)
            else:
                cr.line_to(x, y)
        cr.line_to(x, height)
        cr.close_path()
        cr.fill()

    def add_value(self, value: float):
        """Add a new value to the graph"""
        self.values.append(value)
        self.queue_draw()  # Request redraw

    def set_color(self, r: float, g: float, b: float, a: float = 1.0):
        """Set graph color (RGBA, 0.0-1.0)"""
        self.color = (r, g, b, a)

    def clear(self):
        """Clear all values"""
        self.values.clear()
        self.queue_draw()
