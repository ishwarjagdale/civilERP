import datetime

from flask import Blueprint, redirect, render_template, url_for, request
from flask_login import current_user, login_required
from database import Users, db, Contracts, ContractDetails, ClientDetails, Inventory, Tests

dash = Blueprint('dash', __name__, url_prefix="/dashboard")


@dash.route("/")
@login_required
def dashboard():
    return redirect(url_for('dash.overview'))


@dash.route("/overview")
@login_required
def overview():
    return render_template('views/dashboard/overview.html', title="Overview | C-Labs", tab="Overview",
                           user=current_user)


@dash.route("/new-contract", methods=["GET", "POST"])
@login_required
def new_contract():
    if not current_user.is_superuser:
        return redirect(url_for('dash.dashboard'))

    if request.method == "POST":
        """
        { 
            'client_name': 'Ishwar Jagdale', 
            'client_contact': '8999367986', 
            
            'received_address': 'N9 L29/3 CIDCO', 
            'delivers_name': 'Ishwar Jagdale', 
            'received_date': '2023-03-10T21:32', 
            'quantity_received': '1', 
            'sample_condition': 'Good', 
            'material_description': 'waifu', 
            'tests': 'Test 1', 
            'expected_report': '2023-03-10T21:32', 
            'assignees': '3ed6c6a5-39b7-48cb-a39f-559c9d4e60ac'
        }
        """
        payload = request.form.to_dict()
        contract = Contracts(assigned_to=payload['assignees'])
        db.session.add(contract)
        db.session.commit()

        client_details = ClientDetails(contract_id=contract.contract_id, name=payload['client_name'],
                                       contact=payload['client_contact'])
        db.session.add(client_details)

        contract_details = ContractDetails(contract_id=contract.contract_id, delivers_name=payload['delivers_name'],
                                           recv_date=payload['received_date'], quantity=payload['quantity_received'],
                                           condition=payload['sample_condition'],
                                           description=payload['material_description'],
                                           test_to_perform=payload['tests'])
        db.session.add(contract_details)
        db.session.commit()

        for i in range(contract_details.quantity):
            inv = Inventory(contract_id=contract.contract_id, sample_code=str(contract_details.recv_date) + f"-{i + 1}")
            db.session.add(inv)
        db.session.commit()

        return redirect(url_for('dash.inventory', contract_id=contract.contract_id))

    users = Users.query.filter_by(authenticated=True).all()
    ts = Tests.query.all()
    return render_template('views/dashboard/new-contract.html', title="New Contract | C-Labs", tab="New Contract",
                           user=current_user, testers=users, tests=ts)


@dash.route("/contracts")
@login_required
def contracts():
    cons = {"completed": [], "active": []}
    for contract in Contracts.query.all() if current_user.is_superuser else Contracts.query.filter_by(
            assigned_to=current_user.user_id):
        if current_user.is_superuser:
            contract.client = ClientDetails.query.filter(ClientDetails.contract_id == contract.contract_id).first()
            contract.tester = Users.get(contract.assigned_to)
        contract.details = ContractDetails.query.filter(ContractDetails.contract_id == contract.contract_id).first()
        contract.test = Tests.query.filter_by(test_id=contract.details.test_to_perform).first()
        if contract.completed:
            cons["completed"].append(contract)
        else:
            cons["active"].append(contract)

    return render_template('views/dashboard/contracts.html', title="Contracts | C-Labs", tab="Contracts",
                           user=current_user, contracts=cons)


@dash.route("/accounts", methods=["GET", "POST"])
@login_required
def accounts():
    if not current_user.is_superuser:
        return redirect(url_for('dash.dashboard'))

    if request.method == "POST":
        if "action" in request.form and "user_id" in request.form:
            user = Users.query.filter_by(user_id=request.form.get('user_id')).first()
            if user:
                if request.form.get('action') == "auth":
                    user.authenticated = True
                else:
                    db.session.delete(user)
                db.session.commit()

    users = {"authenticated": [], "pending": []}
    for user in Users.query.all():
        if user.is_authenticated:
            users["authenticated"].append(user)
        else:
            users["pending"].append(user)

    return render_template('views/dashboard/accounts.html', title="Accounts | C-Labs", tab="Accounts", users=users,
                           user=current_user)


@dash.route("/inventory/<contract_id>", methods=["GET", "POST"])
@login_required
def inventory(contract_id):
    if not current_user.is_superuser:
        return redirect(url_for('dash.dashboard'))

    if request.method == "POST":
        for i in request.form:
            item = Inventory.query.filter_by(item_id=i).first()
            if item:
                item.original_id_mark = request.form.get(i)
        db.session.commit()

    contract = Contracts.query.filter_by(contract_id=contract_id).first()
    if contract:
        contract.details = ContractDetails.query.filter_by(contract_id=contract.contract_id).first()
        contract.tester = Users.get(contract.assigned_to)
        contract.inventory = Inventory.query.filter_by(contract_id=contract_id).all()
        contract.test = Tests.query.filter_by(test_id=contract.details.test_to_perform).first()
        print(contract.inventory)
        return render_template('views/dashboard/inventory.html', title="Inventory | C-Labs", tab="Inventory",
                               contract=contract, user=current_user)


@dash.route("/tests", methods=["GET", "POST"])
@login_required
def tests():
    if request.method == "POST":
        test = Tests(test_name=request.form.get('test_name'))
        db.session.add(test)
        db.session.commit()

    ts = Tests.query.all()
    return render_template('views/dashboard/tests.html', title="Inventory | C-Labs", tab="Inventory",
                           user=current_user, tests=ts)
