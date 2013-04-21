# Misc. development related batch jobs

NIRCD:=/opt/local/sbin/ngircd -n -f caipirinha/ngircd.conf

MONGO=mongod --dbpath data

DEVELOPMENT_BOT=venv/bin/caipirinha-bot development.ini

start-development-bot:
	$(MONGO) &
	$(NIRCD) &
	$(DEVELOPMENT_BOT)

stop-development-bot:
	killall ngircd
	killall mongod
	pkill -f caipirinha-bot

irssi:
	irssi --connect=127.0.0.1 --nick=buddy --home=`pwd`/scripts/irssi

