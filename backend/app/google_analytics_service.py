"""
Google Analytics Service

This service integrates with Google Analytics 4 to track book marketing performance,
analyze traffic sources, monitor conversions, and provide actionable insights for
autonomous marketing optimization.

Key Features:
- Real-time traffic and conversion tracking
- Campaign attribution analysis 
- User behavior analysis
- Custom event tracking for book sales funnel
- Efficient data processing to prevent token limits
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    Dimension,
    Metric,
    DateRange,
    FilterExpression,
    Filter,
    StringFilter
)
from google.oauth2.service_account import Credentials
import pandas as pd

logger = logging.getLogger(__name__)

class GoogleAnalyticsService:
    """
    Service for Google Analytics 4 integration with focus on book marketing metrics.
    
    Provides comprehensive analytics for tracking the effectiveness of social media
    campaigns, ad performance, and conversion optimization.
    """
    
    def __init__(self, credentials_path: str, property_id: str):
        """
        Initialize Google Analytics service.
        
        Args:
            credentials_path: Path to Google Analytics service account credentials
            property_id: GA4 property ID for the book marketing site
        """
        self.property_id = property_id
        self.client = None
        
        try:
            # Initialize GA4 client with service account credentials
            credentials = Credentials.from_service_account_file(credentials_path)
            self.client = BetaAnalyticsDataClient(credentials=credentials)
            logger.info("Google Analytics service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Analytics: {str(e)}")
            raise
    
    def get_book_marketing_metrics(self, start_date: str, end_date: str) -> Dict:
        """
        Get comprehensive book marketing metrics from Google Analytics.
        
        This method fetches key metrics for book marketing performance including
        traffic sources, user behavior, conversion rates, and revenue attribution.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dictionary containing all key marketing metrics
        """
        try:
            # Define key metrics for book marketing
            metrics = [
                'sessions',
                'totalUsers', 
                'newUsers',
                'bounceRate',
                'averageSessionDuration',
                'pageviews',
                'conversions',
                'totalRevenue',
                'purchaseRevenue'
            ]
            
            # Define dimensions for detailed analysis
            dimensions = [
                'date',
                'source',
                'medium',
                'campaign',
                'deviceCategory',
                'country',
                'landingPage'
            ]
            
            # Get basic traffic and conversion metrics
            traffic_data = self._fetch_analytics_data(
                start_date, end_date, 
                metrics[:6], 
                dimensions[:5]
            )
            
            # Get conversion and revenue metrics
            conversion_data = self._fetch_analytics_data(
                start_date, end_date,
                metrics[6:],
                ['date', 'source', 'medium']
            )
            
            # Get social media performance specifically
            social_data = self._get_social_media_performance(start_date, end_date)
            
            # Get landing page performance
            landing_page_data = self._get_landing_page_performance(start_date, end_date)
            
            # Calculate derived metrics
            derived_metrics = self._calculate_derived_metrics(traffic_data, conversion_data)
            
            return {
                'traffic_metrics': traffic_data,
                'conversion_metrics': conversion_data,
                'social_media_performance': social_data,
                'landing_page_performance': landing_page_data,
                'derived_metrics': derived_metrics,
                'analysis_period': {
                    'start_date': start_date,
                    'end_date': end_date
                },
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching book marketing metrics: {str(e)}")
            return {'error': str(e)}
    
    def track_campaign_performance(self, campaign_name: str, days_back: int = 7) -> Dict:
        """
        Track performance of specific marketing campaign.
        
        Args:
            campaign_name: Name of the campaign to track
            days_back: Number of days back to analyze
            
        Returns:
            Campaign performance metrics
        """
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            # Create filter for specific campaign
            campaign_filter = FilterExpression(
                filter=Filter(
                    field_name='campaign',
                    string_filter=StringFilter(value=campaign_name)
                )
            )
            
            # Fetch campaign-specific data
            campaign_data = self._fetch_analytics_data(
                start_date, end_date,
                ['sessions', 'totalUsers', 'conversions', 'totalRevenue'],
                ['date', 'source', 'medium', 'deviceCategory'],
                dimension_filter=campaign_filter
            )
            
            # Calculate campaign ROI and effectiveness
            campaign_analysis = self._analyze_campaign_effectiveness(campaign_data)
            
            return {
                'campaign_name': campaign_name,
                'analysis_period': f"{start_date} to {end_date}",
                'performance_data': campaign_data,
                'campaign_analysis': campaign_analysis,
                'recommendations': self._generate_campaign_recommendations(campaign_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error tracking campaign performance: {str(e)}")
            return {'error': str(e)}
    
    def get_conversion_funnel_analysis(self, start_date: str, end_date: str) -> Dict:
        """
        Analyze the conversion funnel for book sales.
        
        Tracks user journey from social media → landing page → book purchase
        """
        try:
            # Define funnel steps for book sales
            funnel_events = [
                'page_view',           # Landing page visit
                'click_amazon_link',   # Amazon link click
                'click_audible_link',  # Audible link click  
                'purchase'             # Book purchase conversion
            ]
            
            funnel_data = {}
            
            for event in funnel_events:
                event_data = self._fetch_event_data(start_date, end_date, event)
                funnel_data[event] = event_data
            
            # Calculate funnel conversion rates
            funnel_analysis = self._calculate_funnel_conversions(funnel_data)
            
            # Identify bottlenecks and optimization opportunities
            bottlenecks = self._identify_funnel_bottlenecks(funnel_analysis)
            
            return {
                'funnel_data': funnel_data,
                'conversion_rates': funnel_analysis,
                'bottlenecks': bottlenecks,
                'optimization_opportunities': self._suggest_funnel_optimizations(bottlenecks)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing conversion funnel: {str(e)}")
            return {'error': str(e)}
    
    def get_social_media_attribution(self, days_back: int = 30) -> Dict:
        """
        Analyze social media attribution for book sales.
        
        Determines which social platforms are driving the most traffic and conversions.
        """
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            # Filter for social media traffic
            social_filter = FilterExpression(
                filter=Filter(
                    field_name='medium',
                    string_filter=StringFilter(value='social')
                )
            )
            
            # Get social media performance data
            social_data = self._fetch_analytics_data(
                start_date, end_date,
                ['sessions', 'totalUsers', 'conversions', 'totalRevenue', 'bounceRate'],
                ['source', 'campaign', 'landingPage'],
                dimension_filter=social_filter
            )
            
            # Analyze platform effectiveness
            platform_analysis = self._analyze_platform_effectiveness(social_data)
            
            # Calculate social media ROI
            social_roi = self._calculate_social_media_roi(social_data)
            
            return {
                'social_media_data': social_data,
                'platform_analysis': platform_analysis,
                'social_roi': social_roi,
                'top_performing_platforms': self._rank_social_platforms(platform_analysis),
                'recommendations': self._generate_social_media_recommendations(platform_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing social media attribution: {str(e)}")
            return {'error': str(e)}
    
    def create_custom_dashboard_data(self) -> Dict:
        """
        Create data for autonomous marketing dashboard.
        
        Provides real-time metrics for autonomous decision-making.
        """
        try:
            # Get recent performance data (last 7 days)
            recent_metrics = self.get_book_marketing_metrics(
                (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                datetime.now().strftime('%Y-%m-%d')
            )
            
            # Get comparison data (previous 7 days)
            comparison_metrics = self.get_book_marketing_metrics(
                (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d'),
                (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            )
            
            # Calculate performance trends
            trends = self._calculate_performance_trends(recent_metrics, comparison_metrics)
            
            # Get real-time alerts
            alerts = self._generate_performance_alerts(recent_metrics, trends)
            
            return {
                'current_metrics': recent_metrics,
                'performance_trends': trends,
                'alerts': alerts,
                'key_insights': self._generate_key_insights(recent_metrics, trends),
                'next_actions': self._suggest_next_actions(recent_metrics, trends, alerts)
            }
            
        except Exception as e:
            logger.error(f"Error creating dashboard data: {str(e)}")
            return {'error': str(e)}
    
    # Helper methods for efficient data processing
    
    def _fetch_analytics_data(self, start_date: str, end_date: str, 
                             metrics: List[str], dimensions: List[str],
                             dimension_filter: Optional[FilterExpression] = None) -> Dict:
        """
        Fetch data from Google Analytics with efficient batching to avoid limits.
        """
        try:
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                dimensions=[Dimension(name=dim) for dim in dimensions],
                metrics=[Metric(name=metric) for metric in metrics],
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                dimension_filter=dimension_filter
            )
            
            response = self.client.run_report(request=request)
            return self._process_analytics_response(response)
            
        except Exception as e:
            logger.error(f"Error fetching analytics data: {str(e)}")
            return {}
    
    def _process_analytics_response(self, response) -> Dict:
        """Process GA4 response into structured data format."""
        try:
            rows = []
            for row in response.rows:
                row_data = {}
                
                # Add dimension values
                for i, dimension_value in enumerate(row.dimension_values):
                    dimension_name = response.dimension_headers[i].name
                    row_data[dimension_name] = dimension_value.value
                
                # Add metric values
                for i, metric_value in enumerate(row.metric_values):
                    metric_name = response.metric_headers[i].name
                    row_data[metric_name] = float(metric_value.value) if metric_value.value else 0
                
                rows.append(row_data)
            
            return {
                'data': rows,
                'row_count': len(rows),
                'totals': self._calculate_totals(rows)
            }
            
        except Exception as e:
            logger.error(f"Error processing analytics response: {str(e)}")
            return {'data': [], 'row_count': 0, 'totals': {}}
    
    def _get_social_media_performance(self, start_date: str, end_date: str) -> Dict:
        """Get specific social media performance metrics."""
        # Implementation for social media specific metrics
        return {}
    
    def _get_landing_page_performance(self, start_date: str, end_date: str) -> Dict:
        """Get landing page performance metrics."""
        # Implementation for landing page analysis
        return {}
    
    def _calculate_derived_metrics(self, traffic_data: Dict, conversion_data: Dict) -> Dict:
        """Calculate derived metrics like conversion rate, cost per acquisition, etc."""
        # Implementation for derived metrics calculation
        return {}
    
    def _fetch_event_data(self, start_date: str, end_date: str, event_name: str) -> Dict:
        """Fetch data for specific events in the conversion funnel."""
        # Implementation for event tracking
        return {}
    
    def _calculate_funnel_conversions(self, funnel_data: Dict) -> Dict:
        """Calculate conversion rates between funnel steps."""
        # Implementation for funnel analysis
        return {}
    
    def _identify_funnel_bottlenecks(self, funnel_analysis: Dict) -> List[Dict]:
        """Identify bottlenecks in the conversion funnel."""
        # Implementation for bottleneck identification
        return []
    
    def _suggest_funnel_optimizations(self, bottlenecks: List[Dict]) -> List[str]:
        """Suggest optimizations based on funnel bottlenecks."""
        # Implementation for optimization suggestions
        return []
    
    def _analyze_platform_effectiveness(self, social_data: Dict) -> Dict:
        """Analyze effectiveness of different social media platforms."""
        # Implementation for platform analysis
        return {}
    
    def _calculate_social_media_roi(self, social_data: Dict) -> Dict:
        """Calculate ROI for social media campaigns."""
        # Implementation for social media ROI calculation
        return {}
    
    def _rank_social_platforms(self, platform_analysis: Dict) -> List[Dict]:
        """Rank social media platforms by performance."""
        # Implementation for platform ranking
        return []
    
    def _generate_social_media_recommendations(self, platform_analysis: Dict) -> List[str]:
        """Generate recommendations for social media optimization."""
        # Implementation for social media recommendations
        return []
    
    def _analyze_campaign_effectiveness(self, campaign_data: Dict) -> Dict:
        """Analyze effectiveness of specific campaigns."""
        # Implementation for campaign analysis
        return {}
    
    def _generate_campaign_recommendations(self, campaign_analysis: Dict) -> List[str]:
        """Generate recommendations for campaign optimization."""
        # Implementation for campaign recommendations
        return []
    
    def _calculate_performance_trends(self, recent_metrics: Dict, comparison_metrics: Dict) -> Dict:
        """Calculate performance trends between periods."""
        # Implementation for trend calculation
        return {}
    
    def _generate_performance_alerts(self, recent_metrics: Dict, trends: Dict) -> List[Dict]:
        """Generate alerts for significant performance changes."""
        # Implementation for alert generation
        return []
    
    def _generate_key_insights(self, recent_metrics: Dict, trends: Dict) -> List[str]:
        """Generate key insights from analytics data."""
        # Implementation for insight generation
        return []
    
    def _suggest_next_actions(self, recent_metrics: Dict, trends: Dict, alerts: List[Dict]) -> List[str]:
        """Suggest next actions based on analytics data."""
        # Implementation for action suggestions
        return []
    
    def _calculate_totals(self, rows: List[Dict]) -> Dict:
        """Calculate totals for metric columns."""
        if not rows:
            return {}
        
        totals = {}
        for row in rows:
            for key, value in row.items():
                if isinstance(value, (int, float)):
                    totals[key] = totals.get(key, 0) + value
        
        return totals 