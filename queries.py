search_query = """
SELECT room_types.price, room_types.name, room_types.capacity, room_types.location, room_types.id, locations.photo_path, locations.chain_name
FROM room_types
    JOIN rooms ON rooms.room_type = room_types.id
    NATURAL JOIN locations
    WHERE price < %(max_price)s AND city = %(city)s AND rooms.id NOT IN
    (SELECT id 
     FROM reservations
     WHERE (check_in <= %(check_in)s AND check_out >= %(check_in)s) OR 
           (check_out >= %(check_out)s AND check_in <= %(check_out)s));"""

current_reservations_query = """
SELECT roomNo, check_in, check_out, first_name, last_name, ssn, country_code
FROM rooms
    JOIN reservations ON rooms.id=reservations.room_id
    JOIN visitors ON visitors.id=reservations.visitor_id
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
SELECT locations.chain_name, locations.city, locations.location, locations.photo_path, room_types.name, room_types.capacity, room_types.price
FROM room_types
NATURAL JOIN locations
WHERE room_types.id IN
                        (SELECT id
                         FROM rooms 
                         WHERE room_type=%s);"""

count_rooms_query = """
SELECT COUNT(*) FROM rooms_view WHERE chain_name=%(chain_name)s AND location=%(location)s;
"""
count_occupied_rooms = """
SELECT COUNT(*) FROM rooms_view WHERE status='occupied' AND chain_name=%(chain_name)s AND location=%(location)s;
"""
total_income = """
SELECT SUM((check_out - check_in)*price) FROM full_reservations WHERE chain_name=%(chain_name)s AND location=%(location)s;
"""
