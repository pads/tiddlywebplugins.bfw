.PHONY: server instance terminate dist test qtest remotes lint coverage clean

server: terminate
	./reloader ./ '^.*\.py$$' twanager server & \
			echo $$! > .server.pid
	sleep 0.5
	touch tiddlywebplugins/__init__.py

instance: remotes
	./bfwinstance dev_instance
	mv dev_instance/* ./
	rm -rf dev_instance

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
	twibuilder tiddlywebplugins.bfw
	./assetr

lint:
	find . -name "*.py" -not -path "./venv/*" | while read filepath; do \
		pep8 --ignore=E128,E261 $$filepath; \
	done

coverage: clean remotes
	coverage run --omit="venv/*" `which py.test` test
	coverage html
	# reports
	coverage report
	@echo "[INFO] additional reports in \`htmlcov/index.html\`"


clean:
	find . -name "*.pyc" -print0 | xargs -0 rm || true
	rm -r dist || true
	rm -r tiddlywebplugins.bfw.egg-info || true
	rm -r tiddlywebplugins/bfw/resources || true
	rm -r .coverage htmlcov/ || true
	# remove remote assets
	git rm -r tiddlywebplugins/bfw/assets # fails if there are modifications
	rm -r tiddlywebplugins/bfw/assets || true
	git checkout HEAD tiddlywebplugins/bfw/assets
