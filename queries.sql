INSERT INTO hotel_chains VALUES(DEFAULT, чейннейм, овнерид)
INSERT INTO locations VALUES(переменные..........)
SELECT room_type.price, room_type.capacity, room_type.location
FROM rooms 
    JOIN room_types ON room_types.name = rooms.type_name
                       room_types.location = rooms.location
                       room_types.hotel_id = rooms.hotel_id
    WHERE price < %s AND city = %s AND rooms.id NOT IN 
    (SELECT id 
     FROM accomodations
     WHERE (check_in <= %checkin AND check_out >= %checkin) OR 
           (check_out >= %checkout AND check_in <= %checkout))