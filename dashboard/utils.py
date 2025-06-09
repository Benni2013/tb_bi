import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_performance_segments(df, rating_col='avg_rating', reviews_col='total_reviews'):
    """
    Create performance segments based on rating and review volume
    """
    df = df.copy()
    
    # Create rating segments
    df['rating_segment'] = pd.cut(
        df[rating_col], 
        bins=[0, 2, 3, 4, 5], 
        labels=['Low', 'Medium', 'Good', 'Excellent'],
        include_lowest=True
    )
    
    # Create review volume segments
    df['volume_segment'] = pd.qcut(
        df[reviews_col], 
        q=3, 
        labels=['Low Volume', 'Medium Volume', 'High Volume']
    )
    
    return df

def calculate_trend_direction(values):
    """
    Calculate trend direction (increasing, decreasing, stable)
    """
    if len(values) < 2:
        return "stable"
    
    # Calculate slope using linear regression
    x = np.arange(len(values))
    z = np.polyfit(x, values, 1)
    slope = z[0]
    
    if slope > 0.1:
        return "increasing"
    elif slope < -0.1:
        return "decreasing"
    else:
        return "stable"

def format_number(num):
    """
    Format numbers for display (e.g., 1000 -> 1K, 1000000 -> 1M)
    """
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return str(int(num))

def create_gauge_chart(value, title, min_val=0, max_val=5):
    """
    Create a gauge chart for ratings or scores
    """
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        delta = {'reference': (min_val + max_val) / 2},
        gauge = {
            'axis': {'range': [None, max_val]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 2], 'color': "lightgray"},
                {'range': [2, 3], 'color': "yellow"},
                {'range': [3, 4], 'color': "orange"},
                {'range': [4, 5], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 4.5
            }
        }
    ))
    
    return fig

def get_color_palette():
    """
    Return consistent color palette for charts
    """
    return {
        'primary': '#1f77b4',
        'secondary': '#ff7f0e',
        'success': '#2ca02c',
        'danger': '#d62728',
        'warning': '#ff7f0e',
        'info': '#17a2b8',
        'light': '#f8f9fa',
        'dark': '#343a40',
        'positive': '#2E8B57',
        'negative': '#DC143C',
        'neutral': '#4682B4'
    }

def create_comparison_chart(data, x_col, y_col, color_col=None, title="Comparison Chart"):
    """
    Create a comparison chart with optional color coding
    """
    if color_col:
        fig = px.bar(
            data, 
            x=x_col, 
            y=y_col, 
            color=color_col,
            title=title,
            color_continuous_scale='RdYlGn'
        )
    else:
        fig = px.bar(
            data, 
            x=x_col, 
            y=y_col, 
            title=title
        )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=400
    )
    
    return fig

def generate_insights(data, metric_col, group_col):
    """
    Generate automatic insights from data
    """
    insights = []
    
    # Basic statistics
    mean_val = data[metric_col].mean()
    median_val = data[metric_col].median()
    std_val = data[metric_col].std()
    
    # Top and bottom performers
    top_performer = data.loc[data[metric_col].idxmax(), group_col]
    bottom_performer = data.loc[data[metric_col].idxmin(), group_col]
    
    insights.append(f"Average {metric_col}: {mean_val:.2f}")
    insights.append(f"Best performer: {top_performer}")
    insights.append(f"Worst performer: {bottom_performer}")
    
    # Variability insight
    if std_val > mean_val * 0.3:
        insights.append("High variability in performance detected")
    else:
        insights.append("Performance is relatively consistent")
    
    return insights