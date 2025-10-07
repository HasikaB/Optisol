import base64
import logging

class ChartGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_charts(self, data_points):
        """Generate charts from data points"""
        charts = []
        
        if not data_points or len(data_points) < 2:
            self.logger.warning("Not enough data points for charts")
            return charts
        
        try:
            # Lazy import plotly to avoid heavy initialization at module import time
            import plotly.graph_objects as go  # noqa: F401
            # Generate bar chart
            bar_chart = self._create_bar_chart(data_points)
            if bar_chart:
                charts.append(bar_chart)
            
            # Generate pie chart if data is suitable
            if len(data_points) <= 6:
                pie_chart = self._create_pie_chart(data_points)
                if pie_chart:
                    charts.append(pie_chart)
        
        except Exception as e:
            self.logger.error(f"Chart generation error: {e}")
        
        return charts
    
    def _create_bar_chart(self, data_points):
        """Create bar chart"""
        try:
            import plotly.graph_objects as go
            labels = [dp['label'] for dp in data_points]
            values = [dp['value'] for dp in data_points]
            
            fig = go.Figure(data=[
                go.Bar(x=labels, y=values, marker_color='#3b82f6')
            ])
            
            fig.update_layout(
                title="Data Overview",
                xaxis_title="Categories",
                yaxis_title="Values",
                template="plotly_white",
                height=400,
                showlegend=False
            )
            
            # Prefer kaleido; some environments need explicit engine
            img_bytes = fig.to_image(format="png", engine="kaleido")
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return {
                'type': 'bar',
                'image': img_base64,
                'title': 'Data Overview'
            }
        except Exception as e:
            self.logger.error(f"Bar chart error: {e}")
            return None
    
    def _create_pie_chart(self, data_points):
        """Create pie chart"""
        try:
            import plotly.graph_objects as go
            labels = [dp['label'] for dp in data_points]
            values = [dp['value'] for dp in data_points]
            
            fig = go.Figure(data=[
                go.Pie(labels=labels, values=values)
            ])
            
            fig.update_layout(
                title="Distribution Analysis",
                template="plotly_white",
                height=400
            )
            
            img_bytes = fig.to_image(format="png", engine="kaleido")
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return {
                'type': 'pie',
                'image': img_base64,
                'title': 'Distribution Analysis'
            }
        except Exception as e:
            self.logger.error(f"Pie chart error: {e}")
            return None