search_query = """
SELECT rooms_view.price, rooms_view.room_type_name, rooms_view.capacity, rooms_view.location, rooms_view.id, rooms_view.room_type, locations.photo_path, locations.chain_name
FROM rooms_view
    NATURAL JOIN locations
    WHERE price < %(max_price)s AND 
    city = %(city)s AND 
    capacity >=%(capacity)s AND
    id IN
    (SELECT MIN(id)
     FROM rooms WHERE id NOT IN
                                (SELECT id 
                                 FROM reservations
                                 WHERE (check_in <= %(check_in)s AND check_out >= %(check_in)s) OR 
                                       (check_out >= %(check_out)s AND check_in <= %(check_out)s))
     GROUP BY room_type);"""

current_reservations_query = """
SELECT roomNo, check_in, check_out, first_name, last_name, ssn, country_code
FROM full_reservations
WHERE status='occupied';"""

check_in_query = """
UPDATE rooms 
SET status = 'occupied' 
WHERE id IN
	(SELECT room_id
	FROM reservations
	WHERE check_in = now()::date AND visitor_id IN
		(SELECT id 
		FROM visitors
		WHERE ssn = %(ssn)s AND country = %(country_code)s
		)
	);"""

get_reservation_query = """
SELECT locations.*, room_types.name, room_types.capacity, room_types.price
FROM room_types
NATURAL JOIN locations
WHERE room_types.id=%s;"""

count_rooms_query = """
SELECT COUNT(*) FROM rooms_view WHERE chain_name=%(chain_name)s AND location=%(location)s;
"""
count_occupied_rooms = """
SELECT COUNT(*) FROM rooms_view WHERE status='occupied' AND chain_name=%(chain_name)s AND location=%(location)s;
"""
total_income = """
SELECT SUM((check_out - check_in)*price) FROM full_reservations WHERE chain_name=%(chain_name)s AND location=%(location)s;
"""
