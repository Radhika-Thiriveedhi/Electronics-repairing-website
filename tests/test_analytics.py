import pytest
from app import create_app
from app.services.analytics_service import get_platform_analytics, get_shop_analytics

@pytest.fixture
def app_ctx():
    app = create_app()
    app.config["TESTING"] = True
    return app

def test_platform_analytics(app_ctx):
    with app_ctx.app_context():
        analytics = get_platform_analytics()
        assert "total_jobs" in analytics
        assert "total_sales" in analytics
        assert "chart_labels" in analytics
        assert analytics["active_shops_count"] > 0

def test_shop_analytics(app_ctx):
    with app_ctx.app_context():
        shop_stats = get_shop_analytics("shp_apex_101")
        assert "total_jobs" in shop_stats
        assert "total_revenue" in shop_stats
