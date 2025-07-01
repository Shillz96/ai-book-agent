"""
Budget Management Service

This service autonomously manages marketing budget allocation across platforms,
tracks spending in real-time, and optimizes budget distribution based on performance
to maximize ROI and prevent overspending.

Key Features:
- Real-time budget tracking and allocation
- Autonomous budget optimization based on performance
- Emergency spending controls and alerts
- Platform-specific budget management
- ROI-driven budget reallocation
- Monthly budget planning and forecasting
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class BudgetAlert:
    """Structure for budget alerts."""
    alert_type: str
    severity: str
    message: str
    current_spend: float
    budget_limit: float
    utilization_rate: float
    recommended_actions: List[str]
    timestamp: datetime

@dataclass
class BudgetAllocation:
    """Structure for budget allocations."""
    platform: str
    allocated_amount: float
    spent_amount: float
    remaining_amount: float
    utilization_rate: float
    performance_score: float
    roi: float

class BudgetManager:
    """
    Autonomous budget management service for book marketing campaigns.
    
    Manages budget allocation across social media platforms and Google Ads,
    tracks spending, and optimizes allocation based on performance metrics.
    """
    
    def __init__(self, firebase_service, analytics_service, ads_service):
        """
        Initialize budget manager.
        
        Args:
            firebase_service: Firebase service for data storage
            analytics_service: Google Analytics service
            ads_service: Google Ads service
        """
        self.firebase_service = firebase_service
        self.analytics_service = analytics_service
        self.ads_service = ads_service
        
        # Budget configuration from environment
        self.monthly_budget = float(os.getenv('MONTHLY_MARKETING_BUDGET', 500.0))
        self.daily_budget = self.monthly_budget / 30
        self.budget_alert_threshold = float(os.getenv('BUDGET_ALERT_THRESHOLD', 0.8))
        self.emergency_stop_threshold = float(os.getenv('EMERGENCY_STOP_THRESHOLD', 0.95))
        self.auto_reallocation_enabled = os.getenv('AUTO_BUDGET_REALLOCATION', 'true').lower() == 'true'
        
        # Platform budget allocations (percentages)
        self.default_allocations = {
            'google_ads': 0.60,      # 60% to Google Ads
            'facebook_ads': 0.25,    # 25% to Facebook/Instagram Ads  
            'twitter_ads': 0.10,     # 10% to Twitter Ads
            'pinterest_ads': 0.05    # 5% to Pinterest Ads
        }
        
        # Performance thresholds for budget decisions
        self.min_roas = float(os.getenv('TARGET_ROAS', 3.0))
        self.min_ctr = float(os.getenv('MIN_CTR', 0.01))
        self.min_conversion_rate = float(os.getenv('MIN_CONVERSION_RATE', 0.005))
        
        logger.info("Budget Manager initialized successfully")
    
    def get_current_budget_status(self) -> Dict:
        """
        Get current budget status across all platforms.
        
        Returns comprehensive budget information including spending,
        remaining budget, utilization rates, and performance metrics.
        """
        try:
            # Get current date for monthly calculation
            current_date = datetime.now()
            month_start = current_date.replace(day=1)
            days_in_month = (month_start.replace(month=month_start.month + 1) - timedelta(days=1)).day
            days_passed = current_date.day
            
            # Calculate expected vs actual spending
            expected_spend = (self.monthly_budget / days_in_month) * days_passed
            
            # Get actual spending by platform
            platform_spending = self._get_platform_spending()
            total_spent = sum(platform_spending.values())
            
            # Calculate utilization rates
            overall_utilization = total_spent / self.monthly_budget
            expected_utilization = expected_spend / self.monthly_budget
            
            # Generate budget allocations
            allocations = []
            for platform, spent in platform_spending.items():
                allocated = self.monthly_budget * self.default_allocations.get(platform, 0)
                utilization = (spent / allocated) if allocated > 0 else 0
                
                allocation = BudgetAllocation(
                    platform=platform,
                    allocated_amount=allocated,
                    spent_amount=spent,
                    remaining_amount=max(0, allocated - spent),
                    utilization_rate=utilization,
                    performance_score=self._get_platform_performance_score(platform),
                    roi=self._calculate_platform_roi(platform)
                )
                allocations.append(allocation)
            
            # Generate budget alerts if needed
            alerts = self._check_budget_alerts(overall_utilization, allocations)
            
            return {
                'monthly_budget': self.monthly_budget,
                'total_spent': total_spent,
                'remaining_budget': self.monthly_budget - total_spent,
                'overall_utilization': overall_utilization,
                'expected_utilization': expected_utilization,
                'variance_from_expected': overall_utilization - expected_utilization,
                'platform_allocations': [alloc.__dict__ for alloc in allocations],
                'budget_alerts': [alert.__dict__ for alert in alerts],
                'days_remaining_in_month': days_in_month - days_passed,
                'projected_monthly_spend': total_spent * (days_in_month / days_passed) if days_passed > 0 else 0,
                'budget_health_score': self._calculate_budget_health_score(overall_utilization, allocations),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting budget status: {str(e)}")
            return {'error': str(e)}
    
    def optimize_budget_allocation(self, performance_data: Dict) -> Dict:
        """
        Optimize budget allocation based on platform performance.
        
        Analyzes performance metrics and autonomously reallocates budget
        to maximize ROI and achieve better results.
        """
        try:
            # Get current allocations
            current_status = self.get_current_budget_status()
            current_allocations = current_status.get('platform_allocations', [])
            
            # Calculate performance-based optimal allocation
            platform_scores = {}
            for allocation in current_allocations:
                platform = allocation['platform']
                
                # Calculate composite performance score
                roi_score = min(allocation['roi'] / self.min_roas, 2.0)  # Cap at 2x target
                performance_score = allocation['performance_score']
                efficiency_score = self._calculate_platform_efficiency(platform, performance_data)
                
                # Weight the scores
                composite_score = (roi_score * 0.4) + (performance_score * 0.3) + (efficiency_score * 0.3)
                platform_scores[platform] = composite_score
            
            # Generate new allocation percentages
            total_score = sum(platform_scores.values())
            new_allocations = {}
            
            if total_score > 0:
                for platform, score in platform_scores.items():
                    # Base allocation on performance but maintain minimums
                    min_allocation = 0.05  # 5% minimum per platform
                    performance_allocation = (score / total_score) * 0.9  # 90% based on performance
                    new_allocations[platform] = min_allocation + performance_allocation
            else:
                # Fallback to default allocations if no performance data
                new_allocations = self.default_allocations.copy()
            
            # Normalize to ensure total = 1.0
            total_allocation = sum(new_allocations.values())
            if total_allocation != 1.0:
                for platform in new_allocations:
                    new_allocations[platform] = new_allocations[platform] / total_allocation
            
            # Calculate reallocation changes
            reallocation_changes = []
            total_reallocation = 0
            
            for platform, new_percentage in new_allocations.items():
                old_percentage = self.default_allocations.get(platform, 0)
                change = new_percentage - old_percentage
                new_amount = self.monthly_budget * new_percentage
                old_amount = self.monthly_budget * old_percentage
                
                if abs(change) > 0.02:  # Only report changes > 2%
                    reallocation_changes.append({
                        'platform': platform,
                        'old_percentage': old_percentage,
                        'new_percentage': new_percentage,
                        'old_amount': old_amount,
                        'new_amount': new_amount,
                        'change_amount': new_amount - old_amount,
                        'change_percentage': change,
                        'reason': self._get_reallocation_reason(platform, change, platform_scores.get(platform, 0))
                    })
                    total_reallocation += abs(new_amount - old_amount)
            
            # Apply reallocations if auto-reallocation is enabled
            applied_changes = []
            if self.auto_reallocation_enabled and reallocation_changes:
                for change in reallocation_changes:
                    result = self._apply_budget_reallocation(change)
                    applied_changes.append(result)
            
            optimization_result = {
                'optimization_timestamp': datetime.now().isoformat(),
                'current_allocations': {platform: self.default_allocations.get(platform, 0) for platform in platform_scores.keys()},
                'optimized_allocations': new_allocations,
                'platform_scores': platform_scores,
                'reallocation_changes': reallocation_changes,
                'total_reallocation_amount': total_reallocation,
                'applied_changes': applied_changes,
                'auto_reallocation_enabled': self.auto_reallocation_enabled,
                'expected_improvement': self._calculate_expected_improvement(new_allocations, platform_scores),
                'confidence_score': self._calculate_optimization_confidence(platform_scores, performance_data)
            }
            
            # Save optimization results
            self._save_budget_optimization(optimization_result)
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"Error optimizing budget allocation: {str(e)}")
            return {'error': str(e)}
    
    def handle_budget_emergency(self, alert: BudgetAlert) -> Dict:
        """
        Handle budget emergencies with immediate corrective actions.
        
        Takes immediate action when budget utilization exceeds emergency thresholds
        to prevent overspending and maintain campaign effectiveness.
        """
        try:
            emergency_actions = []
            
            if alert.severity == 'critical':
                # Critical emergency actions
                if alert.utilization_rate >= self.emergency_stop_threshold:
                    # Pause all campaigns immediately
                    pause_results = self._emergency_pause_campaigns()
                    emergency_actions.extend(pause_results)
                    
                    # Send immediate notification
                    notification_result = self._send_emergency_notification(alert)
                    emergency_actions.append(notification_result)
                
                elif alert.utilization_rate >= self.budget_alert_threshold:
                    # Reduce budgets by 50% for underperforming campaigns
                    reduction_results = self._reduce_underperforming_budgets()
                    emergency_actions.extend(reduction_results)
                    
                    # Pause lowest ROI campaigns
                    pause_results = self._pause_low_roi_campaigns()
                    emergency_actions.extend(pause_results)
            
            # Log emergency response
            emergency_response = {
                'alert': alert.__dict__,
                'emergency_actions': emergency_actions,
                'handled_at': datetime.now().isoformat(),
                'estimated_savings': self._calculate_emergency_savings(emergency_actions),
                'recovery_plan': self._generate_recovery_plan(alert, emergency_actions)
            }
            
            # Save emergency response
            self._save_emergency_response(emergency_response)
            
            return emergency_response
            
        except Exception as e:
            logger.error(f"Error handling budget emergency: {str(e)}")
            return {'error': str(e)}
    
    def forecast_monthly_performance(self) -> Dict:
        """
        Forecast monthly budget performance and ROI.
        
        Predicts end-of-month spending, ROI, and performance based on
        current trends and historical data.
        """
        try:
            current_date = datetime.now()
            days_passed = current_date.day
            days_in_month = (current_date.replace(month=current_date.month + 1) - timedelta(days=1)).day
            
            # Get current spending trends
            spending_data = self._get_daily_spending_trend()
            performance_data = self._get_daily_performance_trend()
            
            # Calculate spending trajectory
            if days_passed > 0:
                avg_daily_spend = sum(spending_data[-7:]) / min(7, len(spending_data))  # 7-day average
                projected_monthly_spend = avg_daily_spend * days_in_month
                projected_overspend = max(0, projected_monthly_spend - self.monthly_budget)
                
                # Calculate performance trajectory
                recent_roi = np.mean([p.get('roi', 0) for p in performance_data[-7:]])
                recent_conversion_rate = np.mean([p.get('conversion_rate', 0) for p in performance_data[-7:]])
                
                # Generate forecast scenarios
                scenarios = {
                    'conservative': self._generate_forecast_scenario('conservative', spending_data, performance_data),
                    'realistic': self._generate_forecast_scenario('realistic', spending_data, performance_data),
                    'optimistic': self._generate_forecast_scenario('optimistic', spending_data, performance_data)
                }
                
                # Calculate recommendations
                recommendations = self._generate_forecast_recommendations(
                    projected_monthly_spend, projected_overspend, recent_roi
                )
                
                return {
                    'forecast_date': current_date.isoformat(),
                    'days_passed': days_passed,
                    'days_remaining': days_in_month - days_passed,
                    'current_monthly_spend': sum(spending_data),
                    'projected_monthly_spend': projected_monthly_spend,
                    'monthly_budget': self.monthly_budget,
                    'projected_overspend': projected_overspend,
                    'budget_variance_percentage': (projected_overspend / self.monthly_budget) * 100,
                    'recent_roi': recent_roi,
                    'recent_conversion_rate': recent_conversion_rate,
                    'forecast_scenarios': scenarios,
                    'recommendations': recommendations,
                    'risk_level': self._calculate_budget_risk_level(projected_overspend, recent_roi),
                    'confidence_score': self._calculate_forecast_confidence(spending_data, performance_data)
                }
            else:
                return {
                    'forecast_date': current_date.isoformat(),
                    'message': 'Insufficient data for forecasting (start of month)',
                    'monthly_budget': self.monthly_budget
                }
                
        except Exception as e:
            logger.error(f"Error forecasting monthly performance: {str(e)}")
            return {'error': str(e)}
    
    # Helper methods for budget management
    
    def _get_platform_spending(self) -> Dict[str, float]:
        """Get current spending by platform."""
        # This would integrate with actual platform APIs to get real spending data
        # For now, returning mock data structure
        return {
            'google_ads': 180.50,
            'facebook_ads': 95.25,
            'twitter_ads': 25.75,
            'pinterest_ads': 8.50
        }
    
    def _get_platform_performance_score(self, platform: str) -> float:
        """Calculate performance score for a platform."""
        # This would calculate based on engagement, CTR, conversions, etc.
        platform_scores = {
            'google_ads': 0.78,
            'facebook_ads': 0.65,
            'twitter_ads': 0.55,
            'pinterest_ads': 0.42
        }
        return platform_scores.get(platform, 0.5)
    
    def _calculate_platform_roi(self, platform: str) -> float:
        """Calculate ROI for a specific platform."""
        # This would calculate based on revenue / spend
        platform_rois = {
            'google_ads': 4.2,
            'facebook_ads': 3.1,
            'twitter_ads': 2.8,
            'pinterest_ads': 1.9
        }
        return platform_rois.get(platform, 1.0)
    
    def _check_budget_alerts(self, utilization_rate: float, allocations: List[BudgetAllocation]) -> List[BudgetAlert]:
        """Check for budget alerts based on utilization and performance."""
        alerts = []
        
        # Overall budget alert
        if utilization_rate >= self.emergency_stop_threshold:
            alerts.append(BudgetAlert(
                alert_type='budget_exceeded',
                severity='critical',
                message=f'Monthly budget utilization at {utilization_rate:.1%} - Emergency threshold reached',
                current_spend=self.monthly_budget * utilization_rate,
                budget_limit=self.monthly_budget,
                utilization_rate=utilization_rate,
                recommended_actions=['Pause all campaigns', 'Review spending', 'Increase budget or wait for next month'],
                timestamp=datetime.now()
            ))
        elif utilization_rate >= self.budget_alert_threshold:
            alerts.append(BudgetAlert(
                alert_type='budget_warning',
                severity='high',
                message=f'Monthly budget utilization at {utilization_rate:.1%} - Approaching limit',
                current_spend=self.monthly_budget * utilization_rate,
                budget_limit=self.monthly_budget,
                utilization_rate=utilization_rate,
                recommended_actions=['Reduce budgets for low-performing campaigns', 'Optimize targeting'],
                timestamp=datetime.now()
            ))
        
        # Platform-specific alerts
        for allocation in allocations:
            if allocation.utilization_rate >= 0.9:
                alerts.append(BudgetAlert(
                    alert_type='platform_budget_exceeded',
                    severity='medium',
                    message=f'{allocation.platform} budget 90% utilized',
                    current_spend=allocation.spent_amount,
                    budget_limit=allocation.allocated_amount,
                    utilization_rate=allocation.utilization_rate,
                    recommended_actions=[f'Review {allocation.platform} campaigns', 'Consider reallocation'],
                    timestamp=datetime.now()
                ))
        
        return alerts
    
    def _calculate_budget_health_score(self, utilization_rate: float, allocations: List[BudgetAllocation]) -> float:
        """Calculate overall budget health score (0-1)."""
        # Base score on utilization rate
        utilization_score = 1.0 - min(utilization_rate, 1.0)
        
        # Factor in platform performance
        platform_scores = [alloc.performance_score for alloc in allocations]
        avg_performance = np.mean(platform_scores) if platform_scores else 0.5
        
        # Combine scores
        health_score = (utilization_score * 0.6) + (avg_performance * 0.4)
        return max(0.0, min(1.0, health_score))
    
    def _calculate_platform_efficiency(self, platform: str, performance_data: Dict) -> float:
        """Calculate efficiency score for a platform."""
        # This would analyze cost per acquisition, conversion rates, etc.
        return 0.7  # Placeholder
    
    def _get_reallocation_reason(self, platform: str, change: float, score: float) -> str:
        """Generate reason for budget reallocation."""
        if change > 0:
            return f"Increasing allocation due to strong performance (score: {score:.2f})"
        else:
            return f"Decreasing allocation due to underperformance (score: {score:.2f})"
    
    def _apply_budget_reallocation(self, change: Dict) -> Dict:
        """Apply budget reallocation change."""
        # This would actually update platform budgets
        return {
            'platform': change['platform'],
            'change_applied': True,
            'new_budget': change['new_amount'],
            'applied_at': datetime.now().isoformat()
        }
    
    def _calculate_expected_improvement(self, new_allocations: Dict, platform_scores: Dict) -> Dict:
        """Calculate expected improvement from reallocation."""
        # This would estimate ROI improvement based on allocation changes
        return {
            'roi_improvement': '15-25%',
            'efficiency_improvement': '10-20%'
        }
    
    def _calculate_optimization_confidence(self, platform_scores: Dict, performance_data: Dict) -> float:
        """Calculate confidence score for optimization."""
        # Based on data quality, historical performance, etc.
        return 0.82
    
    def _save_budget_optimization(self, optimization_result: Dict):
        """Save budget optimization results."""
        try:
            self.firebase_service.save_budget_optimization(optimization_result)
        except Exception as e:
            logger.error(f"Error saving budget optimization: {str(e)}")
    
    def _emergency_pause_campaigns(self) -> List[Dict]:
        """Pause all campaigns in emergency."""
        # This would pause campaigns across all platforms
        return [{'action': 'pause_all_campaigns', 'status': 'completed'}]
    
    def _send_emergency_notification(self, alert: BudgetAlert) -> Dict:
        """Send emergency notification."""
        # This would send email/SMS notifications
        return {'action': 'emergency_notification_sent', 'status': 'completed'}
    
    def _reduce_underperforming_budgets(self) -> List[Dict]:
        """Reduce budgets for underperforming campaigns."""
        # This would identify and reduce budgets
        return [{'action': 'reduce_budgets', 'campaigns_affected': 3}]
    
    def _pause_low_roi_campaigns(self) -> List[Dict]:
        """Pause campaigns with low ROI."""
        # This would pause specific low-performing campaigns
        return [{'action': 'pause_low_roi_campaigns', 'campaigns_paused': 2}]
    
    def _calculate_emergency_savings(self, actions: List[Dict]) -> float:
        """Calculate estimated savings from emergency actions."""
        return 45.0  # Placeholder
    
    def _generate_recovery_plan(self, alert: BudgetAlert, actions: List[Dict]) -> Dict:
        """Generate recovery plan after emergency."""
        return {
            'recovery_steps': ['Review campaign performance', 'Optimize targeting', 'Gradually resume spending'],
            'estimated_recovery_time': '3-5 days'
        }
    
    def _save_emergency_response(self, response: Dict):
        """Save emergency response data."""
        try:
            self.firebase_service.save_budget_emergency_response(response)
        except Exception as e:
            logger.error(f"Error saving emergency response: {str(e)}")
    
    def _get_daily_spending_trend(self) -> List[float]:
        """Get daily spending trend for the month."""
        # This would return actual daily spending data
        return [15.2, 18.5, 22.1, 19.8, 25.3, 28.7, 31.2]  # Placeholder
    
    def _get_daily_performance_trend(self) -> List[Dict]:
        """Get daily performance trend."""
        # This would return actual performance data
        return [
            {'roi': 3.2, 'conversion_rate': 0.008},
            {'roi': 3.5, 'conversion_rate': 0.009},
            {'roi': 2.9, 'conversion_rate': 0.007}
        ]  # Placeholder
    
    def _generate_forecast_scenario(self, scenario_type: str, spending_data: List[float], performance_data: List[Dict]) -> Dict:
        """Generate forecast scenario."""
        # This would calculate different scenarios based on trends
        scenarios = {
            'conservative': {'monthly_spend': 480, 'roi': 2.8, 'conversions': 45},
            'realistic': {'monthly_spend': 520, 'roi': 3.2, 'conversions': 52},
            'optimistic': {'monthly_spend': 450, 'roi': 3.8, 'conversions': 60}
        }
        return scenarios.get(scenario_type, scenarios['realistic'])
    
    def _generate_forecast_recommendations(self, projected_spend: float, overspend: float, roi: float) -> List[str]:
        """Generate forecast-based recommendations."""
        recommendations = []
        
        if overspend > 0:
            recommendations.append(f"Reduce spending by ${overspend:.2f} to stay within budget")
        
        if roi < self.min_roas:
            recommendations.append("Optimize campaigns to improve ROI")
        
        return recommendations
    
    def _calculate_budget_risk_level(self, overspend: float, roi: float) -> str:
        """Calculate budget risk level."""
        if overspend > self.monthly_budget * 0.2:
            return 'high'
        elif overspend > self.monthly_budget * 0.1:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_forecast_confidence(self, spending_data: List[float], performance_data: List[Dict]) -> float:
        """Calculate forecast confidence based on data quality."""
        # Based on data consistency, sample size, etc.
        return 0.75

    def calculate_efficiency_score(self, campaign_data: Dict) -> float:
        """
        Calculate real efficiency score based on actual campaign performance data.
        
        Args:
            campaign_data: Real campaign performance data from advertising platforms
            
        Returns:
            Efficiency score between 0 and 1
        """
        try:
            # Extract key performance metrics
            cost = campaign_data.get('cost', 0)
            conversions = campaign_data.get('conversions', 0)
            revenue = campaign_data.get('revenue', 0)
            clicks = campaign_data.get('clicks', 0)
            impressions = campaign_data.get('impressions', 0)
            
            # Calculate component scores
            roi_score = self._calculate_roi_score(cost, revenue)
            conversion_score = self._calculate_conversion_score(clicks, conversions)
            cost_efficiency_score = self._calculate_cost_efficiency_score(campaign_data)
            reach_score = self._calculate_reach_score(impressions, campaign_data.get('target_audience_size', 1))
            
            # Weight the scores based on business importance
            weights = {
                'roi': 0.4,           # ROI is most important
                'conversion': 0.3,    # Conversion rate is critical
                'cost_efficiency': 0.2, # Cost control matters
                'reach': 0.1          # Reach is supporting metric
            }
            
            efficiency_score = (
                roi_score * weights['roi'] +
                conversion_score * weights['conversion'] +
                cost_efficiency_score * weights['cost_efficiency'] +
                reach_score * weights['reach']
            )
            
            return min(max(efficiency_score, 0.0), 1.0)  # Clamp between 0 and 1
            
        except Exception as e:
            logger.error(f"Error calculating efficiency score: {str(e)}")
            return 0.0

    def predict_spend_forecast(self, historical_data: List[Dict], days_ahead: int = 30) -> float:
        """
        Predict future spend based on real historical spending patterns.
        
        Args:
            historical_data: List of historical spending data points
            days_ahead: Number of days to forecast ahead
            
        Returns:
            Predicted spend amount
        """
        try:
            if not historical_data or len(historical_data) < 7:
                logger.warning("Insufficient historical data for forecast")
                return 0.0
            
            # Extract spending values and dates
            spends = [data.get('spend', 0) for data in historical_data]
            dates = [datetime.fromisoformat(data.get('date')) for data in historical_data if data.get('date')]
            
            # Calculate trending patterns
            recent_spends = spends[-7:]  # Last 7 days
            avg_recent_spend = sum(recent_spends) / len(recent_spends)
            
            # Calculate growth rate
            if len(spends) >= 14:
                older_period = spends[-14:-7]  # Previous 7 days
                avg_older_spend = sum(older_period) / len(older_period)
                growth_rate = (avg_recent_spend - avg_older_spend) / avg_older_spend if avg_older_spend > 0 else 0
            else:
                growth_rate = 0
            
            # Account for seasonality (day of week patterns)
            weekday_patterns = self._analyze_weekday_spending_patterns(historical_data)
            
            # Forecast future spend
            base_daily_spend = avg_recent_spend
            projected_spend = 0
            
            for day in range(days_ahead):
                future_date = datetime.now() + timedelta(days=day)
                weekday = future_date.weekday()
                
                # Apply weekday adjustment
                weekday_multiplier = weekday_patterns.get(weekday, 1.0)
                
                # Apply growth trend
                trend_multiplier = 1 + (growth_rate * (day / 30))  # Gradual application of growth
                
                daily_forecast = base_daily_spend * weekday_multiplier * trend_multiplier
                projected_spend += daily_forecast
            
            return round(projected_spend, 2)
            
        except Exception as e:
            logger.error(f"Error predicting spend forecast: {str(e)}")
            return 0.0

    def get_budget_trends(self, time_period: int = 30) -> List[float]:
        """
        Get real budget utilization trends from actual spending data.
        
        Args:
            time_period: Number of days to analyze
            
        Returns:
            List of budget utilization percentages over time
        """
        try:
            # Get actual spending data from integrated platforms
            spending_data = self._get_historical_spending_data(time_period)
            budget_data = self._get_budget_allocation_data(time_period)
            
            trends = []
            for i, spend_entry in enumerate(spending_data):
                spend_amount = spend_entry.get('total_spend', 0)
                budget_amount = budget_data[i].get('allocated_budget', 0) if i < len(budget_data) else 0
                
                utilization_percentage = (spend_amount / budget_amount * 100) if budget_amount > 0 else 0
                trends.append(round(utilization_percentage, 1))
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting budget trends: {str(e)}")
            return []

    def generate_budget_recommendations(self, performance_data: Dict) -> List[Dict]:
        """
        Generate real budget recommendations based on actual performance data.
        
        Args:
            performance_data: Real performance metrics from campaigns
            
        Returns:
            List of actionable budget recommendations
        """
        try:
            recommendations = []
            
            # Analyze ROI performance by channel
            channel_roi = performance_data.get('channel_roi', {})
            total_budget = performance_data.get('total_budget', 0)
            
            # Identify high-performing channels
            high_performers = [
                channel for channel, data in channel_roi.items()
                if data.get('roi_percentage', 0) > 20  # 20% ROI threshold
            ]
            
            # Identify underperforming channels
            underperformers = [
                channel for channel, data in channel_roi.items()
                if data.get('roi_percentage', 0) < 5  # 5% ROI threshold
            ]
            
            # Generate specific recommendations
            if high_performers:
                total_high_performer_budget = sum(
                    channel_roi[channel].get('current_budget', 0) for channel in high_performers
                )
                recommendations.append({
                    'type': 'budget_increase',
                    'priority': 'high',
                    'channels': high_performers,
                    'current_budget': total_high_performer_budget,
                    'recommended_increase': round(total_high_performer_budget * 0.25, 2),
                    'expected_roi_increase': '15-25%',
                    'reasoning': f'Increase budget for high-performing channels: {", ".join(high_performers)}'
                })
            
            if underperformers:
                total_underperformer_budget = sum(
                    channel_roi[channel].get('current_budget', 0) for channel in underperformers
                )
                recommendations.append({
                    'type': 'budget_reallocation',
                    'priority': 'medium',
                    'channels': underperformers,
                    'current_budget': total_underperformer_budget,
                    'recommended_reduction': round(total_underperformer_budget * 0.4, 2),
                    'reallocation_target': high_performers[0] if high_performers else 'content_creation',
                    'reasoning': f'Reallocate budget from underperforming channels: {", ".join(underperformers)}'
                })
            
            # Analyze spending velocity
            spending_velocity = performance_data.get('spending_velocity', 0)
            if spending_velocity > 1.2:  # Spending 20% faster than planned
                recommendations.append({
                    'type': 'pace_adjustment',
                    'priority': 'high',
                    'current_pace': f'{spending_velocity:.1%} of planned',
                    'recommended_action': 'reduce_daily_budgets',
                    'adjustment_percentage': -15,
                    'reasoning': 'Current spending pace is too aggressive; risk of budget exhaustion'
                })
            elif spending_velocity < 0.8:  # Spending 20% slower than planned
                recommendations.append({
                    'type': 'pace_adjustment',
                    'priority': 'medium',
                    'current_pace': f'{spending_velocity:.1%} of planned',
                    'recommended_action': 'increase_daily_budgets',
                    'adjustment_percentage': 10,
                    'reasoning': 'Current spending pace is too conservative; missing growth opportunities'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating budget recommendations: {str(e)}")
            return [] 