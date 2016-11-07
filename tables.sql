create table users(
    id serial PRIMARY KEY,
    login varchar(50) UNIQUE,
    password char(66),
    access_level integer,
    email varchar(124) UNIQUE
);

create table visitors(
    id serial PRIMARY KEY,
    first_name varchar(100) NOT NULL,
    last_name varchar(100) NOT NULL,
    ssn varchar(50),
    country_code char(3)
);

create table hotel_chains(
    hotel_id serial PRIMARY KEY,
    chain_name varchar(100) UNIQUE,
    owner_id integer references users(id)
);

create table locations(
    admin_id integer references users(id),
    hotel_id integer references hotel_chains(hotel_id),
    location varchar(100),
    city varchar(60),
    PRIMARY KEY(hotel_id, location)
);

CREATE DOMAIN room_status AS varchar(8)
    CHECK(VALUE IN ('occupied', 'clean', 'dirty'));

create table room_type(
    hotel_id integer,
    location varchar(100),
    type varchar(100),
    price integer CHECK(price > 0) NOT NULL,
    capacity integer CHECK(capacity > 0) NOT NULL,
    FOREIGN KEY (location, hotel_id) REFERENCES locations(location, hotel_id),
    PRIMARY KEY (type, location, hotel_id)
);

create table rooms(
    building integer,
    roomNo integer,
    hotel_id integer,
    location varchar(100),
    status room_status,
    type varchar(100),
    FOREIGN KEY (type, location, hotel_id) REFERENCES room_type(type, location, hotel_id) ON DELETE CASCADE,
    PRIMARY KEY(roomNo, building, location, hotel_id)
);

create table accomodations(
    id serial PRIMARY KEY,
    check_in date NOT NULL,
    check_out date NOT NULL,
    hotel_id integer,
    location varchar(100),
    building integer,
    roomNo integer,
    visitor_id integer,
    FOREIGN KEY (building, location, roomNo, hotel_id) REFERENCES rooms(building, location, roomNo, hotel_id),
    FOREIGN KEY (visitor_id) REFERENCES visitors(id),
    CONSTRAINT positive_duration
    CHECK (check_out > check_in)
);

create table payments(
    id serial PRIMARY KEY,
    total integer CHECK(total > 0),
    hotel_id integer,
    location varchar(100),
    building integer,
    roomNo integer,
    visitor_id integer,
    FOREIGN KEY (building, location, roomNo, hotel_id) REFERENCES rooms(building, location, roomNo, hotel_id),
    FOREIGN KEY (visitor_id) REFERENCES visitors(id)
);

create table cleaners(
    staff_id serial PRIMARY KEY,
    first_name varchar(100),
    last_name varchar(100),
    salary integer CHECK(salary > 0) NOT NULL,
    floor integer NOT NULL,
    building integer
);

CREATE DOMAIN day_of_week AS char(3)
    CHECK(VALUE IN ('MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'));

create table cleaning(
    id serial PRIMARY KEY,
    building integer,
    roomNo integer,
    location varchar(100),
    hotel_id integer,
    cleaner integer references cleaners(staff_id),
    weekday day_of_week,
    FOREIGN KEY (roomNo, hotel_id, location, building) REFERENCES rooms(roomNo, hotel_id, location, building) ON DELETE CASCADE
);