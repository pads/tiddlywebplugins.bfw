.PHONY: server terminate dist test qtest clean

server: terminate
	./reloader ./ '^.*\.py$$' twanager server & \
			echo $$! > .server.pid
	sleep 0.5
	touch tiddlywebplugins/__init__.py

terminate:
	ps -o pgid -p `cat .server.pid` | tail -n1 | while read pgid; do \
			kill -TERM -$$pgid || true; done
	rm .server.pid || true

dist: test
	python setup.py sdist

test: clean qtest

qtest:
	py.test -s --tb=short test

clean:
	find . -name "*.pyc" | xargs rm || true
	rm -r dist || true
	rm -r tiddlywebplugins.bfw.egg-info || true
