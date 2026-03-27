from app import create_app
from app.extensions import db
from app.models import ExceptionType, Store, User

app = create_app()


with app.app_context():
    if Store.query.count() == 0:
        stores = [
            Store(code="S001", name="Downtown Store", location="New York"),
            Store(code="S002", name="Uptown Store", location="Chicago"),
        ]
        db.session.add_all(stores)
        db.session.flush()

        users = [
            User(username="store_mgr", password="password123", full_name="Store Manager", role="STORE_MANAGER", store_id=stores[0].id),
            User(username="regional_mgr", password="password123", full_name="Regional Manager", role="REGIONAL_MANAGER"),
            User(username="finance_user", password="password123", full_name="Finance Reviewer", role="FINANCE"),
            User(username="supply_user", password="password123", full_name="Supply Chain Reviewer", role="SUPPLY_CHAIN"),
            User(username="audit_user", password="password123", full_name="Audit Reviewer", role="AUDIT"),
        ]
        db.session.add_all(users)

        types = [
            ExceptionType(code="PRICING_OVERRIDE", name="Pricing Override", default_approval_chain="REGIONAL_MANAGER,FINANCE,AUDIT"),
            ExceptionType(code="INVENTORY_WRITEOFF", name="Inventory Write-Off", default_approval_chain="REGIONAL_MANAGER,SUPPLY_CHAIN,FINANCE,AUDIT"),
            ExceptionType(code="SUPPLIER_SHORT_DELIVERY", name="Supplier Short Delivery", default_approval_chain="REGIONAL_MANAGER,SUPPLY_CHAIN,FINANCE,AUDIT"),
            ExceptionType(code="CUSTOMER_COMPENSATION", name="Customer Compensation", default_approval_chain="REGIONAL_MANAGER,FINANCE,AUDIT"),
            ExceptionType(code="POLICY_DEVIATION", name="Policy Deviation", default_approval_chain="REGIONAL_MANAGER,AUDIT"),
        ]
        db.session.add_all(types)
        db.session.commit()

        print("Seed data inserted")
    else:
        print("Seed data already exists")
