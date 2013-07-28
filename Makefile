.PHONY: server terminate dist test qtest remotes clean

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

test: clean remotes qtest

qtest:
	py.test -s --tb=short test

remotes:
	./assetr

clean:
	find . -name "*.pyc" -print0 | xargs -0 rm || true
	rm -r dist || true
	rm -r tiddlywebplugins.bfw.egg-info || true
	# remove remote assets
	git rm -r tiddlywebplugins/bfw/assets # fails if there are modifications
	rm -r tiddlywebplugins/bfw/assets || true
	git checkout HEAD tiddlywebplugins/bfw/assets
