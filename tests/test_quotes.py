import pytest
from app import create_app
from app.services.repair_service import create_repair_request
from app.services.quote_service import create_quote, respond_to_quote, record_payment

@pytest.fixture
def app_ctx():
    app = create_app()
    app.config["TESTING"] = True
    return app

def test_quote_creation_and_customer_approval(app_ctx):
    with app_ctx.app_context():
        repair = create_repair_request(
            customer_id="usr_customer_1",
            customer_name="Aarav Sharma",
            shop_id="shp_apex_101",
            item_name="E-Bike Lithium Battery",
            category="E-Bikes & Scooters",
            fault_description="BMS cut-off problem",
            delivery_type="Drop-off at Shop"
        )
        
        quote, msg = create_quote(
            repair_id=repair["id"],
            min_estimated_cost=2000,
            max_estimated_cost=3000,
            final_quoted_amount=2500,
            estimated_completion_time="3 Business Days",
            technician_notes="Replace faulty BMS balancing board"
        )
        assert quote is not None
        assert quote["status"] == "Pending Customer Approval"

        # Customer approves
        success, resp_msg = respond_to_quote(quote["id"], "usr_customer_1", "Approved")
        assert success is True

        # Process payment
        payment = record_payment(
            repair_id=repair["id"],
            quote_id=quote["id"],
            customer_id="usr_customer_1",
            shop_id="shp_apex_101",
            amount=2500,
            payment_method="UPI / Online Transfer"
        )
        assert payment["amount"] == 2500
        assert payment["status"] == "Completed"
