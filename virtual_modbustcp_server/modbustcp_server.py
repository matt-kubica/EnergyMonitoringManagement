import argparse
import time
import random

from pyModbusTCP.server import ModbusServer, DataBank
from apscheduler.schedulers.background import BackgroundScheduler


def set_databank_words():
	words = []
	words.append(random.randrange(0, 10000))
	words.append(random.randrange(220, 240))
	words.append(random.randrange(0, 800))
	print(words)

	DataBank.set_words(0, [words[0]])   # power
	DataBank.set_words(1, [words[1]])	# ac voltage
	DataBank.set_words(2, [words[2]])	# dc voltage


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", type=str, default="0.0.0.0", help="host")
    parser.add_argument("-p", "--port", type=int, default=502, help="port")
    args = parser.parse_args()

    modbus_server = ModbusServer(host=args.host, port=args.port, no_block=True)
    modbus_server.start()

    scheduler = BackgroundScheduler()
    scheduler.add_job(set_databank_words, trigger="cron", second="*/20")
    scheduler.start()

    print('server started on {0}:{1}!'.format(args.host, args.port))

    while True:
    	time.sleep(1)