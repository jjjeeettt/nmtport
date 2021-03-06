from datetime import datetime, timedelta
from flask import render_template, flash
from app.model import Post, Mechanism
from app import db
from pprint import pprint
HOURS = 10


def today_shift_date():
    '''get date and shift'''
    hour = datetime.now().hour
    if hour >= 8 and hour < 20:
        date_shift = datetime.now()
        shift = 1
    elif hour < 8:
        date_shift = datetime.now() - timedelta(days=1)
        shift = 2
    else:
        date_shift = datetime.now()
        shift = 2
    return date_shift.date(), shift


def all_mechanisms_id(type=None):
    '''Find all mechanisms id'''
    if type == None:
        return [m.id for m in db.session.query(Mechanism).all()]
    return [m.id for m in db.session.query(Mechanism).filter(Mechanism.type == type).all()]

def all_mechanisms_type():
    '''Find all mechanisms type'''
    ls = [m.type for m in db.session.query(Mechanism).all()]
    return set(ls)

def all_number(type, number):
    '''Need to do then'''
    return [m.id for m in Mechanism.query.all()]

def multiple_5(date): #not use
    '''Return time multiple 5 minutes and remite microseconds'''
    global HOURS
    # date -= timedelta(minutes=5)
    date += timedelta(hours=HOURS)
    mul5 = date.minute - date.minute % 5
    date_n = date.replace(minute=mul5, second=0, microsecond=0)
    return date_n



def time_for_shift_kran(date_shift, shift):
    '''get dict with all minute's values for the period, name and total'''
    # get data from db
    shift = int(shift)
    all_mechs = all_mechanisms_id('kran')
    cursor = db.session.query(Post).filter(Post.date_shift == date_shift, Post.shift ==
                                           shift, Post.mechanism_id.in_(all_mechs)).order_by(Post.mechanism_id).all()
    # create dict all works mechanism in shift
    data_per_shift = {}
    for el in cursor:
        date_t = el.timestamp.replace(second=0, microsecond=0)
        date_t += timedelta(hours=10)
        if data_per_shift.get(el.mech.number):
            data_per_shift[el.mech.number]['data'][date_t] = [el.value, el.value3]
            if el.value==1:
                data_per_shift[el.mech.number]['total_90'] += 1
            if el.value==2:
                data_per_shift[el.mech.number]['total_180'] += 1
            pre_value=el.value3
        else:
            data_per_shift[el.mech.number] = {}
            data_per_shift[el.mech.number]['mechanism'] = el.mech
            data_per_shift[el.mech.number]['total_90'] = 0
            data_per_shift[el.mech.number]['total_180'] = 0
            if el.value==1:
                data_per_shift[el.mech.number]['total_90'] = 1
            if el.value==2:
                data_per_shift[el.mech.number]['total_180'] = 1
            data_per_shift[el.mech.number]['data'] = {}
            data_per_shift[el.mech.number]['data'][date_t] = [el.value, el.value3]
            pre_value=el.value3

    # get start time for this shift
    start = datetime.combine(date_shift, datetime.min.time())
    if shift == 1:
        start = start.replace(hour=8, minute=0, second=0, microsecond=0)
    else:
        start = start.replace(hour=20, minute=0, second=0, microsecond=0)

    if data_per_shift == {}:
        return None
    # create dict with all minutes to now if value is not return (-1) because 0 may exist
    time_by_minuts = {}
    for key, value in data_per_shift.items():
        flag_start=True
        flag_finish = True
        pre_value3 = 0
        flag_work = True
        count_work = 0
        time_by_minuts[key] = {}
        time_by_minuts[key]['name'] = data_per_shift[key]['mechanism'].name
        # translate hours into minutes and round
        time_by_minuts[key]['total_180'] = round(data_per_shift[key]['total_180'], 2)
        time_by_minuts[key]['total_90'] = round(data_per_shift[key]['total_90'], 2)
        time_by_minuts[key]['data'] = {}
        delta_minutes = start
        for i in range(1, 60 * 12 + 1):
            date_t = delta_minutes.strftime("%H:%M")
            try:
                val_minute = data_per_shift[key]['data'][delta_minutes][0]
                pre_value =  data_per_shift[key]['data'][delta_minutes][1]
            except KeyError:
                val_minute = -1


            time_by_minuts[key]['data'][i] = {'time': date_t, 'value': val_minute}
            delta_minutes += timedelta(minutes=1)
            today_date, today_shift = today_shift_date()
            if val_minute>0 and flag_start:
                time_by_minuts[key]['start'] = date_t
                flag_start =False
            if val_minute > 0:
                time_by_minuts[key]['finish'] = date_t
            if delta_minutes >= datetime.now() and date_shift == today_date and today_shift == shift:
                break



    return time_by_minuts






def time_for_shift_usm(date_shift, shift):
    '''get dict with all minute's values for the period, name and total'''
    # get data from db
    shift = int(shift)
    all_mechs = all_mechanisms_id('usm')
    cursor = db.session.query(Post).filter(Post.date_shift == date_shift, Post.shift ==
                                           shift, Post.mechanism_id.in_(all_mechs)).order_by(Post.mechanism_id).all()
    # create dict all works mechanism in shift
    data_per_shift = {}
    for el in cursor:
        date_t = el.timestamp.replace(second=0, microsecond=0)
        date_t += timedelta(hours=10)
        # date_t = date_t.strftime("%H:%M")
        el.value = -1 if el.value==None else el.value
        val_minute = 0 if el.value < 0.1 else el.value

        if data_per_shift.get(el.mech.number):
            data_per_shift[el.mech.number]['data'][date_t] = val_minute
            data_per_shift[el.mech.number]['total'] += el.value
        else:
            data_per_shift[el.mech.number] = {}
            data_per_shift[el.mech.number]['mechanism'] = el.mech
            data_per_shift[el.mech.number]['total'] = el.value
            data_per_shift[el.mech.number]['data'] = {}
            data_per_shift[el.mech.number]['data'][date_t] = val_minute

    # get start time for this shift
    start = datetime.combine(date_shift, datetime.min.time())
    if shift == 1:
        start = start.replace(hour=8, minute=0, second=0, microsecond=0)
    else:
        start = start.replace(hour=20, minute=0, second=0, microsecond=0)

    if data_per_shift == {}:
        return None
    # create dict with all minutes to now if value is not return (-1) because
    # 0 may exist
    time_by_minuts = {}
    for key, value in data_per_shift.items():
        flag_start=True
        flag_finish = True
        time_by_minuts[key] = {}
        time_by_minuts[key]['name'] = data_per_shift[key]['mechanism'].name
        # translate hours into minutes and round
        time_by_minuts[key]['total'] = round(
            data_per_shift[key]['total'] / 60, 2)
        time_by_minuts[key]['data'] = {}
        delta_minutes = start
        for i in range(1, 60 * 12 + 1):
            date_t = delta_minutes.strftime("%H:%M")
            val_minute = data_per_shift[key]['data'].setdefault(delta_minutes, -1)
            time_by_minuts[key]['data'][i] = {'time': date_t, 'value': val_minute}
            delta_minutes += timedelta(minutes=1)
            today_date, today_shift = today_shift_date()
            if val_minute>0 and flag_start:
                time_by_minuts[key]['start'] = date_t
                flag_start =False
            if val_minute > 0:
                time_by_minuts[key]['finish'] = date_t
            if delta_minutes >= datetime.now() and date_shift == today_date and today_shift == shift:
                break
    return time_by_minuts



def image_mechanism(value, type_mechanism, number, last_time):
    dt = datetime.now()- last_time
    dt =dt.total_seconds()/60
    if type_mechanism=="usm":
        if dt > 120.0:
            return './static/numbers/'+str(type_mechanism)+'/gray/'+str(number)+'.png'
        if dt >= 3.0:
            return './static/numbers/'+str(type_mechanism)+'/red/'+str(number)+'.png'
        if value<0.1:
            return './static/numbers/'+str(type_mechanism)+'/yellow/'+str(number)+'.png'
        else:
            return './static/numbers/'+str(type_mechanism)+'/green/'+str(number)+'.png'

    if type_mechanism=="kran":
        if dt > 120.0:
            return './static/numbers/'+str(type_mechanism)+'/gray/'+str(number)+'.png'
        if dt >= 5.0:
            return './static/numbers/'+str(type_mechanism)+'/red/'+str(number)+'.png'
        if value==1:
            return './static/numbers/'+str(type_mechanism)+'/black/'+str(number)+'.png'
        if value==2:
            return './static/numbers/'+str(type_mechanism)+'/blue/'+str(number)+'.png'
        else:
            return './static/numbers/'+str(type_mechanism)+'/yellow/'+str(number)+'.png'



# not use
def time_for_shift_list(date_shift, shift): #not use
    '''get dict with all minute's values for the period'''
    # get data from db
    cursor = db.session.query(Post).filter(
        Post.date_shift == date_shift, Post.shift == shift).order_by(Post.mechanism_id).all()

    # create dict all works mechanism in shift
    data_per_shift = {}
    for el in cursor:
        if data_per_shift.get(el.mech.name):
            data_per_shift[el.mech.name].append(el)
        else:
            data_per_shift[el.mech.name] = [el]

    # get start time for this shift
    start = datetime.combine(date_shift, datetime.min.time())
    if shift == 1:
        start = start.replace(hour=8, minute=0, second=0, microsecond=0)
    else:
        start = start.replace(hour=20, minute=0, second=0, microsecond=0)

    # create dict existing values by time
    existing_values = {}
    for key, values in data_per_shift.items():
        existing_values[key] = {}
        for val in values:
            date_t = val.timestamp.replace(second=0, microsecond=0)
            date_t += timedelta(hours=HOURS)
            existing_values[key][date_t] = val.value

    # create dict with all minutes to now if value is not return (-1) because
    # 0 may exist
    time_by_minuts = {}
    for key_m, values_m in existing_values.items():
        start_m = start
        time_by_minuts[key_m] = []
        for i in range(60 * 12 - 1):
            val_minutes = existing_values[key_m].setdefault(start_m, -1)
            if (val_minutes < 0.1 and val_minutes > 0):
                val_minutes = 0
            time_by_minuts[key_m].append(val_minutes)
            start_m += timedelta(minutes=1)
            if start_m >= datetime.now():
                break
    return time_by_minuts

def handle_date(date):
    day = month = year = None
    spl_date = date.split('.')
    if len(spl_date) >3:
        return redirect(url_for('index'))
    try:
        day = int(spl_date[0])
        month = int(spl_date[1])
        year = int(spl_date[2])
    except IndexError:
        print('ERR', day, month, year)
    if not year: year=datetime.now().year
    if not month: month=datetime.now().month
    if not day: day=datetime.now().day
    try:
        return datetime(year, month, day).date()
    except:
        flash('Enter correct shift')
        return datetime.now().date()

def add_post(post):
    # new_post = Post(value, latitude, longitude, mechanism_id)
    print(post)
    # print(post.value, post.latitude)
    # db.session.add(new_post)
    # db.session.commit()


# date_shift, shift = today_shift_date()
# print(date_shift, shift)
# dd = time_for_shift('usm', date_shift, shift)
# pprint(dd)




