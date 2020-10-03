CREATE TABLE energy_meters(
	id int PRIMARY KEY,
	host varchar(64) NOT NULL,
	port int NOT NULL,
	slave_address int NOT NULL,
	type varchar(32) NOT NULL,
	description varchar(64) NOT NULL
);

CREATE TABLE registers(
	type varchar(32) NOT NULL,
	register_address int NOT NULL,
	measurement_name varchar(64) NOT NULL,
	data_unit varchar(8),
	data_type int CHECK (data_type >= 1 AND data_type <= 3),
	function_code int CHECK (function_code >= 3 AND function_code <= 4),
	word_order int CHECK (word_order >= 1 AND word_order <= 2),
	byte_order int CHECK (byte_order >= 1 AND byte_order <= 2)
);




INSERT INTO registers VALUES(
	'virtual_modbustcp_server',
	0,
	'test_measurement',
	't-unit',
	3,
	4,
	2,
	2
);


INSERT INTO energy_meters VALUES(
	0,
	'virtual_modbustcp_server',
	502,
	0,
	'virtual_modbustcp_server',
	'test_energy_meter'
);




