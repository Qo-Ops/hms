 create table users(
    id serial PRIMARY KEY,
    login varchar(50) UNIQUE NOT NULL,
    password char(66) NOT NULL,
    access_level INTEGER NOT NULL,
    email varchar(124) UNIQUE NOT NULL
);

create table employees(
    id INTEGER PRIMARY KEY references users(id) NOT NULL,
    first_name varchar(100) NOT NULL,
    last_name varchar(100) NOT NULL,
    salary INTEGER NOT NULL,
    position varchar(100) NOT NULL
);

create table visitors(
    id serial PRIMARY KEY,
    first_name varchar(100) NOT NULL,
    last_name varchar(100) NOT NULL,
    ssn varchar(50) NOT NULL,
    country_code char(3) NOT NULL,
    email varchar(124) NOT NULL
);

create table hotel_chains(
    chain_name varchar(100) PRIMARY KEY,
    owner_id integer NOT NULL references users(id) ON DELETE CASCADE ON UPDATE CASCADE
);

create table locations(
    chain_name varchar(100) references hotel_chains(chain_name) ON DELETE CASCADE ON UPDATE CASCADE,
    city varchar(60) NOT NULL,
    location varchar(100) NOT NULL,
    photo_path varchar(200),
    admin_id integer references users(id) ON DELETE SET NULL ON UPDATE CASCADE,
    address varchar(200),
    PRIMARY KEY(chain_name, location)
);

CREATE DOMAIN room_status AS varchar(8)
    CHECK(VALUE IN ('occupied', 'clean', 'dirty'));

create table room_types(
    id SERIAL PRIMARY KEY,
    chain_name varchar(100) NOT NULL,
    location varchar(100) NOT NULL,
    name varchar(100) NOT NULL,
    price integer CHECK(price > 0) NOT NULL,
    capacity integer CHECK(capacity > 0) NOT NULL,
    FOREIGN KEY (location, chain_name) REFERENCES locations(location, chain_name) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE (chain_name, location, name)
);

create table rooms(
    id serial PRIMARY KEY,
    room_type INTEGER REFERENCES room_types(id) ON DELETE CASCADE ON UPDATE CASCADE,
    roomNo integer NOT NULL CHECK(roomNo > 0),
    status room_status NOT NULL
);

create table reservations(
    id serial PRIMARY KEY,
    total integer CHECK(total > 0),
    check_in date NOT NULL,
    check_out date NOT NULL,
    room_id integer NOT NULL REFERENCES rooms(id),
    visitor_id integer NOT NULL REFERENCES visitors(id),
	CONSTRAINT positive_duration CHECK (check_out > check_in)
);

CREATE DOMAIN day_of_week AS char(3)
    CHECK(VALUE IN ('MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'));

create table cleaning(
    id serial PRIMARY KEY REFERENCES rooms(id) ON DELETE CASCADE ON UPDATE CASCADE,
    cleaner integer references employees(staff_id) ON DELETE CASCADE ON UPDATE CASCADE,
    weekday day_of_week NOT NULL
);



CREATE VIEW rooms_view AS
SELECT rooms.*, chain_name, location, name as room_type_name, price, capacity 
FROM rooms 
    JOIN room_types ON room_types.id=room_type;

CREATE VIEW full_reservations AS
SELECT reservations.*, rooms.roomNo, status, room_types.id as room_type, chain_name, location, name as room_type_name, price, capacity, visitors.email, visitors.ssn, visitors.country_code, visitors.last_name, visitors.first_name
FROM reservations
    JOIN rooms ON room_id=rooms.id
    JOIN room_types ON rooms.room_type=room_types.id
    JOIN visitors ON visitor_id=visitors.id;

CREATE FUNCTION trigger_occupied_dirty ()
        RETURNS trigger AS $$
        BEGIN
           if ( NEW.status = 'clean' AND OLD.status = 'occupied' )
           then
           NEW.status = 'dirty';
           end if;
        return NEW;
        END;
        $$
    LANGUAGE  plpgsql;

CREATE TRIGGER cleaners
    BEFORE UPDATE OR INSERT ON cleaning
    EXECUTE PROCEDURE ensure_cleaner ();

CREATE FUNCTION ensure_cleaner ()
        RETURNS trigger AS $$
        BEGIN
           if (SELECT position FROM employees WHERE id=NEW.cleaner <> 'cleaner')
           then RAISE EXCEPTION "the employee is not a cleaner" 
        return NEW;
        END;
        $$
    LANGUAGE  plpgsql;

CREATE TRIGGER check_out
    BEFORE UPDATE ON rooms
    EXECUTE PROCEDURE trigger_occupied_dirty ();