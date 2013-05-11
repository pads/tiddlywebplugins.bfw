.PHONY: server terminate test clean

server: terminate
	./reloader ./ '^.*\.py$$' twanager server & \
			echo $$! > .server.pid
	sleep 0.5
	touch tiddlywebplugins/__init__.py

terminate:
	ps -o pgid -p `cat .server.pid` | tail -n1 | while read pgid; do \
			kill -TERM -$$pgid || true; done
	rm .server.pid

test: clean
	py.test -s --tb=short test

clean:
	find . -name "*.pyc" | xargs rm || true
