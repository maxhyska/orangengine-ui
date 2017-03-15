
import logging
import subprocess
from flask import jsonify, request, abort
from api import app, db
from api.auth import auth_token_required
from api.models import ChangeRequest, Device, Address, Service

# Setup
logger = logging.getLogger(__name__)

def data_results(data):
    # wrap the data in a standard response and jsonify it
    if isinstance(data, basestring):
        data = {'message': data}
    return jsonify({"data": data}, )

# Info method, Return Request Data back to client as JSON
@app.route('/v1.0/info', methods=['POST', 'GET'])
@auth_token_required
def app_getinfo():
    """ Returns Flask API Info """
    response = dict()
    response['message'] = "Flask API Data"
    response['status'] = "200"
    response['method'] = request.method
    response['path'] = request.path
    response['remote_addr'] = request.remote_addr
    response['user_agent'] = request.headers.get('User-Agent')

    # GET attributes
    for key in request.args:
        response['GET ' + key] = request.args.get(key, '')
    # POST Attributes
    for key in request.form.keys():
        response['POST ' + key] = request.form[key]

    return data_results(response)

@app.route('/')
def app_index():
    """Index identifying the server"""
    response = {"message": "orangeninge-ui api server: Authentication required for use",
                "status": "200"}
    return data_results(response)

@app.route('/v1.0/change_requests/', methods=['POST', 'GET'])
@auth_token_required
def change_requests():

    if request.method == 'POST':
        new_request = ChangeRequest(**request.json)
        db.session.add(new_request)
        db.session.commit()
        return data_results("success")

    elif request.method == 'GET':
        status = request.args.get('status')
        deleted = request.args.get('deleted', False)
        if status:
            # only with a specified state
            result_set = ChangeRequest.query.filter_by(deleted=deleted, status=getattr(
                                                    ChangeRequest.StateOptions, status)).all()
        else:
            # all change requests
            result_set = ChangeRequest.query.filter_by(deleted=deleted).all()
        serialized_list = []
        for obj in result_set:
            serialized_list.append(obj.serialize())
        return data_results(serialized_list)

@app.route('/v1.0/change_requests/<int:id>/', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@auth_token_required
def change_request(id):

    # some weird session thing?
    change_request = ChangeRequest.query.filter(ChangeRequest.id==id).first_or_404()

    if request.method == 'GET':
        return data_results(change_request.serialize())

    elif request.method == 'PUT':
        # not implemented
        abort(501)

    elif request.method == 'PATCH':
        for key in request.json.keys():
            if key != 'created_at' or key != 'modified_at' or key != 'id':
                setattr(change_request, key, request.json[key])
        db.session.commit()
        return data_results('Patched change_request %d' % id)

    elif request.method == 'DELETE':
        change_request.deleted = True
        db.session.commit()
        return data_results('Deleted change_request %d' % id)

@app.route('/v1.0/devices/', methods=['POST', 'GET'])
@auth_token_required
def devices():

    if request.method == 'POST':
        new_device = Device(**request.json)
        db.session.add(new_device)
        db.session.commit()
        return data_results("success")

    elif request.method == 'GET':
        deleted = request.args.get('deleted', False)
        result_set = Device.query.filter_by(deleted=deleted).all()
        serialized_list = []
        for obj in result_set:
            serialized_list.append(obj.serialize())
        return data_results(serialized_list)

@app.route('/v1.0/devices/<int:id>/', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@auth_token_required
def device(id):

    # some weird session thing?
    device = Device.query.filter(Device.id==id).first_or_404()

    if request.method == 'GET':
        return data_results(device.serialize())

    elif request.method == 'PUT':
        # not implemented
        abort(501)

    elif request.method == 'PATCH':
        for key in request.json.keys():
            if key != 'created_at' or key != 'modified_at' or key != 'id':
                setattr(device, key, request.json[key])
        db.session.commit()
        return data_results('Patched device %d' % id)

    elif request.method == 'DELETE':
        device.deleted = True
        db.session.commit()
        return data_results('Deleted device %d' % id)

#added
@app.route('/v1.0/addresses/', methods=['POST', 'GET'])
@auth_token_required
def addresses():

    if request.method == 'POST':
        new_address = Address(**request.json)
        db.session.add(new_address)
        db.session.commit()
        return data_results("success")

    elif request.method == 'GET':
        status = request.args.get('status')
        deleted = request.args.get('deleted', False)
        if status:
            # only with a specified state
            result_set = Address.query.filter_by(deleted=deleted, status=getattr(
                                                    Address.StateOptions, status)).all()
        else:
            # all change requests
            result_set = Address.query.filter_by(deleted=deleted).all()
        serialized_list = []
        for obj in result_set:
            serialized_list.append(obj.serialize())
        return data_results(serialized_list)

@app.route('/v1.0/addresses/<int:id>/', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@auth_token_required
def address(id):

    # some weird session thing?
    address = Address.query.filter(Address.id==id).first_or_404()

    if request.method == 'GET':
        return data_results(address.serialize())

    elif request.method == 'PUT':
        # not implemented
        abort(501)

    elif request.method == 'PATCH':
        for key in request.json.keys():
            if key != 'created_at' or key != 'modified_at' or key != 'id':
                setattr(address, key, request.json[key])
        db.session.commit()
        return data_results('Patched address %d' % id)

    elif request.method == 'DELETE':
        address.deleted = True
        db.session.commit()
        return data_results('Deleted address %d' % id)

@app.route('/v1.0/services/', methods=['POST', 'GET'])
@auth_token_required
def services():

    if request.method == 'POST':
        new_service = Service(**request.json)
        db.session.add(new_service)
        db.session.commit()
        return data_results("success")

    elif request.method == 'GET':
        status = request.args.get('status')
        deleted = request.args.get('deleted', False)
        if status:
            # only with a specified state
            result_set = Service.query.filter_by(deleted=deleted, status=getattr(
                                                    Service.StateOptions, status)).all()
        else:
            # all change requests
            result_set = Service.query.filter_by(deleted=deleted).all()
        serialized_list = []
        for obj in result_set:
            serialized_list.append(obj.serialize())
        return data_results(serialized_list)

@app.route('/v1.0/services/<int:id>/', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@auth_token_required
def service(id):

    # some weird session thing?
    service = Service.query.filter(Service.id==id).first_or_404()

    if request.method == 'GET':
        return data_results(service.serialize())

    elif request.method == 'PUT':
        # not implemented
        abort(501)

    elif request.method == 'PATCH':
        for key in request.json.keys():
            if key != 'created_at' or key != 'modified_at' or key != 'id':
                setattr(service, key, request.json[key])
        db.session.commit()
        return data_results('Patched service %d' % id)

    elif request.method == 'DELETE':
        service.deleted = True
        db.session.commit()
        return data_results('Deleted service %d' % id)
#end added
