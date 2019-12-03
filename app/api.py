# -*- coding: utf-8 -*-
from flask import request, json, jsonify, abort, make_response
from flask import render_template, flash, redirect
from app import db, app
from app.model import Mechanism, Post
from app.form import AddMechanism
from datetime import datetime, timedelta
from functions import today_shift_date, all_mechanisms_id, time_for_shift, time_for_shift_list
from sqlalchemy import func
from pprint import pprint


@app.route("/api/v1.0/get_per_shift/<int:m_id>", methods=["GET"])
def get_per_shift(m_id):
    '''get data for this shift by id mechanism'''
    date_shift, shift = today_shift_date()
    data_per_shift = db.session.query(Post).filter( Post.date_shift == date_shift, Post.shift == shift, Post.mechanism_id == m_id).all()
    try:
        start = db.session.query(Post.timestamp).filter( Post.date_shift == date_shift, Post.shift == shift, Post.mechanism_id == m_id).first()[0]
        stop = db.session.query(Post.timestamp).filter(Post.date_shift == date_shift, Post.shift == shift, Post.mechanism_id == m_id).order_by(Post.timestamp.desc()).first()[0]
    except TypeError:
        abort(405)
    start += timedelta(hours=10)
    stop += timedelta(hours=10)
    total = round(sum(el.value for el in data_per_shift)/60, 3)
    data = {'total': total, 'start': start, 'stop': stop}
    return jsonify(data)


@app.route("/api/v1.0/get_data/<type_mechanism>/<date_shift>/<int:shift>", methods=['GET', 'POST'])
def get_data(type_mechanism, date_shift, shift):
    '''get data shift for by type of mechanism'''
    try:
        date = datetime.strptime(date_shift, '%Y-%m-%d').date()
    except ValueError:
        return make_response(jsonify({'error': 'Bad format date'}), 400)

    data = time_for_shift(type_mechanism, date, shift)
    return jsonify(data)


@app.route("/api/v1.0/get_mech/<int:m_id>", methods=["GET"])
def get_mech(m_id):
    '''get name mechanism'''
    mech = Mechanism.query.get(m_id)
    print(mech)
    return f'{mech.name}'

@app.route('/api/v1.0/add_post', methods=['POST'])
def add_post():
    '''add post from arduino'''
    need_keys = 'password', 'value', 'latitude', 'longitude', 'mechanism_id'
    request_j = request.json
    # print(request_j)
    if not request_j:
        abort(400)
    keys = [p for p in request_j.keys()]
    if not set(keys).issubset(need_keys):
        abort(400)
    if request_j['password'] != 'super':
        abort(403)  # need use this password in Arduino
    if request_j['mechanism_id'] not in all_mechanisms_id():
        abort(405)
    value = request_j['value']
    latitude = request_j['latitude']
    longitude = request_j['longitude']
    mechanism_id = request_j['mechanism_id']
    if float(latitude)==0 or float(longitude)==0:
        mech = Mechanism.query.get(mechanism_id)
        data_mech = db.session.query(Post).filter(Post.mechanism_id == mechanism_id).first()
        latitude =data_mech.latitude
        longitude = data_mech.longitude
        print(latitude, longitude)
    new_post = Post(value, latitude, longitude, mechanism_id)
    data = request.data
    db.session.add(new_post)
    db.session.commit()
    # import sys
    # print('******', sys.getsizeof(request_j))
    return data, 201


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404
    # return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(403)
def not_found(error):
    return make_response(jsonify({'error': 'Wrong password'}), 403)


@app.route('/api/v1.0/add_mechanism', methods=['POST'])
def add_mechanism():
    all_mech_id = [mech.id for mech in Mechanism.query.all()]
    request_f = request.form
    id = request_f['id']
    company = request_f['company']
    type = request_f['type']
    model = request_f['model']
    number = request_f['number']
    name = request_f['name']
    new_mech = Mechanism(id, company, type, model, number, name)
    data = request.data
    db.session.add(new_mech)
    db.session.commit()
    return redirect("http://localhost:5000/show_all_mechanisms", code=301)
    # return data

# may be not use
@app.route('/api/v1.0/add_mech_json', methods=['POST'])
def add_mechanism_json():
    id = request.json['id']
    company = request.json['company']
    type = request.json['type']
    model = request.json['model']
    number = request.json['number']
    name = request.json['name']
    new_mech = Mechanism(id, company, type, model, number, name)
    data = request.data
    db.session.add(new_mech)
    db.session.commit()
    return data