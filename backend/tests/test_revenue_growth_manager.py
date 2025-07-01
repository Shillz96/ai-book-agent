"""
Tests for Revenue Growth Manager Service

This test file ensures the Revenue Growth Management functionality
is working properly and can operate with or without analytics services.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from app.services.revenue_growth_manager import RevenueGrowthManager, RevenueMetrics
from tests.mocks.mock_firebase import MockFirebaseService


class TestRevenueGrowthManager:
    """Test cases for Revenue Growth Manager."""
    
    @pytest.fixture
    def mock_firebase(self):
        """Create a mock Firebase service."""
        return MockFirebaseService()
    
    @pytest.fixture
    def mock_openai_key(self):
        """Mock OpenAI API key."""
        return "test-openai-key"
    
    @pytest.fixture
    def rgm_with_firebase(self, mock_openai_key, mock_firebase):
        """Create RGM instance with Firebase service."""
        with patch('openai.OpenAI'):
            return RevenueGrowthManager(
                mock_openai_key,
                mock_firebase,
                analytics_service=None,
                ads_service=None,
                performance_service=None
            )
    
    @pytest.fixture
    def rgm_without_firebase(self, mock_openai_key):
        """Create RGM instance without Firebase service."""
        with patch('openai.OpenAI'):
            return RevenueGrowthManager(
                mock_openai_key,
                firebase_service=None,
                analytics_service=None,
                ads_service=None,
                performance_service=None
            )
    
    def test_initialization_with_firebase(self, rgm_with_firebase):
        """Test RGM initialization with Firebase service."""
        assert rgm_with_firebase is not None
        assert rgm_with_firebase.firebase_service is not None
        assert rgm_with_firebase.analytics_service is None
        assert rgm_with_firebase.ads_service is None
        assert rgm_with_firebase.performance_service is None
        assert rgm_with_firebase.has_analytics is False
        assert rgm_with_firebase.has_ads is False
        assert rgm_with_firebase.has_performance is False
        assert rgm_with_firebase.min_growth_rate == 0.15
        assert rgm_with_firebase.churn_threshold == 0.05
    
    def test_initialization_without_firebase(self, rgm_without_firebase):
        """Test RGM initialization without Firebase service."""
        assert rgm_without_firebase is not None
        assert rgm_without_firebase.firebase_service is None
        assert rgm_without_firebase.analytics_service is None
        assert rgm_without_firebase.ads_service is None
        assert rgm_without_firebase.performance_service is None
        assert rgm_without_firebase.has_analytics is False
        assert rgm_without_firebase.has_ads is False
        assert rgm_without_firebase.has_performance is False
    
    def test_analyze_revenue_performance(self, rgm_with_firebase):
        """Test revenue performance analysis."""
        app_id = "test-app"
        user_id = "test-user"
        
        result = rgm_with_firebase.analyze_revenue_performance(app_id, user_id)
        
        assert result is not None
        assert 'current_metrics' in result
        assert 'growth_opportunities' in result
        assert 'ai_recommendations' in result
        assert 'growth_projections' in result
        assert 'next_actions' in result
        assert 'analysis_timestamp' in result
    
    def test_optimize_pricing_strategy(self, rgm_with_firebase):
        """Test pricing strategy optimization."""
        current_metrics = RevenueMetrics(
            monthly_sales=5000.0,
            growth_rate=0.12,
            customer_acquisition_cost=25.0,
            customer_lifetime_value=150.0,
            churn_rate=0.03,
            conversion_rate=0.025,
            average_order_value=24.99
        )
        market_data = {}
        
        with patch.object(rgm_with_firebase.client.chat.completions, 'create') as mock_create:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Test pricing recommendations"
            mock_create.return_value = mock_response
            
            result = rgm_with_firebase.optimize_pricing_strategy(current_metrics, market_data)
            
            assert result is not None
            assert 'pricing_analysis' in result
            assert 'ai_recommendations' in result
            assert 'implementation_priority' in result
            assert 'expected_impact' in result
    
    def test_predict_and_prevent_churn(self, rgm_with_firebase):
        """Test churn prediction and prevention."""
        app_id = "test-app"
        user_id = "test-user"
        
        with patch.object(rgm_with_firebase.client.chat.completions, 'create') as mock_create:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Test retention strategies"
            mock_create.return_value = mock_response
            
            result = rgm_with_firebase.predict_and_prevent_churn(app_id, user_id)
            
            assert result is not None
            assert 'churn_analysis' in result
            assert 'retention_strategies' in result
            assert 'automated_actions' in result
            assert 'prevention_score' in result
    
    def test_gather_performance_data_with_firebase(self, rgm_with_firebase):
        """Test performance data gathering with Firebase."""
        app_id = "test-app"
        user_id = "test-user"
        
        # Mock Firebase user settings
        mock_settings = {
            'estimatedMonthlySales': 6000.0,
            'bookPrice': 29.99
        }
        rgm_with_firebase.firebase_service.get_user_settings = Mock(return_value=mock_settings)
        rgm_with_firebase.firebase_service.get_user_posts = Mock(return_value=[
            {'id': '1', 'content': 'Test post 1'},
            {'id': '2', 'content': 'Test post 2'}
        ])
        
        result = rgm_with_firebase._gather_performance_data(app_id, user_id)
        
        assert result is not None
        assert 'revenue_data' in result
        assert result['revenue_data']['monthly_sales'] == 6000.0
        assert result['revenue_data']['average_order_value'] == 29.99
        assert 'content_metrics' in result
        assert result['content_metrics']['total_posts'] == 2
    
    def test_gather_performance_data_without_firebase(self, rgm_without_firebase):
        """Test performance data gathering without Firebase."""
        app_id = "test-app"
        user_id = "test-user"
        
        result = rgm_without_firebase._gather_performance_data(app_id, user_id)
        
        assert result is not None
        assert 'revenue_data' in result
        assert result['revenue_data']['monthly_sales'] == 5000.0  # Default value
        assert result['revenue_data']['average_order_value'] == 24.99  # Default value
    
    def test_calculate_revenue_metrics(self, rgm_with_firebase):
        """Test revenue metrics calculation."""
        performance_data = {
            'revenue_data': {
                'monthly_sales': 7000.0,
                'growth_rate': 0.15,
                'customer_acquisition_cost': 30.0,
                'customer_lifetime_value': 200.0,
                'churn_rate': 0.02,
                'conversion_rate': 0.035,
                'average_order_value': 35.00
            }
        }
        
        metrics = rgm_with_firebase._calculate_revenue_metrics(performance_data)
        
        assert isinstance(metrics, RevenueMetrics)
        assert metrics.monthly_sales == 7000.0
        assert metrics.growth_rate == 0.15
        assert metrics.customer_acquisition_cost == 30.0
        assert metrics.customer_lifetime_value == 200.0
        assert metrics.churn_rate == 0.02
        assert metrics.conversion_rate == 0.035
        assert metrics.average_order_value == 35.00
    
    def test_identify_growth_opportunities(self, rgm_with_firebase):
        """Test growth opportunity identification."""
        # Test with low growth rate
        low_growth_metrics = RevenueMetrics(
            monthly_sales=5000.0,
            growth_rate=0.05,  # Below threshold
            customer_acquisition_cost=25.0,
            customer_lifetime_value=150.0,
            churn_rate=0.02,
            conversion_rate=0.025,
            average_order_value=24.99
        )
        
        opportunities = rgm_with_firebase._identify_growth_opportunities(low_growth_metrics, {})
        
        assert len(opportunities) > 0
        assert any(opp['type'] == 'growth_acceleration' for opp in opportunities)
        assert any(opp['priority'] == 'high' for opp in opportunities)
    
    def test_generate_growth_recommendations(self, rgm_with_firebase):
        """Test growth recommendation generation."""
        opportunities = [
            {
                'type': 'growth_acceleration',
                'priority': 'high',
                'description': 'Monthly growth rate below target',
                'potential_impact': 'high'
            },
            {
                'type': 'conversion_optimization',
                'priority': 'medium',
                'description': 'Conversion rate below optimal threshold',
                'potential_impact': 'medium'
            }
        ]
        
        recommendations = rgm_with_firebase._generate_growth_recommendations(
            RevenueMetrics(5000.0, 0.10, 25.0, 150.0, 0.03, 0.025, 24.99),
            opportunities
        )
        
        assert len(recommendations) == 2
        assert recommendations[0]['category'] == 'Marketing Optimization'
        assert recommendations[1]['category'] == 'Landing Page Optimization'
    
    def test_calculate_growth_projections(self, rgm_with_firebase):
        """Test growth projection calculations."""
        metrics = RevenueMetrics(
            monthly_sales=5000.0,
            growth_rate=0.12,
            customer_acquisition_cost=25.0,
            customer_lifetime_value=150.0,
            churn_rate=0.03,
            conversion_rate=0.025,
            average_order_value=24.99
        )
        recommendations = []
        
        projections = rgm_with_firebase._calculate_growth_projections(metrics, recommendations)
        
        assert 'current_monthly_sales' in projections
        assert 'projected_monthly_sales_30_days' in projections
        assert 'projected_monthly_sales_90_days' in projections
        assert 'estimated_annual_growth' in projections
        assert 'confidence_level' in projections
        assert projections['current_monthly_sales'] == 5000.0
        assert projections['projected_monthly_sales_30_days'] > 5000.0
    
    def test_error_handling(self, rgm_with_firebase):
        """Test error handling in various methods."""
        # Test with invalid app_id and user_id
        result = rgm_with_firebase.analyze_revenue_performance("invalid", "invalid")
        
        # Should return error or handle gracefully
        assert result is not None
        # The method should either return an error dict or valid default data
        assert isinstance(result, dict)
    
    def test_pricing_analysis(self, rgm_with_firebase):
        """Test pricing effectiveness analysis."""
        current_metrics = RevenueMetrics(
            monthly_sales=5000.0,
            growth_rate=0.12,
            customer_acquisition_cost=25.0,
            customer_lifetime_value=150.0,
            churn_rate=0.03,
            conversion_rate=0.025,
            average_order_value=24.99
        )
        market_data = {}
        
        analysis = rgm_with_firebase._analyze_pricing_effectiveness(current_metrics, market_data)
        
        assert 'effectiveness_score' in analysis
        assert 'price_sensitivity' in analysis
        assert 'market_position' in analysis
        assert 'optimization_potential' in analysis
        assert 0 <= analysis['effectiveness_score'] <= 1
    
    def test_churn_pattern_analysis(self, rgm_with_firebase):
        """Test churn pattern analysis."""
        engagement_data = {
            'user_activity': {
                'last_login': datetime.now().isoformat(),
                'settings_updates': 1,
                'content_generation_frequency': 'weekly'
            },
            'content_interaction': {
                'recent_posts': 5,
                'average_engagement': 0.03,
                'trending_content': []
            }
        }
        
        churn_analysis = rgm_with_firebase._analyze_churn_patterns(engagement_data)
        
        assert 'churn_risk_level' in churn_analysis
        assert 'risk_score' in churn_analysis
        assert 'warning_signals' in churn_analysis
        assert 'engagement_trend' in churn_analysis


if __name__ == "__main__":
    pytest.main([__file__]) 