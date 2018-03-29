RPMBUILD = rpmbuild --define "_topdir %(pwd)/build" \
        --define "_builddir %{_topdir}" \
        --define "_rpmdir %{_topdir}" \
        --define "_srcrpmdir %{_topdir}" \
        --define "_sourcedir %(pwd)"

GIT_VERSION = $(shell git name-rev --name-only --tags --no-undefined HEAD 2>/dev/null || echo git-`git rev-parse --short HEAD`)
SERVER_VERSION=$(shell awk '/Version:/ { print $$2; }' onemetre-camera-server.spec)

all:
	mkdir -p build
	cp camd camd.bak
	awk '{sub("SOFTWARE_VERSION = .*$$","SOFTWARE_VERSION = \"$(SERVER_VERSION) ($(GIT_VERSION))\""); print $0}' camd.bak > camd
	${RPMBUILD} -ba rasa-camera-server.spec
	${RPMBUILD} -ba rasa-camera-client.spec
	${RPMBUILD} -ba python34-warwick-rasa-camera.spec
	mv build/noarch/*.rpm .
	rm -rf build
	mv camd.bak camd

